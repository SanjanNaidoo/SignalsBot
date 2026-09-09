gp = load('Gold_pr.dat');  % gold price
gpc = gp(:,1);  % closing price
N = length(gpc);

% Moving average parameters
M1 = 0;  
M2 = 2;

% New figure
fh = figure;

% Plot price
subplot(2,1,1);
sh = stem(1:N, gpc, 'filled');
set(sh,'Color','b');
axis([1 length(gpc) 500 800]);
title('Input:  Gold closing');

% Output plot
subplot(2,1,2);
axis([1 length(gpc) 500 800]);
title(sprintf('Output (M1=%i, M2=%i)',M1,M2));

for n=M2+1:N-M1
  
  % Recolour input
  nvu = n + M1;  nvl = n - M2;
  subplot(2,1,1);
  hold on;  sho = stem(nvl:nvu,gp(nvl:nvu),'filled');  hold off;
  set(sho,'Color','r');
  
  % Plot output point
  gpsm = mean(gp(nvl:nvu));
  subplot(2,1,2);
  hold on;  sh2 = stem(n,gpsm,'filled');  hold off;
  set(sh2,'Color','r');  
  
  pause;
  delete(sho);
end