s = load('handel');
y = s.y;  Fs = s.Fs;

% Corrupting cosine
csig = 0.05*cos(6*pi/10*(1:length(y))');

% Corrupted signal
ysig = y + csig;

% Filter corrupted signal with good and bad filters
Hd = lowpass1;  Num = Hd.Numerator;
bNum = zeros(size(Num));
offs = round(length(Num)/2);
bNum(offs-2:offs+2) = ones(1,5)/5;
ysigf_good = conv(ysig,Num);
%ysigf_bad = conv(ysig,ones(1,5)/5);  
ysigf_bad = conv(ysig,bNum);  

% Show good filter frequency response
[H1,W1] = freqz(Num,1,1000);
fh = figure;  
subplot(2,1,1);  plot(W1,20*log10(abs(H1)));  axis([0 pi -60 10]);  
title('Frequency response:  good filter');
subplot(2,1,2);  plot(W1,angle(H1));
%fvtool(Num,1);

% Show bad filter frequency response
[H2,W2] = freqz(ones(1,5)/5,1,1000);
fh = figure;  
subplot(2,1,1);  plot(W2,20*log10(abs(H2)));  axis([0 pi -60 10]);  
title('Frequency response:  bad filter');
subplot(2,1,2);  plot(W2,angle(H2));
%fvtool(ones(1,5)/5,1);

% Show signals
sp = 500;  ep = 600;
fh = figure;
plot(sp:ep,y(sp:ep),'g',sp:ep,ysig(sp:ep),'r');
legend('Ideal signal','Actual (corrupted) signal');
title('Input');

% Good filter input and output
fh = figure;
plot(sp:ep,ysig(sp:ep),'g',sp:ep,ysigf_good((sp:ep)+offs),'r');
title('Good filter input and output');

% Bad filter input and output
fh = figure;
plot(sp:ep,ysig(sp:ep),'g',sp:ep,ysigf_bad((sp:ep)+offs),'r');
title('Bad filter input and output');

% Comparison
ylp = conv(y,Num);
fh = figure; 
plot(sp:ep,ylp((sp:ep)+offs),'b',sp:ep,ysigf_good((sp:ep)+offs),'g',sp:ep,ysigf_bad((sp:ep)+offs),'r');
legend('Good filter ideal output','Good filter actual output','Bad filter actual output');
title('Outputs');