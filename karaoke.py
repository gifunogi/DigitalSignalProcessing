#!/usr/bin/env python
# coding: utf-8
import os
import wx
import wx.media
import scipy.io.wavfile as scw
from ProcessMusic.RemoveVocal import *
from ProcessMusic.AnalyzeBPM import *
from GenerateText.GenerateText import *

def main():
    app = wx.App(False)
    frame = MyFrame(parent=None)
    app.MainLoop()


# 歌詞の出力部分クラス
class LyricObject:

    def __init__(self, panel, font, pos):
        # 白文字部分
        self.lstextbk = wx.StaticText(panel, pos=pos)
        # 緑文字部分
        self.lstext = wx.StaticText(panel, pos=pos)
        self.lstring = ""
        # 緑色にする文字数
        self.lcnt = 0

        self.lstextbk.SetFont(font)
        self.lstext.SetFont(font)
        self.lstextbk.SetForegroundColour("#FFFFFF")
        self.lstext.SetForegroundColour("#90EE90")


class MyFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, None, title="karaoke", size=(155*6, 87*6))
        try:
            self.mc = wx.media.MediaCtrl(self, style=wx.SUNKEN_BORDER)
        except NotImplementedError:
            self.Destroy()
            raise # program exit.

        self.bg = wx.Panel(self, -1, pos=(0, 0), size=(155*6, 87*6))
        self.panel = wx.Panel(self, -1, pos=(0, 0), size=(640, 320))
        self.panel.SetBackgroundColour("black")

        self.bpmMark = wx.Panel(self.panel, -1, pos=(600, 280), size=(20, 20))
        self.bpmMark.SetBackgroundColour("#00FF00")

        self.slider = wx.Slider(self.bg, wx.ID_ANY, 1000000, 0, 1000000,
            pos=(20, 320), size=(600, -1), style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.slider.Bind(wx.EVT_SLIDER, self.onSeek)

        loadButton = wx.Button(self.bg, wx.ID_ANY, "Load File", pos=(665, 20))
        self.Bind(wx.EVT_BUTTON, self.onLoadFile, loadButton)

        playButton = wx.Button(self.bg, wx.ID_ANY, "Play", pos=(665, 100))
        playButton.SetToolTip(wx.ToolTip("load a file first")) # message when on mouse
        self.Bind(wx.EVT_BUTTON, self.onPlay, playButton)

        pauseButton = wx.Button(self.bg, wx.ID_ANY, "Pause", pos=(665, 180))
        pauseButton.SetToolTip(wx.ToolTip("press Play to resume"))
        self.Bind(wx.EVT_BUTTON, self.onPause, pauseButton)

        stopButton = wx.Button(self.bg, wx.ID_ANY, "Stop", pos=(665, 260))
        stopButton.SetToolTip(wx.ToolTip("also resets to start"))
        self.Bind(wx.EVT_BUTTON, self.onStop, stopButton)

        # self.Maximize(True)
        self.Show(True)

        font = wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.top_lyric = LyricObject(self.panel, font, (0, 0))
        self.bottom_lyric = LyricObject(self.panel, font, (0, 160))
        while len(self.top_lyric.lstring) > 32:
            self.top_lyric.lstring = shapeLyric(GenerateText().generate())
        while len(self.bottom_lyric.lstring) > 32:
            self.bottom_lyric.lstring = shapeLyric(GenerateText().generate())
        # topとbottomの切り替え(要調整)
        self.lnum = 0

        # True:再生 False:停止
        self.mediaFlag = False
        self.bpm = 60

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)

    def onTimer(self, evt):
        offset = self.mc.Tell()
        self.slider.SetValue(offset)

        # 出力文字数(要調整)
        top_n = self.top_lyric.lcnt/2*len(self.top_lyric.lstring)/(6000/self.bpm)
        bottom_n = self.bottom_lyric.lcnt/2*len(self.bottom_lyric.lstring)/(6000/self.bpm)
        self.top_lyric.lstextbk.SetLabel(self.top_lyric.lstring)
        self.top_lyric.lstext.SetLabel(self.top_lyric.lstring[:int(top_n)])

        self.bottom_lyric.lstextbk.SetLabel(self.bottom_lyric.lstring)
        self.bottom_lyric.lstext.SetLabel(self.bottom_lyric.lstring[:int(bottom_n)])

        if self.lnum%2 == 0:
            self.processLyric(self.top_lyric)
        else:
            self.processLyric(self.bottom_lyric)

        if self.slider.GetValue() % (60.0 / self.bpm  * 1000) < 120:
            self.bpmMark.SetBackgroundColour("#00FF00")
        else:
             self.bpmMark.SetBackgroundColour("#000000")

    # 歌詞出力周りの処理(要調整)
    def processLyric(self, l):
        if l.lcnt/2*len(l.lstring)/(6000/self.bpm) >= len(l.lstring):
            l.lstring = shapeLyric(GenerateText().generate())
            l.lcnt = 0
            self.lnum += 1
        elif self.mediaFlag:
            l.lcnt += 1

    def onLoadFile(self, evt):
        mask = "Media Files|*.wav|All (.*)|*.*"
        dlg = wx.FileDialog(self,
            message="Choose a wav file",
            defaultDir=os.getcwd(), defaultFile="",
            wildcard=mask, style=wx.OPEN|wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = self.getRemovedPath(dlg.GetPath())
            self.timer.Start(int(60.0 / self.bpm * 100))
            print "BPM = " + str(self.bpm)
            print "timeReload = " + str(int(60.0 / self.bpm * 100))
            self.doLoadFile(path)
        dlg.Destroy()

    def doLoadFile(self, path):
        if not self.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path,
            "ERROR", wx.ICON_ERROR|wx.OK)
        else:
            folder, self.filename = os.path.split(path)
            self.slider.SetRange(0, self.mc.Length())

    def onPlay(self, evt):
        self.slider.SetRange(0, self.mc.Length())
        s1 = "  %s" % self.filename
        s2 = "  size: %s ms" % self.mc.Length()
        self.mc.Play()
        self.mediaFlag = True

    def onPause(self, evt):
        self.mc.Pause()
        self.mediaFlag = False

    def onStop(self, evt):
        self.mc.Stop()
        self.mediaFlag = False
        self.top_lyric.lstring = ""
        self.bottom_lyric.lstring = ""

    def onSeek(self, evt):
        """allows dragging the slider pointer to this position"""
        offset = self.slider.GetValue()
        self.mc.Seek(offset)

    # オフボーカル音源を生成しパスを返す
    def getRemovedPath(self, path):
        name, ext = os.path.splitext(path)
        rate, data = scw.read(path)

        analyzer = AnalyzeBPM(data)
        self.bpm = analyzer.analyzeBPM()

        rv = RemoveVocal(data)
        karaoke = rv.removeVocal()
        scw.write(name + "_karaoke.wav", rate, karaoke)

        return name + "_karaoke.wav"


# 文字列挿入
def insert(pos, s, x):
    return x.join([s[:pos], s[pos:] ])

# 出力用に一定文字数毎に改行する
def shapeLyric(s):
    n = len(s)%16 + 1
    for i in range(1, n+1):
        s = insert(16*i, s, "\n")
    return s

if __name__ == '__main__':
    main()