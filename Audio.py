"""
  Audio.py
  Audio class contains methods for extracting audio features
  Also contains functions for generating training data, as well as training and querying the model
"""
from scipy.io import wavfile
import pyaudio
import wave
import pylab
import math
import sys
import os
import numpy as np

class Audio:
   def __init__(self, path, name=None):
      if name is None:
         path, name = os.path.split(path)

      self.name = name
      self.path = path
      self.nowPlaying = False

      # Read wav file
      self.sampFreq, self.tDomain = wavfile.read(path + '/' + name)


      # Get frequency domain
      fDomain = pylab.fft(self.tDomain)
      nPoints = len(self.tDomain)
      nUniquePoints = int(math.ceil((nPoints+1)/2.0))
      fDomain = abs(fDomain[0:nUniquePoints])

      # Normalize frequency domain
      fDomain = fDomain/float(nPoints)
      fDomain = fDomain ** 2
      if nPoints % 2 > 0:
         fDomain[1:len(fDomain)] = fDomain[1:len(fDomain)] * 2
      else:
         fDomain[1:len(fDomain)-1] = fDomain[1:len(fDomain)-1] * 2

      self.fDomain = fDomain
      self.nPoints = nPoints
      self.nUniquePoints = nUniquePoints

   def getFullPath(self):
      return self.path + '/' + self.name

   def stop(self):
      """ Stop audio playback """
      self.nowPlaying = False

   def play(self, context=None):
      """ 
         Start audio playback.
         context object with stopAudio() for callbacks to UI
      """

      self.nowPlaying = True

      # Open file for reading
      wf = wave.open(self.path + '/' + self.name, 'rb')
      p = pyaudio.PyAudio()

      # Open stream for playback
      stream = p.open( format = p.get_format_from_width( wf.getsampwidth() ),
                       channels = wf.getnchannels(),
                       rate = wf.getframerate(), output = True)

      # Read file in chunks of 1024 bytes
      data = wf.readframes(1024)

      # Read while there is data left to read
      # If nowPlaying is False, user has clicked Stop
      while data != '' and self.nowPlaying:
         stream.write(data)
         data = wf.readframes(1024)

      stream.stop_stream()
      stream.close()

      p.terminate()

      self.nowPlaying = False

      # Callback to UI to signal that audio has finished playing
      if context is not None:
         context.stopAudio()


   def getPitch(self):
      """ Return pitch of audio """
      return 0

   def getEnergy(self):
      """ Compute and return energy of audio """
      return 0

   def getCentroid(self):
      """ Compute and return spectral centroid of audio """
      time = self.nPoints / self.sampFreq
      frequency = np.arange(self.nUniquePoints) / time

      centroid = 0.0
      sumMagnitude = 0.0

      for i in range(0,self.nUniquePoints):
         f = frequency[i]
         x = self.fDomain[i]

         centroid += f*x
         sumMagnitude += x
        
      centroid /= sumMagnitude

      return centroid

   def getFeatures(self):
      """ Get features of audio for training or querying with the model """
      return "1:" + str(self.getPitch()) + \
             " 2:" + str(self.getEnergy()) + \
             " 3:" + str(self.getCentroid())

   def classify(self, model):
      """ Classify this audio using the provided model """
      audioType = None

      if self.name.startswith('mu'):
         audioType = 'Music'
      else:
         audioType = 'Speech'

      return audioType

def generateTrainingData(directory, outFileName='TrainingData'):
    """
     Generate training data from audio files in directory.
     Write generated data into outFile
    """
    # Fet list of files in selected directory
    fileList = os.listdir(directory)
    fileList.sort()

    outFile = open(outFileName, "w")

    for f in fileList:
      if f.endswith('.wav'):
        audio = Audio(directory, f)
        features = audio.getFeatures()
        
        if audio.name.startswith('mu'):
          audioType = '1' #music
        else:
          audioType = '0' #speech
        
        #outFile.write(audio.name + '\t')#for testing
        outFile.write(audioType + ': ' + features + '\n')

    outFile.close()

def trainModel(model, directory):
   """
      Generate training data from audio files in directory and train model
   """
   # Generate training data first
   generateTrainingData(directory)

   print 'Training model', model
   # Use SVM to train and create model from the data generated above
   return None

if __name__ == '__main__':
    
    argc = len(sys.argv)
    if argc > 2 and sys.argv[1] == 'generate':
       directory = sys.argv[2]
       outFile = sys.argv[3] if argc > 3 else 'TrainingData'
       generateTrainingData(directory, outFile)
    elif argc == 4 and sys.argv[1] == 'train':
       model = sys.argv[2]
       directory = sys.argv[3]
       trainModel(model, directory)
    elif argc == 4 and sys.argv[1] == 'classify':
       model = sys.argv[2]
       audioFile = sys.argv[3]
       audio = Audio(audioFile)
       print 'Classification:', audio.classify(model)
    else:
       print 'Invalid input. Format:\n\tpython Audio.py generate <directory> [output-file]' +\
             '\nOR\n\tpython Audio.py train <model> <directory>' +\
             '\nOR\n\tpython Audio.py classify <model> <audio-file>'
