from scipy.io import wavfile
import pyaudio
import wave

class Audio:
   def __init__(self, name, path):
      self.name = name
      self.path = path
      self.nowPlaying = False
      #self.sampFreq, self.amp = wavfile.read(path)

   def stop(self):
      self.nowPlaying = False

   def play(self):
      self.nowPlaying = True

      wf = wave.open(self.path + '/' + self.name, 'rb')
      p = pyaudio.PyAudio()

      stream = p.open( format = p.get_format_from_width( wf.getsampwidth() ),
                       channels = wf.getnchannels(),
                       rate = wf.getframerate(), output = True)

      data = wf.readframes(1024)

      while data != '' and self.nowPlaying:
         stream.write(data)
         data = wf.readframes(1024)

      stream.stop_stream()
      stream.close()

      p.terminate()

