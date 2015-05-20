import wx
import os
import common

class AudioList(wx.Panel):
   def __init__(self, parent):
      super(AudioList, self).__init__(parent)

      self.listBox = None
      self.browseButton = wx.Button(self, label='Browse', size=(100,30))
      self.directory = 'audio/music'
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
      #get list of files
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

   def onSelect(self, e):
      selectedIndex = self.listBox.GetSelection()
      common.audioInfo.select(self.listBox.GetString(selectedIndex), self.directory)

