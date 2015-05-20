import wx
from Audio import Audio
from threading import Thread

class AudioInfo(wx.Panel):
   def __init__(self, parent):
      super(AudioInfo, self).__init__(parent, size=(400,330))

      self.infoBox = wx.StaticBox(self, label='Audio.wav', size=(400,330))
      sbox = wx.StaticBoxSizer(self.infoBox, wx.VERTICAL)
      
      ampPlot = wx.Image('ampPlot.png', wx.BITMAP_TYPE_ANY)
      sbox.Add(wx.StaticBitmap(self, -1, ampPlot.ConvertToBitmap()), 0, wx.CENTER)

      self.playButton = wx.Button(self, label='Play', size=(100,30))
      self.Bind(wx.EVT_BUTTON, self.playAudio, self.playButton)

      sbox.Add(self.playButton, 0, wx.CENTER | wx.TOP, 5)

      self.SetSizer(sbox)

      self.audio = None

   def select(self, fileName, path):
      self.audio = Audio(fileName, path)
      self.infoBox.SetLabel(fileName)

   def setPlayButtonLabel(self, label):
      self.playButton.SetLabel(label)

   def playAudio(self, e):
         if self.audio.nowPlaying:
            Thread(target=self.audio.stop).start()
            self.setPlayButtonLabel('Play')

         else:
            self.setPlayButtonLabel('Stop')
            Thread(target=self.audio.play, args=(self,)).start()

