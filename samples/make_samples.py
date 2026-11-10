# Builds ZK-88's drum samples from Karoryfer "Unruly Drums" (CC0): mixes the microphones of each hit,
# trims and fades it, and renders an Amen-style break played on the same kit.
import numpy as np,subprocess,wave,os,sys
SR=44100
# K: the Samples folder of a checkout of https://github.com/sfzinstruments/karoryfer.unruly-drums
K=sys.argv[1] if len(sys.argv)>1 else 'karoryfer.unruly-drums/Samples/';OUT=os.path.dirname(os.path.abspath(__file__))+'/'
def load(p):
    r=subprocess.run(['ffmpeg','-v','error','-i',K+p,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True,check=True)
    return np.frombuffer(r.stdout,dtype=np.float32).copy()
def mix(parts,length):
    n=int(length*SR);y=np.zeros(n,np.float32)
    for p,g in parts:
        x=load(p)[:n];y[:len(x)]+=g*x
    return y
def biquad(x,kind,f,Q=.707,gain_db=0):   # standard EQ filters (RBJ cookbook)
    A=10**(gain_db/40);w=2*np.pi*f/SR;c=np.cos(w);al=np.sin(w)/(2*Q)
    if kind=='hp':b=[(1+c)/2,-(1+c),(1+c)/2];a=[1+al,-2*c,1-al]
    elif kind=='peak':b=[1+al*A,-2*c,1-al*A];a=[1+al/A,-2*c,1-al/A]
    elif kind=='hshelf':sq=2*np.sqrt(A)*al;b=[A*((A+1)+(A-1)*c+sq),-2*A*((A-1)+(A+1)*c),A*((A+1)+(A-1)*c-sq)];a=[(A+1)-(A-1)*c+sq,2*((A-1)-(A+1)*c),(A+1)-(A-1)*c-sq]
    b=np.array(b)/a[0];a=np.array(a)/a[0];y=np.zeros_like(x);x1=x2=y1=y2=0.
    for i,xi in enumerate(x):
        yi=b[0]*xi+b[1]*x1+b[2]*x2-a[1]*y1-a[2]*y2;x2,x1,y2,y1=x1,xi,y1,yi;y[i]=yi
    return y.astype(np.float32)
def snare_eq(x):   # drum & bass snare EQ: lose the low mud, bring out the crack and the air
    x=biquad(x,'hp',140,.7);x=biquad(x,'peak',220,1.2,-2);x=biquad(x,'peak',4500,.8,7);return biquad(x,'hshelf',8000,.7,5)
def onset(x,th=.02):   # start each sample right at the hit
    i=np.argmax(np.abs(x)>th*np.abs(x).max());return x[max(0,i-int(.001*SR)):]
def fade(x,sec):
    m=int(sec*SR);x=x.copy();x[-m:]*=np.linspace(1,0,m)**2;return x
def norm(x,db=-1):return x*(10**(db/20)/np.abs(x).max())
def save(name,x):
    x=np.clip(x,-1,1);w=wave.open(OUT+name+'.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((x*32767).astype('<i2').tobytes());w.close();print(name,'%.2fs'%(len(x)/SR),os.path.getsize(OUT+name+'.wav')//1024,'KB')
def kick(v,rr):return mix([(f'k20/in/rr{rr}/kick_dirty_vl{v}_rr{rr}.flac',1),(f'k20/oh/rr{rr}/kick_dirty_vl{v}_rr{rr}.flac',.45)],.5)
def snare(v,rr):return mix([(f's13/top/rr{rr}/s13_center_vl{v}_rr{rr}.flac',1),(f's13/btm/rr{rr}/s13_center_vl{v}_rr{rr}.flac',.45),
                             (f's13/ohl/rr{rr}/s13_center_vl{v}_rr{rr}.flac',.4),(f's13/ohr/rr{rr}/s13_center_vl{v}_rr{rr}.flac',.4)],.6)
def hat(name,length):return mix([(f'h14/cl/rr1/{name}_rr1.flac',1),(f'h14/ohl/rr1/{name}_rr1.flac',.3),(f'h14/ohr/rr1/{name}_rr1.flac',.3)],length)
def ride(v):return mix([(f'r20/cl/rr1/ride_bow_vl{v}_rr1.flac',1),(f'r20/oh/rr1/ride_bow_vl{v}_rr1.flac',.5)],2.5)
# keep the loudness differences between soft and hard hits: normalise each family by its loudest member
def family(items,db=-1):
    pk=max(np.abs(x).max() for _,x in items);g=10**(db/20)/pk
    return [(n,x*g) for n,x in items]
kicks=family([('kick1',fade(onset(kick(8,1)),.08)[:int(.42*SR)]),('kick2',fade(onset(kick(8,2)),.08)[:int(.42*SR)]),('kick_soft',fade(onset(kick(5,1)),.08)[:int(.42*SR)])])
kicks=[(n,fade(x,.06)) for n,x in kicks]
snares=family([('snare1',onset(snare_eq(snare(9,1)))),('snare2',onset(snare_eq(snare(9,2)))),('snare_mid',onset(snare_eq(snare(6,1)))),('snare_ghost',onset(snare_eq(snare(3,1))))])
snares=[(n,fade(x[:int(.45*SR)],.12)) for n,x in snares]
hats=family([('hat',onset(hat('hh_closed_tip_vl5',.3))),('hat_soft',onset(hat('hh_closed_tip_vl3',.3))),('open',onset(hat('hh_open_tip_vl4',.9)))],-3)
hats=[(n,fade(x[:int((.7 if n=='open' else .2)*SR)],.1 if n=='open' else .05)) for n,x in hats]
for n,x in kicks+snares+hats:save(n,x)
# ---- Amen-style break: the famous pattern, played on this kit, mixed like a break ----
D=dict(kicks+snares+hats)
rides={'ride':onset(ride(6)),'ride_soft':onset(ride(4))}
BPM=170;st=60/BPM/4;bar=16*st;n=int((bar+.6)*SR);y=np.zeros(n,np.float32)
rng=np.random.default_rng(7)
def put(x,step,g):
    i=int((step*st+rng.normal(0,.0015))*SR);i=max(0,i);m=min(len(x),n-i);y[i:i+m]+=g*x[:m]
for s in range(0,16,2):put(rides['ride' if s%4==0 else 'ride_soft'][:int(1.2*SR)],s,.32)
for s,k in [(0,'kick1'),(2,'kick2'),(10,'kick1'),(11,'kick_soft')]:put(D[k],s,1)
for s,k,g in [(4,'snare1',1),(7,'snare_mid',.75),(9,'snare_mid',.85),(12,'snare2',1),(15,'snare_ghost',.7)]:put(D[k],s,g)
# glue: a simple compressor (fast attack, short release) then gentle tape-style saturation, like a sampled break
env=0;out=np.empty_like(y);a=np.exp(-1/(.002*SR));r=np.exp(-1/(.08*SR));pk=np.abs(y).max();th=pk*.35
for i,v in enumerate(np.abs(y)):
    env=a*env+(1-a)*v if v>env else r*env+(1-r)*v
    gr=1 if env<th else (th+(env-th)/4)/env
    out[i]=y[i]*gr
out=np.tanh(1.6*out/np.abs(out).max())/np.tanh(1.6)
brk=out[:int(bar*SR)];brk=norm(brk,-1);brk[-int(.004*SR):]*=np.linspace(1,0,int(.004*SR))
save('break',brk)
print('break step length %.5f s at %d BPM'%(st,BPM))
