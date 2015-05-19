import wx

class AudioInfo(wx.Panel):
   def __init__(self, parent):
      super(AudioInfo, self).__init__(parent, size=(700,450))

      self.text = wx.StaticText(self, label="Audio Info")
      self.playButton = wx.Button(self, label='Play', size=(100,30))

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

