import wx
import pyaudio
import wave
import sys

class AudioInfo(wx.Panel):
   def __init__(self, parent):
      super(AudioInfo, self).__init__(parent, size=(700,450))

      self.text = wx.StaticText(self, label="Audio Info")
      self.playButton = wx.Button(self, label='Play', size=(100,30))
      self.Bind(wx.EVT_BUTTON, self.playAudio, self.playButton)

      vbox = wx.BoxSizer(wx.VERTICAL)
      vbox.Add(self.text, 0, wx.CENTER)
      vbox.Add(self.playButton, 0, wx.CENTER)

      self.SetSizer(vbox)

      self.fileName = None
      self.path = None

   def select(self, fileName, path):
      self.fileName = fileName
      self.path = path

      self.text.Destroy()
      self.text = wx.StaticText(self, label=path + '/' + fileName)

   def playAudio(self, e):
      wf = wave.open(self.path + '/' + self.fileName, 'rb')
      p = pyaudio.PyAudio()

      stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels = wf.getnchannels(), rate = wf.getframerate(), output = True)

      data = wf.readframes(4096)

      while data != '':
         stream.write(data)
         data = wf.readframes(4096)

      stream.stop_stream()
      stream.close()

      p.terminate()

