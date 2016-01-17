# coding: utf-8
import sys
import numpy as np
import scipy.io.wavfile as scw
import matplotlib.pyplot as plt

MIN_BPM = 60
MAX_BPM = 240
BPM_RANGE = range(MIN_BPM, MAX_BPM)

def main():
    # データ読み込み
    if len(sys.argv) > 1:
        wavfile = sys.argv[1]
    else:
        wavfile = "tempo_120.wav"

    rate, data = scw.read(wavfile)
    print "File name :", wavfile
    print "Sampling rate :", rate

    analyzer = AnalyzeBPM(data)
    bpm = analyzer.analyzeBPM()

    print "bpm = " + str(bpm)

class AnalyzeBPM(object):
    def __init__(self, data):
        self.data = data

    def analyzeBPM(self):
        # normalize
        self.data = self.data / (2.0 ** 15)
        # ステレオ音源のときはLチャネルのみ抽出
        if len(self.data.shape) > 1:
            self.data = self.data[:,0]

        # 1フレームのサンプル数
        sample = 512
        frame_max = self.data.size / sample
        sample_max = frame_max * sample
        # フレーム毎の振幅二乗和から音量を計算
        frame_list = np.hsplit(self.data[:sample_max], frame_max)
        amp_list = np.array([np.sqrt(sum(x ** 2)) for x in frame_list])

        # フレーム毎の音量の増加を計算
        amp_diff_list = amp_list[1:] - amp_list[:-1]
        amp_diff_list = np.vectorize(lambda x: 0.0 if x < 0 else x)(amp_diff_list)

        # 各bpmのマッチ度を計算
        match_list = self.calc_all_match(amp_diff_list)
        # 最大マッチbpm
        most_match = np.argmax(match_list)
        bpm = int(MIN_BPM + most_match)

        # plt.plot(np.arange(MIN_BPM, MAX_BPM), match_list)
        # plt.show()

        return bpm

    # 信号とbpmのマッチ度を計算
    def calc_match_bpm(self, data, bpm):
        n = len(data)
        phase = np.arange(1, n+1) * 2 * np.pi * (bpm / 60.0) / (44100 / 512.0)
        # 音量増加量の周波数解析
        cos_match = np.dot(data, np.cos(phase)) / n
        sin_match = np.dot(data, np.sin(phase)) / n

        return np.sqrt(cos_match ** 2 + sin_match ** 2)

    # 各bpmでのマッチ度リストを返す
    def calc_all_match(self, data):
        # 各bpmにおいてmatch度を計算
        match_list = np.array([self.calc_match_bpm(data, bpm) for bpm in BPM_RANGE])

        return match_list

if __name__ == '__main__':
    main()