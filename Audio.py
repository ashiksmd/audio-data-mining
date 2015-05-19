from scipy.io import wavfile

class Audio:
   def __init__(self, name, path):
      self.name = name
      self.path = path
      
      self.sampFreq, self.amp = wavfile.read(path)
      self.


