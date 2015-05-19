# UI.py
# Main UI to execute queries

import wx
from AudioList import AudioList
from AudioInfo import AudioInfo
import common

class AudioDMUI(wx.Frame):
   def __init__(self, parent, title):
      super(AudioDMUI, self).__init__(parent, title=title, size=(800,400))

      self.audioList = AudioList(self)
      self.audioInfo = AudioInfo(self)

      common.audioInfo = self.audioInfo

      hbox = wx.BoxSizer(wx.HORIZONTAL)
      hbox.Add(self.audioList)
      hbox.Add(self.audioInfo)

      self.SetSizer(hbox)
      self.Show()

if __name__ == '__main__':
   app = wx.App()
   AudioDMUI(None, title='Audio Data Mining')
   app.MainLoop()





