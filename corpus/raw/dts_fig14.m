ws = 0.01;
w = -2*pi-0.25*pi:ws:2*pi+0.25*pi;

M1 = 0;  M2 = 4;
H = 1/(M1+M2+1)*sin(w*(M1+M2+1)/2)./sin(w/2).*exp(-i*w*(M2-M1)/2);

mH = abs(H);
aH = angle(H);

subplot(2,1,1);
phm = plot(w,mH);
ah = gca;
xt = [-2*pi, -pi, -2*pi/5, 0, 2*pi/5, pi, 2*pi];
xtl = {'-2pi',  '-pi',  '-2pi/5',  '0',  '2pi/5',  'pi',  '2pi'};
set(gca,'XTick',xt);
set(gca,'XTickLabel',xtl);
yt = [0 1];
set(gca,'YTick',yt);
%set(gca,'XTickLabel',xtl);

subplot(2,1,2);
pha = plot(w,aH);
xt = [-2*pi, -pi, 0, pi, 2*pi];
xtl = {'-2pi',  '-pi',  '0',  'pi',  '2pi'};
set(gca,'XTick',xt);
set(gca,'XTickLabel',xtl);
yt = [-pi, 0, pi];
ytl = {'-pi',  '0',  'pi'};
set(gca,'YTick',yt);
set(gca,'YTickLabel',ytl);
xlabel('omega');  ylabel('angH');

%close(gcf);
