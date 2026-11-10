# Builds ZK-88's sound effects from public-domain (CC0) recordings:
#   VSCO 2 Community Edition (https://github.com/sgossner/VSCO-2-CE): trumpets, glockenspiel, concert bass drum, timpani, gong
#   Kenney Sci-Fi Sounds (https://kenney.nl/assets/sci-fi-sounds, GitHub copy: Boyquotes/kenney-sci-fi-sounds-for-godot): lasers, explosions
# usage: python3 make_fx.py <VSCO-2-CE folder> <kenney sci-fi sounds folder>
import numpy as np,subprocess,wave,os,sys
SR=44100;V=sys.argv[1].rstrip('/')+'/';K=sys.argv[2].rstrip('/')+'/';OUT=os.path.dirname(os.path.abspath(__file__))+'/'
def load(p):
    r=subprocess.run(['ffmpeg','-v','error','-i',p,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True)
    return np.frombuffer(r.stdout,dtype=np.float32).astype(np.float64)
def peakfreq(x,lo=80,hi=4000):   # the pitch of a held note: strongest harmonic-product peak in its loudest part
    e=np.convolve(x**2,np.ones(2048),'same');c=np.argmax(e);seg=x[max(0,c-8192):c+8192]
    S=np.abs(np.fft.rfft(seg*np.hanning(len(seg)),n=65536));f=np.fft.rfftfreq(65536,1/SR);H=S.copy()
    for k in (2,3,4):H[:len(S)//k]*=S[::k][:len(S)//k]
    m=(f>lo)&(f<hi);return f[m][np.argmax(H[m])]
def shift(x,ratio):   # resample: ratio>1 raises the pitch (and shortens), like speeding up a tape
    n=int(len(x)/ratio);return np.interp(np.arange(n)*ratio,np.arange(len(x)),x)
def tune(x,target):return shift(x,target/peakfreq(x))
def bend(x,cents_curve):   # play with a pitch that changes over time (cents per output sample)
    rate=2**(cents_curve/1200);pos=np.cumsum(rate);pos=pos[pos<len(x)-1];return np.interp(pos,np.arange(len(x)),x)
def onset(x,th=.02):i=np.argmax(np.abs(x)>th*np.abs(x).max());return x[max(0,i-int(.001*SR)):]
def fade(x,sec):m=int(sec*SR);x=x.copy();x[-m:]*=np.linspace(1,0,m)**2;return x
def fit(x,sec):n=int(sec*SR);return np.pad(x,(0,max(0,n-len(x))))[:n]
def norm(x,db=-1):return x*(10**(db/20)/np.abs(x).max())
def biquad(x,kind,f,Q=.707,gain_db=0):
    A=10**(gain_db/40);w=2*np.pi*f/SR;c=np.cos(w);al=np.sin(w)/(2*Q)
    if kind=='hp':b=[(1+c)/2,-(1+c),(1+c)/2];a=[1+al,-2*c,1-al]
    elif kind=='lp':b=[(1-c)/2,1-c,(1-c)/2];a=[1+al,-2*c,1-al]
    elif kind=='peak':b=[1+al*A,-2*c,1-al*A];a=[1+al/A,-2*c,1-al/A]
    b=np.array(b)/a[0];a=np.array(a)/a[0];y=np.zeros_like(x);x1=x2=y1=y2=0.
    for i,xi in enumerate(x):
        yi=b[0]*xi+b[1]*x1+b[2]*x2-a[1]*y1-a[2]*y2;x2,x1,y2,y1=x1,xi,y1,yi;y[i]=yi
    return y
def save(name,x):
    x=np.clip(x,-1,1);w=wave.open(OUT+name+'.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((x*32767).astype('<i2').tobytes());w.close();print(name,'%.2fs'%(len(x)/SR),os.path.getsize(OUT+name+'.wav')//1024,'KB')
E4,B4,E5=329.63,493.88,659.26
T=V+'Brass/Trumpet/'
# ---- air horn: a trumpet section playing an E chord, driven hard like a sound-system horn ----
def horn_chord(kind,length):
    parts=[(f'{kind}/Sum_SHTrumpet_{kind}_D#3_v3_rr1.wav',E4,1),(f'{kind}/Sum_SHTrumpet_{kind}_A#3_v3_rr1.wav',B4,.85),(f'{kind}/Sum_SHTrumpet_{kind}_F4_v3_rr1.wav',E5,.7)]
    y=np.zeros(int(length*SR))
    for p,f,g in parts:
        x=fit(onset(tune(load(T+p),f)),length);y+=g*x
        d=int(.011*SR);y[d:]+=.45*g*fit(onset(tune(load(T+p),f*2**(9/1200))),length)[:len(y)-d]   # a second player, slightly sharp and late
    return y
def horn_fx(y):   # brassy grit: drive, then shape like a horn speaker
    y=np.tanh(2.0*y/np.abs(y).max());y=biquad(y,'hp',260,.7);y=biquad(y,'peak',1300,.9,4);y=biquad(y,'peak',3600,1,-4);return biquad(y,'lp',6500,.7)
hs=horn_fx(horn_chord('stac',.32));save('horn_short',norm(fade(hs,.08),-2))
hl=horn_chord('sus',1.0);n=len(hl);cur=np.zeros(n);fall=int(.32*SR);cur[n-fall:]=-np.linspace(0,1,fall)**1.6*160   # the last blast sags at the end
hl=fade(horn_fx(fit(bend(hl,cur),.9)),.22);save('horn_long',norm(hl,-2))
# ---- boom: concert bass drum + low explosion + timpani + gong tail + sub drop, one cinematic hit ----
L=2.4;t=np.arange(int(L*SR))/SR
bd=fit(onset(load(V+'Percussion/BDrumNewhit_v7_rr1_Sum.wav')),L)
lfe=fit(onset(load(K+'low_frequency_explosion_000.ogg')),L)
cr=fit(onset(load(K+'explosion_crunch_000.ogg')),L)
tp=fit(onset(load(V+'Percussion/Timpani/Timpani2_Hit_v4_rr1_Sum.wav')),L)
gg=fit(onset(load(V+'VSCO 1 Percussion/varMetal/Gong/gong_hit_ff.wav')),L)
sub=np.sin(2*np.pi*np.cumsum(30+30*np.exp(-t/.25))/SR)*np.exp(-t/.7)
boom=norm(bd)*1+norm(lfe)*.75+norm(cr)*.3+norm(tp)*.45+norm(gg)*.22+sub*.5
boom=np.tanh(1.4*boom/np.abs(boom).max());save('boom',norm(fade(boom,.6),-1))
# ---- laser: Kenney's big laser with a bright zap on top ----
ll=fit(onset(load(K+'laser_large_000.ogg')),.5);ls=fit(onset(load(K+'laser_small_001.ogg')),.5)
save('laser',norm(fade(norm(ll)+.25*norm(ls),.12),-1))
# ---- coin: two glockenspiel notes in the key (B6 then E7) ----
gl=onset(load(V+'Percussion/Glock/glock_medium_C6.wav'))   # a glockenspiel sounds two octaves above its written note
def strongest(x,lo,hi):S=np.abs(np.fft.rfft(x[:int(.3*SR)]*np.hanning(int(.3*SR)),n=1<<17));f=np.fft.rfftfreq(1<<17,1/SR);m=(f>lo)&(f<hi);return f[m][np.argmax(S[m])]
def glock(f):return shift(gl,f/strongest(gl,1000,6000))
c=np.zeros(int(1.1*SR));a=fit(glock(1975.5),1.1);b=fit(glock(2637.0),1.1);d=int(.075*SR)
c+=.75*a;c[d:]+=b[:len(c)-d];save('coin',norm(fade(c,.4),-2))
# ---- power up: a fast glockenspiel run upwards, sped up a little ----
pw=onset(load(V+'Miscellania Raw/Misc 2/glock_glisses/glock_fx_up_chromatic_fast_01.wav'))
pw=fit(shift(pw,1.5),1.3);save('power',norm(fade(pw,.35),-2))
