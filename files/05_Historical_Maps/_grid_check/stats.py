import json,glob,numpy as np,math
d={}
import glob
for f in glob.glob('det2_*.json'): d[f[5:-5]]=json.load(open(f))
lat={'zofar69':30.6,'menuha69':30.4,'yafruk69':30.2,'sedom61':31.1}
order=['amatzyahu69','zofar69','menuha69','yafruk69','sedom61','sedom61mm','arava58','yahav48','omer48','adin49','eilat55']
out={}
for k in order:
    v=np.array(d[k],float); m=json.load(open('nodes.json'))[k]['px']
    s=m*(math.cos(math.radians(lat[k])) if k in lat else 1)
    ok=(v[:,6]==1)&(v[:,7]==1)
    v=v[ok]
    dx=(v[:,4]-v[:,2])*s; dy=-(v[:,5]-v[:,3])*s   # + = map line is east/north of true position
    # robust: drop >3 MAD outliers
    r=np.hypot(dx-np.median(dx),dy-np.median(dy)); keep=r<max(3*np.median(r)*1.4826,3*s)
    dx,dy,vv=dx[keep],dy[keep],v[keep]
    mag=np.hypot(dx,dy)
    # affine fit of residuals vs position (km)
    E=(vv[:,0]-vv[:,0].mean())/1000; N=(vv[:,1]-vv[:,1].mean())/1000
    A=np.c_[np.ones_like(E),E,N]
    cx,_,_,_=np.linalg.lstsq(A,dx,rcond=None); cy,_,_,_=np.linalg.lstsq(A,dy,rcond=None)
    rx=dx-A@cx; ry=dy-A@cy; rr=np.hypot(rx,ry)
    rot=math.degrees((cy[1]-cx[2])/2/1000); scl=(cx[1]+cy[2])/2/1000*1e6  # ppm... per km residual m/km
    out[k]=dict(n=int(len(dx)),dropped=int((~keep).sum()),px=round(s,2),mean_dx=round(dx.mean(),1),mean_dy=round(dy.mean(),1),
      rms=round(float(np.sqrt((mag**2).mean())),1),p90=round(float(np.percentile(mag,90)),1),max=round(float(mag.max()),1),
      rot_deg=round(rot,4),scale_m_per_km=round((cx[1]+cy[2])/2,2),rms_after_affine=round(float(np.sqrt((rr**2).mean())),1),
      worst=[[int(a),int(b),round(float(x),1),round(float(y),1)] for a,b,x,y in sorted(zip(vv[:,0],vv[:,1],dx,dy),key=lambda t:-math.hypot(t[2],t[3]))[:3]])
    print(k,out[k])
json.dump(out,open('stats_out.json','w'),indent=1)
