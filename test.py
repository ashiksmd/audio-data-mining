from pylab import *
from scipy.io import wavfile
import matplotlib.pyplot as plt

fs, data = wavfile.read("test.wav")

b=[(ele/2**8.)*2-1 for ele in data] # this is 8-bit track, b is now normalized on [-1,1)
c = fft(b) # create a list of complex number
d = len(c)  # you only need half of the fft list
plt.plot(abs(c[:(d-1)]),'r') 
plt.show()
