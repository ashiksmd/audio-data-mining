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
import subprocess

class Audio:
   def __init__(self, path, name=None):
      if name is None:
         path, name = os.path.split(path)

      self.name = name
      self.path = path
      self.nowPlaying = False

      # Read wav file
      self.sampFreq, self.tDomain = wavfile.read(path + '/' + name)
      
      self.tDomain = self.normalize(self.tDomain)

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

      fDomain = self.normalize(fDomain)

      self.fDomain = fDomain
      self.nPoints = nPoints
      self.nUniquePoints = nUniquePoints

   def getFullPath(self):
      return self.path + '/' + self.name

   def stop(self):
      """ Stop audio playback """
      self.nowPlaying = False

   def normalize(self, sampArray):
      mean = 0.0
      stdDev = 0.0
      size = len(sampArray)

      for i in range(0, size):
         mean += sampArray[i]

      mean /= size

      for i in range(0, size):
         stdDev += (sampArray[i] - mean)**2

      stdDev = math.sqrt(stdDev/size)

      for i in range(0, size):
         sampArray[i] = (sampArray[i] - mean) / stdDev

      return sampArray


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

   def getEnergy(self):
      """ Compute and return energy of audio """
      energy = 0.0

      for i in range(0, self.nPoints):
         x = self.tDomain[i]
         energy += x**2

      energy /= self.nPoints

      return energy

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

   def getZCrossingRate(self):
      """ Compute and return zero crossing rate of audio """
      zcr = 0.0
      for i in range(1, self.nPoints):
         sgn1 = 1 if self.tDomain[i] > 0 else -1
         sgn2 = 1 if self.tDomain[i-1] > 0 else -1

         zcr += abs(sgn1 - sgn2)

      zcr /= (2.0 * self.nPoints)

      return zcr

   def getFeatures(self):
      """ Get features of audio for training or querying with the model """
      return "1:" + str(self.getEnergy()) + \
             " 2:" + str(self.getCentroid()) + \
             " 3:" + str(self.getZCrossingRate())


def classify(self, model, featuresFile='temp.txt'):
      """ Classify this audio using the provided model """

      subprocess.call(('svm_classify', featuresFile, model, 'result.txt'))

      # Read results
      resultFile = open('result.txt', 'r')
      audioType = 'Music' if float(resultFile.readline()) > 0 else 'Speech'

      return audioType

def getAudioFiles(directory):
    # Fetch list of files in selected directory
    fileList = os.listdir(directory)
    fileList.sort()

    audioList = []
    for f in fileList:
      if f.endswith('.wav'):
       audioList.append(Audio(directory, f))

    return audioList

def generateFeatureData(audioList, outFileName='TrainingData.txt'):
    """
     Generate training data from audio files in directory.
     Write generated data into outFile
    """

    outFile = open(outFileName, "w")

    for audio in audioList:
        features = audio.getFeatures()
        
        if audio.name.startswith('mu'):
          audioType = '1' #music
        else:
          audioType = '-1' #speech
        
        outFile.write(audioType + ' ' + features + ' # ' + audio.name  + '\n')

    outFile.close()

    return outFileName

if __name__ == '__main__':
    
    argc = len(sys.argv)
    if argc > 2 and sys.argv[1] == 'generate':
       directory = sys.argv[2]
       outFile = sys.argv[3] if argc > 3 else 'TrainingData.txt'
       audioList = getAudioFiles(directory)
       generateFeatureData(audioList, outFile)
    elif argc == 4 and sys.argv[1] == 'classify':
       model = sys.argv[2]
       directory = sys.argv[3]
       audioList = getAudioFiles(directory)
       generateFeatureData(audioList, 'temp.txt')
       results = classify(model, 'temp.txt')

       for i in range(0, len(audioList)):
          print audioList[i].name, ":", results[i]

    else:
       print 'Invalid input. Format:\n\tpython Audio.py generate <directory> [output-file]' +\
             '\nOR\n\tpython Audio.py classify <model> <directory>'
