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
      self.Bind(wx.EVT_BUTTON, self.togglePlayAudio, self.playButton)
      sbox.Add(self.playButton, 0, wx.CENTER | wx.TOP, 5)

      self.audioType = wx.StaticText(self, label='Identified as: Music')
      sbox.Add(self.audioType, 0, wx.CENTER | wx.TOP, 5)

      self.SetSizer(sbox)

      self.audio = None

   def select(self, fileName, path):
      self.audio = Audio(fileName, path)
      self.infoBox.SetLabel(fileName)
      
      audioType = 'Music'
      if fileName.startswith('mu'):
         audioType = 'Music'
      else:
         audioType = 'Speech'

      self.audioType.SetLabel('Identified as: ' + audioType)

   def setPlayButtonLabel(self, label):
      self.playButton.SetLabel(label)

   def playAudio(self):
      self.setPlayButtonLabel('Stop')
      self.audio.play(self)
      
   def stopAudio(self):
      self.setPlayButtonLabel('Play')
      self.audio.stop()

   def togglePlayAudio(self, e):
         if self.audio.nowPlaying:
            self.stopAudio()

         else:
            Thread(target=self.playAudio).start()

