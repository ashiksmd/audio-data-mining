"""
   AudioList.py
   UI Elements to display audio files in current directory
"""
import wx
import os
import common

class AudioList(wx.Panel):
   def __init__(self, parent):
      super(AudioList, self).__init__(parent)

      self.listBox = None;

      # Choose folder to get audio files from
      self.browseButton = wx.Button(self, label='Browse', size=(100,30))

      # Use this folder for now
      self.directory = 'audio/music'

      # Load audio files in the folder
      self.loadAudioList()

      self.Bind(wx.EVT_BUTTON, self.chooseFolder, self.browseButton)

      vbox = wx.BoxSizer(wx.VERTICAL)
      vbox.Add(self.listBox)
      vbox.Add(self.browseButton, 0, wx.CENTER)

      self.SetSizer(vbox)
   
   def chooseFolder(self, e):
      """ Choose folder to get audio files from """

      dialog = wx.DirDialog(None, "Choose a directory:", "audio/",
                          style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

      if dialog.ShowModal() == wx.ID_OK:
          self.directory = dialog.GetPath()
          dialog.Destroy()
          self.loadAudioList()

   def loadAudioList(self):
      # Fet list of files in selected directory
      fileList = os.listdir(self.directory)
      fileList.sort()

      audioFiles = []

      for f in fileList:
         if f.endswith('.wav'):
            audioFiles.append(f)

      if(self.listBox is not None):
         self.listBox.Destroy()

      self.listBox = wx.ListBox(self, choices=audioFiles, size=(200,300))
      self.Bind(wx.EVT_LISTBOX, self.onSelect, self.listBox)

      self.listBox.SetSelection(0)

      # Update info area
      if common.audioInfo and common.audioInfo.audio:
         self.onSelect(None)

   def onSelect(self, e):
      # If a previous audio file is playing, stop it now
      if common.audioInfo.audio is not None:
          common.audioInfo.stopAudio()

      selectedIndex = self.listBox.GetSelection()
      common.audioInfo.select(self.listBox.GetString(selectedIndex), self.directory)

