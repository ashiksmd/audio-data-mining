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
import getopt

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

      # Get frequency values to go with magnitudes
      time = nPoints / float(self.sampFreq)
      frequencies = np.arange(nUniquePoints) / time

      # Store frequency domain as list of (frequency, magnitude)
      self.fDomain = zip(frequencies, fDomain)

      # Store sizes of arrays for later
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

   def getEnergy(self):
      """ Compute and return energy of audio """
      energy = 0.0

      for i in range(0, self.nPoints):
         energy += self.tDomain[i] ** 2

      energy /= self.nPoints
      return energy

   def getCentroid(self):
      """ Compute and return spectral centroid of audio """
      centroid = 0.0
      sumMagnitude = 0.0

      for i in range(0,self.nUniquePoints):
         freq,magnitude = self.fDomain[i]

         centroid += freq*magnitude
         sumMagnitude += magnitude
        
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

   def getBandwidth(self):
      """ Compute and return the bandwidth of the audio """
      # Use mean of the magnitudes as threshold
      threshold = np.mean([x[1] for x in self.fDomain])
      
      # Find freqencies which have magnitude greater than threshold
      nonZero = [f for f,x in self.fDomain if x > threshold]

      bandwidth = max(nonZero) - min(nonZero)
      return bandwidth
     

   def getFeatures(self):
      """ Get features of audio for training or querying with the model """
      return "1:" + str(self.getEnergy()) + \
             " 2:" + str(self.getCentroid()) + \
             " 3:" + str(self.getZCrossingRate()) + \
             " 4:" + str(self.getBandwidth())

   def predictType(self):
      """ Predict type of audio file using file name """
      return 'Music' if self.name.startswith('mu') else 'Speech'

def classify(model, featuresFile='tmp/features.txt'):
      """ Classify audio files using the provided model and features """

      # Use external svm_classify to classify audio using the given features
      subprocess.call(['svm_classify', featuresFile, model, 'tmp/result.txt'])

      # Read results
      results = []
      with open('tmp/result.txt', 'r') as f:
         results = f.readlines()
         for i in range(0, len(results)):
            results[i] = 'Music' if float(results[i]) > 0 else 'Speech'

      return results

def getAudioFiles(directory):
    """ Find all the audio files in this directory """

    # Fetch list of files in selected directory
    fileList = os.listdir(directory)
    fileList.sort()

    # Create Audio objects
    audioList = []
    for f in fileList:
      if f.endswith('.wav'):
       audioList.append(Audio(directory, f))

    return audioList

def generateFeatureData(directory, outFileName='tmp/features.txt', isClassifying=False):
    """
     Generate training data from audio files in directory.
     Write generated data into outFileName
     If isClassifying, use class as 0(unknown), else use 1 for music, -1 for speech
    """

    audioList = getAudioFiles(directory)

    outFile = open(outFileName, "w")

    for audio in audioList:
        features = audio.getFeatures()
        
        if isClassifying:  # We are classifying, we don't know type
           audioType = '0'
        else:              # We are generating training data. Try to predict using file name
           audioType = '1' if audio.predictType() == 'Music' else '-1'
        
        outFile.write(audioType + ' ' + features + ' # ' + audio.name  + '\n')

    outFile.close()

    return audioList

if __name__ == '__main__':

    options, _ = getopt.getopt(sys.argv[1:], 'gcd:o:m:h', ['generate', 'classify',
                                                          'directory=', 'out=', 'model=',
                                                          'help'])

    isClassifying = True # Set to False if we are trying to generate training data
    directory = 'test'
    outputFile = 'tmp/output.txt'
    model = 'models/model.dat'

    for opt,arg in options:
       if opt in ('-g', '--generate'):
          isClassifying = False
       elif opt in ('-d', '--directory'):
          directory = arg
       elif opt in ('-o', '--out'):
          outputFile = arg
       elif opt in ('-m', '--model'):
          model = arg
       elif opt in ('-h', '--help'):
          print 'Usage:\n\tpython Audio.py [Method] [Options]'
          print '\nMethod:'
          print '\t-g, --generate\n\t\tGenerate training data'
          print '\t-c, --classify\n\t\tClassify audio files (default unless you use --generate)'
          print '\nOptions:'
          print '\t-d, --directory=Directory'
          print '\t\tAudio files to use as training or testing data are read from here. Defaults to "."'
          print '\t-o, --out=File\n\t\tOutput will be written to this file. Defaults to output.txt'
          print '\t-m, --model=Model\n\t\tModel to use for classifying. Defaults to model.dat'
          print '\t-h, --help\n\t\tDisplay this message'
          sys.exit(0)

    # Generate features for all the audio files in directory
    audioList = generateFeatureData(directory, outputFile, isClassifying)

    if isClassifying:
       results = classify(model, outputFile)

       # To compute precision, recall
       totalMusic = 0    # Total number of music files in sample
       correctMusic = 0  # Number of music files correctly reported to be music
       reportedMusic = 0 # Number of music files reported to be music

       print '\nResults'
       for i in range(0, len(audioList)):
          print audioList[i].name, ":", results[i]

          if results[i] == 'Music':
             reportedMusic += 1
          if audioList[i].predictType() == 'Music':
             totalMusic += 1
             if results[i] == 'Music':
                correctMusic += 1

       # To avoid division by zero. Precision should be zero
       if reportedMusic == 0:
          reportedMusic = 1

       print '\nPrecision:', correctMusic, '/', reportedMusic, '=', 100*correctMusic/reportedMusic, '%'
       print 'Recall:', correctMusic, '/', totalMusic, '=', 100*correctMusic/totalMusic, '%'


