"""
  AudioInfo.py
  UI Elements to display audio information
"""
import wx
from Audio import Audio
from threading import Thread

class AudioInfo(wx.Panel):
   def __init__(self, parent):
      super(AudioInfo, self).__init__(parent, size=(400,330))

      self.infoBox = wx.StaticBox(self, label='Audio.wav', size=(400,330))
      sbox = wx.StaticBoxSizer(self.infoBox, wx.VERTICAL)
      
      # Plot time domain graph. Using static image until we can replace with the real thing
      #ampPlot = wx.Image('ampPlot.png', wx.BITMAP_TYPE_ANY)
      #sbox.Add(wx.StaticBitmap(self, -1, ampPlot.ConvertToBitmap()), 0, wx.CENTER)

      # Allow playback of selected audio
      self.playButton = wx.Button(self, label='Play', size=(100,30))
      self.Bind(wx.EVT_BUTTON, self.togglePlayAudio, self.playButton)
      sbox.Add(self.playButton, 0, wx.CENTER | wx.TOP, 5)

      # Display audio classification
      self.audioType = wx.StaticText(self, label='Identified as: Music')
      sbox.Add(self.audioType, 0, wx.CENTER | wx.TOP, 5)

      self.SetSizer(sbox)

      # No audio file selected now
      self.audio = None

   def select(self, fileName, path):
      """ Select an audio file and classify it """
      self.audio = Audio(path, fileName)
      self.infoBox.SetLabel(fileName)
      
      audioType = self.audio.classify('model')
      
      self.audioType.SetLabel('Identified as: ' + audioType)

   def setPlayButtonLabel(self, label):
      """ Update label on the Play button to 'Play' or 'Stop' """
      self.playButton.SetLabel(label)

   def playAudio(self):
      """ Play the selected audio file """
      self.setPlayButtonLabel('Stop')
      self.audio.play(self)
      
   def stopAudio(self):
      """ Stop playback of audio if any are playing """
      self.setPlayButtonLabel('Play')
      self.audio.stop()

   def togglePlayAudio(self, e):
      """ Play/Stop selected audio """
      if self.audio.nowPlaying:
         self.stopAudio()

      else:
         # Start playback in new thread
         Thread(target=self.playAudio).start()

