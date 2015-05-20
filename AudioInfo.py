import wx
from Audio import Audio
from threading import Thread

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

      self.audio = None

   def select(self, fileName, path):
      self.audio = Audio(fileName, path)

      self.text.Destroy()
      self.text = wx.StaticText(self, label=path + '/' + fileName)

   def playAudio(self, e):
         if self.audio.nowPlaying:
            Thread(target=self.audio.stop).start()

         else:
            Thread(target=self.audio.play).start()

