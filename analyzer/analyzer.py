import os
import time
import threading
import soundfile as sf
import numpy as np
import scipy
import matplotlib.pyplot as plt

import constants
import util
from analyzer.data_file import DataFile


class Analyzer(threading.Thread):
    def __init__(self, config):
        super().__init__()
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

    def run(self):
        while True:
            for hydrophone in self.config["hydrophones"]:
                current_files = util.find_files(
                    hydrophone["directory_to_watch"],
                    hydrophone["file_structure_pattern"],
                )
                new_files = current_files - self.processed_files
                for file in new_files:
                    print(f"Detected new file: {file}")
                    data_file = DataFile(
                        f"{hydrophone['directory_to_watch']}/{file}", hydrophone
                    )
                    if "spectrogram" in hydrophone["metrics"]:
                        self.spectrogram(data_file, hydrophone)
                    if "spl" in hydrophone["metrics"]:
                        self.spl(data_file)
                    with open(constants.PROCESSED_FILES_PATH, "a") as f:
                        f.write(file + "\n")
                    self.processed_files.add(file)
                time.sleep(self.config["scan_interval"])

    def spl(self, file_path):
        pass

    def spectrogram(self, data_file: DataFile, hydrophone: dict[str, any]):
        print(f"Reading data from {data_file.file_path}")
        x, sample_rate = sf.read(data_file.file_path)
        print(f"Sample rate: {sample_rate}")
        v = x * 3
        nsec = v.size / sample_rate
        spa = 1
        nseg = int(nsec / spa)
        print(f"{nseg} segments of length {spa} seconds in {nsec} seconds of audio")
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
