# -*- coding: utf-8 -*
import sys
import os.path
from scipy.io.wavfile import *

wavfile = sys.argv[1]
name, ext = os.path.splitext(wavfile)

fs, data = read(wavfile)
print "File name :", wavfile
print "Sampling rate :", fs
#2チャネル(ステレオ)音源であることを確認
if (data.shape[1] == 2):
	#左右チャネルに分割
	left = data[:,0]
	right = data[:,1]
	#差分をとって中央の音源を相殺
	diff = left - right
	karaoke = numpy.c_[diff, -diff]
	write(name + "_karaoke.wav", fs, karaoke)
	print("\nsuccess")
