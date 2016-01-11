# coding: utf-8
import sys
import os.path
import numpy as np
import scipy.io.wavfile as scw

def main():
	# データ読み込み
	if len(sys.argv) > 1:
		wavfile = sys.argv[1]
	else:
		wavfile = "tempo_120.wav"
	name, ext = os.path.splitext(wavfile)

	fs, data = scw.read(wavfile)
	print "File name :", wavfile
	print "Sampling rate :", fs

	rv = RemoveVocal(data)
	karaoke = rv.removeVocal()
	scw.write(name + "_karaoke.wav", fs, karaoke)

class RemoveVocal(object):

	def __init__(self, data):
		self.data = data

	def removeVocal(self):
		# 2チャネル(ステレオ)音源であることを確認
		if len(self.data.shape) == 2:
			# 左右チャネルに分割
			# 差分をとって中央の音源を相殺
			diff = self.data[:,0] - self.data[:,1]
			removed = np.c_[diff, -diff]

		return removed

if __name__ == '__main__':
	main()
