# DigitalSignalProcessing
ディジタル信号処理作製課題

音声信号を入力することでセンターキャンセル法から音声信号のオフボーカル化(カラオケ音源化)を行って，自動で歌詞の生成を行うGUIプログラムです．音源はwav(WAVE Formatファイル)のみ対応しています．
###karaoke.py
GUI本体プログラムです．
`python karaoke.py`  
のコマンドで起動します．[wxPython](http://www.wxpython.org/)モジュールを利用しています．

## GenerateText
自動歌詞生成を行うプログラム部分です．[MeCab](http://mecab.googlecode.com/svn/trunk/mecab/doc/index.html?sess=3f6a4f9896295ef2480fa2482de521f6)によって形態素解析を行い，マルコフ連鎖のアルゴリズムから文章生成を行っています．
[o-tomox](https://github.com/o-tomox)様のhttps://github.com/o-tomox/TextGenerator のプログラムを利用しています．
###PrepareChain.py
文章生成の元となる文章を準備します．
`python PrepareChain.py lyric.txt`  
でlyric.txt内の文章を形態素解析し，データベースファイルの出力を行います．  
元にするテキストファイルはJ-POPの歌詞ファイルなどがおすすめです．

###GenerateText.py
文章生成を行う部分のプログラムです．  
`python GenerateText.py`  
と，コンソール上で入力してもPrepareChain.pyで準備した文章から文章の自動生成・出力が行えます．

## ProcessMusic
音声処理を行うプログラム部分です．音源はwav(WAVE Formatファイル)のみ対応しています．

###AnalyzeBPM.py
音声のBPM解析を行うプログラムです．(http://ism1000ch.hatenablog.com/entry/2014/07/08/164124)様のプログラムを参考にしています．  
[SciPy](http://www.scipy.org/ ''SciPy)モジュールからwavファイルを扱っています．
`python AnalizeBPM.py music.wav` 
と，コンソール上で入力してもmusic.wavファイルのBPM解析が行えます．  
コメントアウトされている
```
# plt.plot(np.arange(MIN_BPM, MAX_BPM), match_list)  
# plt.show()
```
の部分をコメントアウトを解除すると，BPMのマッチ度のグラフの出力が行えます．

###RemoveVocal.py
ステレオのwavファイルをLRチャネルの比較を行ってオフボーカル音源にするプログラムです．  
`python karaoke.py music.wav`  
で同じディレクトリにmusic_karaoke.wawの生成を行えます．  