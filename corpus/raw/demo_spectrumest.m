% Example code for demonstrating spectrum estimation

N = 255;  % Observation length (must be odd)

% Sinusoids (change these as required)
A0 = 1;  w0 = pi/3;
A1 = 0.75;  w1 = 2*pi/3;
%A1 = 0.5;  w1 = 2*pi/3;
%A1 = 0.5;  w1 = 2*pi/3;
%A1 = 0.25;  w1 = 1.1*pi/3;

nv=-3:N+3;
wr = zeros(size(nv));
wt = zeros(size(nv));

% Rectangular window
wr(4:N+4) = 1;

% Triangular window
tw = zeros(N,1);
tw(1:floor(N/2)) = 1:floor(N/2);
tw(floor(N/2)+1:end) = floor(N/2)+1:-1:1;
wt(4:4+length(tw)-1) = tw;

% Select window (choose desired window below)
ws = wr;
% ws = wt;

% Slowly calculate FT of window
w=-pi:0.01:pi;
mW = zeros(size(w));
for n=1:length(w)
  cw = w(n);
  cmW = 0;
  for p=0:N-1
    cmW = cmW + ws(4+p)*exp(sqrt(-1)*cw*p);
  end
  mW(n) = abs(cmW);
end

% Make the signal
nv=-3:N+3;
sv=zeros(size(nv));
for i=1:length(nv);
  n = nv(i);
  sv(i) = A0*cos(w0*n) + A1*cos(w1*n);
  %sv(i) = cos(pi/3*n) + 0.25*cos(1.2*pi/3*n);
end

% Make the windowed signal
svw = sv.*ws;

% Slowly calculate FT of signal
w=-pi:0.01:pi;
mXw = zeros(size(w));
for n=1:length(w)
  cw = w(n);
  cmXw = 0;
  for p=0:N-1
    cmXw = cmXw + svw(4+p)*exp(sqrt(-1)*cw*p);
  end
  mXw(n) = abs(cmXw);
end

% Calculate DFT of the windowed signal
svwr = svw(4:end-4);
dftsvwr = abs(fft(svwr));
dftw = 2*pi*(0:N-1)/N;
for k=1:length(dftw)
  if dftw(k)>pi 
    dftw(k) = dftw(k)-2*pi;
  end
end

% Ideal frequency response
wideal=[-w1 -w0 w0 w1];
mX = [A1 A0 A0 A1]/2;

% Signal and window
figure;
subplot(3,1,1);
ph = stem(nv,sv,'filled');
set(ph,'markersize',3);
hold on; plot(nv, zeros(size(nv)), 'k-');  hold off;
axis tight;
xlabel('n', "FontSize",20);  ylabel('x[n]', "FontSize",20);

subplot(3,1,2);
ph = stem(nv,ws,'filled');
set(ph,'markersize',3);
hold on; plot(nv, zeros(size(nv)), 'k-');  hold off;
axis tight;
xlabel('n', "FontSize",20);  ylabel('w[n]', "FontSize",20);

subplot(3,1,3);
ph = stem(nv,svw,'filled');
set(ph,'markersize',3);
hold on; plot(nv, zeros(size(nv)), 'k-');  hold off;
axis tight;
xlabel('n', "FontSize",20);  ylabel('xw[n]', "FontSize",20);

figure;
subplot(4,1,1)
ph = stem(wideal,mX,'^','filled');
xt = [-pi, -2*pi/3, -pi/3, 0, pi/3, 2*pi/3, pi];
xtl = {'-pi', '-2pi/3', '-pi/3', '0', 'pi/3', '2pi/3', 'pi'};
set(gca,'XTick',xt);
set(gca,'XTickLabel',xtl);
xlabel('w', "FontSize",20);  ylabel('|X(ejw)|', "FontSize",20);
axis([-pi pi 0 1.1]);

subplot(4,1,2)
ph = plot(w,mW);
xt = [-pi, 0, pi];
xtl = {'-pi', '0', 'pi'};
set(gca,'XTick',xt);
set(gca,'XTickLabel',xtl);
% yt = [0, N];
% set(gca,'YTick',yt);
xlabel('w', "FontSize",20);  ylabel('|W(ejw)|', "FontSize",20);
axis([-pi pi 0 ceil(max(mW))]);

subplot(4,1,3)
ph = plot(w,mXw);
xt = [-pi, -2*pi/3, -pi/3, 0, pi/3, 2*pi/3, pi];
xtl = {'-pi', '-2pi/3', '-pi/3', '0', 'pi/3', '2pi/3', 'pi'};
set(gca,'XTick',xt);
set(gca,'XTickLabel',xtl);
xlabel('w', "FontSize",20);  ylabel('|Xw(ejw)|', "FontSize",20);
axis([-pi pi 0 ceil(max(mXw))]);

subplot(4,1,4)
ph = stem(dftw,dftsvwr,'filled');
set(ph,'markersize',3);
xt = [-pi, -2*pi/3, -pi/3, 0, pi/3, 2*pi/3, pi];
xtl = {'-N/2', '-N/3', '-N/6', '0', 'N/6', 'N/3', 'N/2'};
set(gca,'XTick',xt);
set(gca,'XTickLabel',xtl);
xlabel('k', "FontSize",20);  ylabel('|Xw[k]|', "FontSize",20);
axis([-pi pi 0 ceil(max(dftsvwr))]);

%print(gcf, '-depsc2', 'dft_fig18.eps');
%(gcf);
