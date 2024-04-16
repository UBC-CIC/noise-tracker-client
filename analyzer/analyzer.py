import json
import os
import time
import threading
import datetime
import soundfile as sf
import numpy as np
import scipy
import matplotlib.pyplot as plt
import pandas as pd

import constants
import util
from analyzer.data_file import DataFile
from logger import logger


class Analyzer(threading.Thread):
    def __init__(self, config):
        super().__init__()
        self.__stop_event = threading.Event()
        if not os.path.exists(constants.RESULTS_TMP_PATH):
            os.makedirs(constants.RESULTS_TMP_PATH)
        if not os.path.exists(constants.PROCESSED_FILES_PATH):
            with open(constants.PROCESSED_FILES_PATH, "w") as f:
                f.write("")
        processed_files: set[str] = set()
        with open(constants.PROCESSED_FILES_PATH, "r") as f:
            for line in f:
                processed_files.add(line.strip())
        self.processed_files = processed_files
        self.config = config

    def stop(self):
        self.__stop_event.set()

    def stopped(self):
        return self.__stop_event.is_set()

    def run(self):
        while True and not self.stopped():
            for hydrophone in self.config["hydrophones"]:
                current_files = util.find_files(
                    hydrophone["directory_to_watch"],
                    hydrophone["file_structure_pattern"],
                )
                new_files = current_files - self.processed_files
                for file in new_files:
                    logger.info(f"Detected new file: {file}")
                    data_file = DataFile(
                        f"{hydrophone['directory_to_watch']}/{file}", hydrophone
                    )
                    if "spectrogram" in hydrophone["metrics"]:
                        logger.info("Generating spectrogram")
                        self.spectrogram(data_file, hydrophone)
                    if "spl" in hydrophone["metrics"]:
                        logger.info("Calculating SPL")
                        self.spl(data_file)
                    with open(constants.PROCESSED_FILES_PATH, "a") as f:
                        f.write(file + "\n")
                    self.processed_files.add(file)
                    logger.info(f"Processing finished for file: {file}")
                time.sleep(self.config["scan_interval"])

    def spl(self, data_file: DataFile):
        x, sample_rate = sf.read(data_file.file_path)
        # break x to 60 second chunks
        chunk_size = 60 * sample_rate
        chunks = [x[i : i + chunk_size] for i in range(0, len(x), chunk_size)]
        spls = {}
        for i, chunk in enumerate(chunks):
            timestamp = data_file.timestamp + datetime.timedelta(seconds=i * 60)
            if len(chunk) == 60 * sample_rate:
                spls[timestamp] = self.chunk_spl(chunk, sample_rate)
        for timestamp, spl_tuple in spls.items():
            spl, bioband_spl = spl_tuple
            spl_result_path = f"{constants.RESULTS_TMP_PATH}/{data_file.hydrophone['id']}_{timestamp.strftime('%Y-%m-%d-%H-%M-%S')}_spl.json"
            bioband_spl_result_path = f"{constants.RESULTS_TMP_PATH}/{data_file.hydrophone['id']}_{timestamp.strftime('%Y-%m-%d-%H-%M-%S')}_biospl.json"
            json.dump(
                spl.to_dict(orient="records"), open(spl_result_path, "w"), indent=2
            )
            json.dump(
                bioband_spl.to_dict(orient="records"),
                open(bioband_spl_result_path, "w"),
                indent=2,
            )

    def chunk_spl(self, audioIn: np.array, fs: int):
        if len(audioIn) != 60.0 * fs:
            raise ValueError("Audio chunk is not 60 seconds long")
        if audioIn.ndim != 1:
            pass
        # computes spectrogram 1 Hz resolution (linear units)
        # -----------
        df = 0.1  # the minimum df for a 60s file is 0.1/6 = 0.166
        NFFT = int(fs / float(df))
        # -----------
        # --- FFT WINDOW
        noverlap_par = int(NFFT * 0.5)
        window_par = scipy.signal.get_window("hann", Nx=NFFT, fftbins=True)
        # ---
        f_vals, t_vals, psdArr = scipy.signal.spectrogram(
            audioIn,
            fs=fs,
            nperseg=NFFT,
            nfft=NFFT,
            window=window_par,
            noverlap=noverlap_par,
            return_onesided=True,
            scaling="density",
            mode="psd",
        )
        #
        psd = np.mean(psdArr, axis=1)
        # RMS
        psdRMS = psd / (np.sqrt(2))
        # apply calibration
        pass
        # if callable(cal_func):
        # 	for i in range(len(psdRMS)):
        # 		psdRMS[i] = psdRMS[i] / ( 10**(cal_func(f_vals[i])/10.0) )

        # format output
        df_psd = pd.DataFrame()
        df_psd["f"] = f_vals + 1
        df_psd["psd"] = psdRMS
        # compile hybrid frequency bands
        # ---
        f_band_zero = np.array([[0.0, 0.0, 0.5]])
        # ---
        f_bands_lin = []
        for it_1 in np.arange(1, 456.0, 1):
            f_c = it_1
            f_l = f_c - 0.5
            f_h = f_c + 0.5
            f_bands_lin.append([f_l, f_c, f_h])
        # ---
        f_z = 1000.0
        it_min = int(np.log10(456.0 / f_z) * 1000.0)
        it_max = int(np.log10((fs * 0.5) / f_z) * 1000.0)
        #
        f_bands_md = []
        for it_0 in range(it_min, it_max, 1):
            f_c = f_z * 10 ** (it_0 / 1000.0)
            f_l = f_c * 10 ** (-1.0 / 2000.0)
            f_h = f_c * 10 ** (+1.0 / 2000.0)
            f_bands_md.append([f_l, f_c, f_h])
        # ---
        f_bands = np.concatenate(
            [f_band_zero, np.copy(f_bands_lin), np.copy(f_bands_md)], axis=0
        )
        # ---
        # compute SPL values for hybrid frequency bands
        milDecHy_array = np.array(
            [
                np.sum(df_psd["psd"][df_psd["f"].between(f_band[0], f_band[2])])
                for f_band in f_bands
            ]
        )
        milDecHy_array = milDecHy_array * df
        # --- bio-bands
        bio_bands = np.array(
            [
                [10.0, "LF", 100.0],
                [100.0, "MF", 1000.0],
                [500.0, "KWCOM", 15000.0],
                [15000.0, "KWECH", np.min([100000.0, fs / 2.0])],
                [10.0, "BB", fs / 2.0],
            ]
        )
        #
        bioBands_array = np.array(
            [
                np.sum(
                    df_psd["psd"][
                        df_psd["f"].between(float(bio_band[0]), float(bio_band[2]))
                    ]
                )
                for bio_band in bio_bands
            ]
        )
        bioBands_array = bioBands_array * df

        # formatting outputs
        # millidecades
        df_spl = pd.DataFrame()
        df_spl["f"] = np.copy(f_bands)[:, 1]
        df_spl["val"] = milDecHy_array
        # frequency bands in df
        df_fbands = pd.DataFrame()
        df_fbands["f_start"] = np.copy(f_bands)[:, 0]
        df_fbands["f_center"] = np.copy(f_bands)[:, 1]
        df_fbands["f_end"] = np.copy(f_bands)[:, 2]
        # bio-bands
        df_biobands = pd.DataFrame()
        df_biobands["f_min"] = bio_bands[:, 0]
        df_biobands["f_max"] = bio_bands[:, 2]
        df_biobands["val"] = bioBands_array
        # ---
        return df_spl, df_biobands

    def spectrogram(self, data_file: DataFile, hydrophone: dict[str, any]):
        x, sample_rate = sf.read(data_file.file_path)
        v = x * 3
        nsec = v.size / sample_rate
        spa = 1
        nseg = int(nsec / spa)
        nfreq = int(sample_rate / 2 + 1)
        sg = np.empty((nfreq, nseg), float)
        w = scipy.signal.get_window("hann", sample_rate)
        for x in range(0, nseg):
            cstart = x * spa * sample_rate
            cend = (x + 1) * spa * sample_rate
            f, psd = scipy.signal.welch(
                v[cstart:cend], fs=sample_rate, window=w, nfft=sample_rate
            )
            psd = 10 * np.log10(psd)
            sg[:, x] = psd

        tck = scipy.interpolate.splrep(
            hydrophone["calibration_curve"]["frequency"],
            hydrophone["calibration_curve"]["sensitivity"],
            s=0,
        )
        isens = scipy.interpolate.splev(f, tck, der=0)
        isensg = np.transpose(np.tile(isens, [nseg, 1]))

        plt.figure(dpi=300)
        im = plt.imshow(sg - isensg, aspect="auto", origin="lower", vmin=30, vmax=100)
        plt.yscale("log")
        plt.ylim(10, 100000)
        plt.colorbar(im)
        plt.xlabel("Seconds")
        plt.ylabel("Frequency (Hz)")
        plt.title("Calibrated spectrum levels")
        img_path = (
            f"{constants.RESULTS_TMP_PATH}/{data_file.file_time_name()}_spectrogram.png"
        )
        plt.savefig(img_path)
        return img_path
