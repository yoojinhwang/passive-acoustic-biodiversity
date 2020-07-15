from __future__ import division

import numpy as np
import os
import csv
import pandas as pd

from scipy import signal
from scipy.stats import zscore
from scipy.signal import spectrogram
from scipy.fftpack import fft, ifft
from scipy.signal import butter, lfilter
import scipy.signal as scipy_signal
# import scipy.signal import welch 

import soundfile as sf
import sounddevice as sd
import matplotlib.pyplot as plt

from memory_profiler import profile

def plot_spectrogram(x, filename):
    prefix = os.path.spliltext(filename)[0]
    nfft = 1024 # allowed values = {64, 128, 256, 512, 1024, 2048}
    # Compute spectrogram
    fs = 384000
    f, t, Pxx = spectrogram(x, fs, nfft = nfft, nperseg = nfft, noverlap = nfft/2, window = 'hann', scaling = 'density')
    
    # TO DO; avoid the "plt.<...>" calls as much as possible
    # Use: * fig, axs = plt.subplots(3,1); ax = axs[0] and use ax.plot(x) instead
    # Reason: it is generally not good to have important state hidden
    #  in the state of some external library
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(x)
    plt.xlim([0,len(x)])
    plt.ylabel('Amplitude [V]')
    plt.xlabel('Time [sec]')

    plt.subplot(3,1,2)
    plt.pcolormesh(t, f, np.log(Pxx))
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    # cb = plt.colorbar() # uncomment to see the colorbar
    # cb.set_label('Power Spectral Density [dB]')

    # Taking a while to load...  
    plt.subplot(3,1,3)
#     f, Pxx_den = signal.welch(x, fs, nperseg=1024)
    # f, Pxx_spec = signal.welch(x, fs, 'flattop', 1024, scaling='spectrum')
#     plt.xlim([0,5000])
    f, Pxx_den = signal.periodogram(x, fs)

    plt.semilogy(f, Pxx_den)
    plt.ylabel('PSD [V**2/Hz]')
    plt.xlabel('Frequency (Hz)')
    plt.title('Periodogram')
    plt.savefig(f'{prefix}_spectrogram.png')

    plt.close('all')
    # TO DO: plt.close(fig)

    # plt.show()


# Example
# plot_spectrogram('20190617_080000.WAV') 

### FILTERING FUNCTIONS ###
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Get n-second clips
def split_into_n_seconds(wav_data, samplerate, n=5):
    length_in_seconds = len(wav_data) / samplerate
    length_in_minutes = length_in_seconds / 60
    shorter_len = int(round(length_in_minutes / (1/(60/n))))
    print(shorter_len)
    second_clips = None
    
    try:  
        second_clips = np.split(wav_data, shorter_len)
        
    except: # Figure out what this exception error is for
        cut_wav_data = wav_data[:-((len(wav_data)) % shorter_len)]
        second_clips = np.split(cut_wav_data, shorter_len)

    print('%d %d-second clips' % (len(second_clips), n))
    return second_clips


### CODING ###
downsampling_rate = 44100
original_rate = 384000
rate_ratio = original_rate/downsampling_rate

### IMPORT DATA ###
datapath = "./Data/"
listing = os.listdir(datapath)

### EACH FILE ###
@profile
def full_plot(): 
    for file in listing:
        print("Before: ")
        print(file)
        x, fs = sf.read(datapath + file)
        # x = zscore(x) 
        plot_spectrogram(x, str(file.rsplit('.',1)[0]) + '_before')

        # # Split files into 5 second audio clips 
        split_data = np.array(split_into_n_seconds(x, original_rate, 5))
        
        number_of_rows = split_data.shape[0]
        random_indices = np.random.choice(number_of_rows, size=1, replace=False)
        x = split_data[random_indices, :]

        # Sample rate and desired cutoff frequencies (in Hz).
        # fs needs to be at least 2 x Wn
        # 191kHz limit due to Nyquist frequency 

        # Figure out issues here:
        x = butter_bandpass_filter(x, 5000, 191000, fs, order=5) 

        ### DOWNSAMPLING ### 
        # 2) Scipy's built in resample function 
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.resample.html
        print(x)
        x = scipy_signal.resample(x, int(len(x)*rate_ratio))
        
        print("After: ")
        print(file)
        plot_spectrogram(x, str(file.rsplit('.',1)[0]) + '_after')

if __name__ == '__main__':
    full_plot()