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
        # kokokaraRYUUYO
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

        # self.currentVolume = 50
        # self.volumeCtrl = wx.Slider(self.bg, style=wx.SL_HORIZONTAL|wx.SL_INVERSE, pos=(665, 340), size=(100, -1))
        # self.volumeCtrl.SetRange(0, 100)
        # self.volumeCtrl.SetValue(self.currentVolume)
        # self.volumeCtrl.Bind(wx.EVT_SLIDER, self.onSetVolume)

        # self.Maximize(True)
        self.Show(True)

        font = wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.stextbk = wx.StaticText(self.panel)
        self.stext = wx.StaticText(self.panel)
        self.stextbk.SetFont(font)
        self.stext.SetFont(font)

        ext = "load .mp3 .mpg .mid .wav .wma .au or .avi files"
        self.st_info = wx.StaticText(self.bg, wx.ID_ANY, ext ,pos=(200, 200), size=(300,-1))
        self.st_info.SetBackgroundColour("white")

        # self.lyric = u"軋んだ思いを吐き出したいのは\n  存在の証明が他に無いから"
        self.lyric = shapeLyric(GenerateText().generate())
        while len(self.lyric) > 32:
            self.lyric = shapeLyric(GenerateText().generate())
        self.lcnt = 0
        # True:再生 False:停止
        self.mediaFlag = False
        self.bpm = 60

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        # self.timer.Start(100)

        #ヤバい#
        self.stextbk_2 = wx.StaticText(self.panel, pos=(0, 160))
        self.stext_2 = wx.StaticText(self.panel, pos=(0, 160))
        self.stextbk_2.SetFont(font)
        self.stext_2.SetFont(font)
        self.lyric_2 = shapeLyric(GenerateText().generate())
        while len(self.lyric_2) > 32:
            self.lyric_2 = shapeLyric(GenerateText().generate())
        self.lcnt_2 = 0
        self.lnum = 0
        #ヤバい#

    def onTimer(self, evt):
        """moves the slider pointer"""
        offset = self.mc.Tell()
        self.slider.SetValue(offset)

        self.stextbk.SetLabel(self.lyric)
        self.stext.SetLabel(self.lyric[:int(self.lcnt/2*len(self.lyric)/(6000/self.bpm))])
        self.stextbk.SetForegroundColour("white")
        self.stext.SetForegroundColour("#90EE90")


        #ヤバい#
        self.stextbk_2.SetLabel(self.lyric_2)
        self.stext_2.SetLabel(self.lyric_2[:int(self.lcnt_2/2*len(self.lyric_2)/(6000/self.bpm))])
        self.stextbk_2.SetForegroundColour("white")
        self.stext_2.SetForegroundColour("#90EE90")
        #ヤバい#

        if self.lnum%2 == 0:
            if self.lcnt/2*len(self.lyric)/(6000/self.bpm) >= len(self.lyric):
                self.lyric = shapeLyric(GenerateText().generate())
                while len(self.lyric) > 32:
                    self.lyric = shapeLyric(GenerateText().generate())
                self.lcnt = 0
                self.lnum += 1
            elif self.mediaFlag:
                self.lcnt += 1
        else:
            if self.lcnt_2/2*len(self.lyric_2)/(6000/self.bpm) >= len(self.lyric_2):
                self.lyric_2 = shapeLyric(GenerateText().generate())
                while len(self.lyric_2) > 32:
                    self.lyric_2 = shapeLyric(GenerateText().generate())
                self.lcnt_2 = 0
                self.lnum += 1
            elif self.mediaFlag:
                self.lcnt_2 += 1

        # print "s = " + str(self.slider.GetValue()) + "  c = " + str(self.slider.GetValue() % (60.0 / self.bpm  * 1000))
        if self.slider.GetValue() % (60.0 / self.bpm  * 1000) < 120:
            self.bpmMark.SetBackgroundColour("#00FF00")
        else:
             self.bpmMark.SetBackgroundColour("#000000")

    def onLoadFile(self, evt):
        mask = "Media Files|*.mp3;*.mpg;*.mid;*.wav;*.au;*.avi|All (.*)|*.*"
        dlg = wx.FileDialog(self,
            message="Choose a media file (.mp3 .mpg .mid .wav .wma .au .avi)",
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
            self.st_info.SetLabel("  %s" % self.filename)
            # set the slider range min to max
            self.slider.SetRange(0, self.mc.Length())
            # self.mc.Play()

    def onPlay(self, evt):
        self.slider.SetRange(0, self.mc.Length())
        s1 = "  %s" % self.filename
        s2 = "  size: %s ms" % self.mc.Length()
        self.st_info.SetLabel(s1+s2)
        self.mc.Play()
        self.mediaFlag = True

    def onPause(self, evt):
        self.mc.Pause()
        self.mediaFlag = False

    def onStop(self, evt):
        self.mc.Stop()
        self.mediaFlag = False
        self.lyric = ""

    def onSeek(self, evt):
        """allows dragging the slider pointer to this position"""
        offset = self.slider.GetValue()
        self.mc.Seek(offset)

    def onSetVolume(self, event):
        """
        Sets the volume of the music player
        """
        self.currentVolume = self.volumeCtrl.GetValue()
        print "setting volume to: %s" % int(self.currentVolume)
        self.mc.SetVolume(self.currentVolume)

    def getRemovedPath(self, path):
        name, ext = os.path.splitext(path)
        rate, data = scw.read(path)

        analyzer = AnalyzeBPM(data)
        self.bpm = analyzer.analyzeBPM()

        rv = RemoveVocal(data)
        karaoke = rv.removeVocal()
        scw.write(name + "_karaoke.wav", rate, karaoke) 

        return name + "_karaoke.wav"

def insert(pos, s, x):
    return x.join([s[:pos], s[pos:] ])

def shapeLyric(s):
    n = len(s)%16 + 1
    for i in range(1, n+1):
        s = insert(16*i, s, "\n")
    return s

if __name__ == '__main__':
    main()