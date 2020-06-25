%{
Yoo-Jin Hwang 
Program that downsamples the sampling rate in order to 
fit the 16kHz to 44kHz (using the preferred 44kHz here) 
range that most pipelines and studies in bioacoustic 
academic research papers use.

Using Nyquist-Shannon sampling theorem, since the sampling
rate of the recording device is 384kHz, then we can
perfectly reconstruct up to 192kHz. 

Note that the N-S theorem states, f_sample >= 2*f_max.

From above, we want to change the sampling rate from 384kHz 
to 44kHz to isolate the human hearing range. 

%}

[x,fs]=audioread('20190611_205000.WAV');
n = floor(fs/44000); 
new_fs = fs/n;
y = downsample(x, n); 

figure('Name','20190611_205000.WAV');
sgtitle('20190611-205000.WAV'); 
colormap(jet); 
N = round((512)*(384/44.1)); % Ratio of N
window = hanning(N);

num_Seconds = (1/fs)*length(x);
fullTime = x(2:fs*num_Seconds); 

x = x(1:fs*60); % Could change to 5 or 20, it is arbitrary

%%% PLOTTING %%%

% Note that default parameters were used here
% Reference: https://www.mathworks.com/help/signal/ref/spectrogram.html

subplot(1, 3, 1);
spectrogram(x,window,N/2,N,fs,'yaxis');
freq_limit = (new_fs/2)/1000; % to scale axis properly
ylim([0 freq_limit]);
title('Original Signal (scaled)');

subplot(1, 3, 2); 
spectrogram(x,window,N/2,N,fs,'yaxis');
title('Original Signal (no downsampling, not scaled)');

subplot(1, 3, 3);
spectrogram(y,window,N/2,N,new_fs,'yaxis');
title('Downsampled Signal'); 

%%% CHECKING SOUND %%%
player_original = audioplayer(x, fs); 
player_downsampled = audioplayer(y, new_fs); 

%{
Run the following in the command window, line by line:
play(player_original); 
pause(player_original); 
play(player_downsampled);
pause(player_downsampled); 
%}
