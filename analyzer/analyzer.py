from datetime import datetime
import soundfile as sf
import numpy as np
import scipy
import matplotlib.pyplot as plt

import config
from data_file import DataFile


class Analyzer:
    @staticmethod
    def analyze(data_file):
        tmp_results_path = 1
        if "spectrogram" in config.METRICS:
            img_path = Analyzer.spectrogram(data_file)
        if "spl" in config.METRICS:
            Analyzer.spl(data_file)
        return

    @staticmethod
    def spl(file_path):
        pass

    @staticmethod
    def spectrogram(data_file: DataFile):
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

        tck = scipy.interpolate.splrep(calfreq, calsens, s=0)
        isens = scipy.interpolate.splev(f, tck, der=0)
        isensg = np.transpose(np.tile(isens, [nseg, 1]))

        # x, sample_rate = sf.read(file_path)
        # v = x * 3  # convert scaled voltage to volts
        # print(f"Sample rate: {sample_rate}")
        # nsec = (v.size) / sample_rate  # number of seconds in vector
        # spa = 1  # seconds per average
        # nseg = int(nsec / spa)
        # print(f"{nseg} segments of length {spa} seconds in {nsec} seconds of audio")
        # nfreq = int(sample_rate / 2 + 1)
        # LTSA = np.empty((nfreq, nseg), float)
        # w = scipy.signal.get_window("hann", sample_rate)
        # # process LTSA
        # for x in range(0, nseg):
        #     cstart = x * spa * sample_rate
        #     cend = (x + 1) * spa * sample_rate
        #     f, psd = scipy.signal.welch(
        #         v[cstart:cend], fs=sample_rate, window=w, nfft=sample_rate
        #     )
        #     psd = 10 * np.log10(psd) + 177.9
        #     LTSA[:, x] = psd

        # plt.figure(dpi=300)
        # im = plt.imshow(LTSA, aspect="auto", origin="lower", vmin=30, vmax=100)
        # plt.yscale("log")
        # plt.ylim(10, 1000)
        # plt.colorbar(im)
        # plt.xlabel("Minute of day")
        # plt.ylabel("Frequency (Hz)")
        # plt.title("Calibrated spectrum levels")
        # plt.show()
        # save LTSA to file
        # np.save("LTSA.npy", LTSA)
        # # save compressed
        # np.savez_compressed("LTSA.npz", LTSA)

        plt.figure(dpi=300)
        im = plt.imshow(sg - isensg, aspect="auto", origin="lower", vmin=30, vmax=100)
        plt.yscale("log")
        plt.ylim(10, 100000)
        plt.colorbar(im)
        plt.xlabel("Seconds")
        plt.ylabel("Frequency (Hz)")
        plt.title("Calibrated spectrum levels")
        img_path = (
            f"{config.RESULTS_TMP_PATH}/{data_file.file_time_name}_spectrogram.png"
        )
        plt.savefig(img_path)
        return img_path


calfreq = [
    0,
    250,
    10000,
    20100,
    30100,
    40200,
    50200,
    60200,
    70300,
    80300,
    90400,
    100400,
    110400,
    120500,
    130500,
    140500,
    150600,
    160600,
    170700,
    180700,
    190700,
    200000,
]
calsens = [
    -177.90,
    -177.90,
    -176.80,
    -176.35,
    -177.05,
    -177.35,
    -177.30,
    -178.05,
    -178.00,
    -178.40,
    -178.85,
    -180.25,
    -180.50,
    -179.90,
    -180.15,
    -180.20,
    -180.75,
    -180.90,
    -181.45,
    -181.30,
    -180.75,
    -180.30,
]
