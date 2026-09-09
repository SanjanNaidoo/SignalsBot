% Moving average parameters
M1 = 0;  M2 = 4;
N = M1 + M2 + 1;    % Include n = 0
nv = 1:100;

fh = figure;
for w0=(0:10)/10*pi;
  xv = cos(w0*nv);
  subplot(2,1,1);  stem(nv,xv,'filled');
  axis([min(nv) max(nv) -1 1]);
  title(sprintf('x[n] = cos(wn) for w = %f',w0),'FontSize',20);
  yv = conv(xv,ones(1,N)/N,'same');
  subplot(2,1,2);  stem(nv,yv,'filled');
  title(sprintf('y[n] after MA filter',w0),'FontSize',20);
  axis([min(nv) max(nv) -1 1]);

  pause;
end