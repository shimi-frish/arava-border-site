import sys; sys.path.insert(0,'scripts'); from georef_tools import *
def similarity(G):
    M=[];v=[]
    for c,r,E,N in G:
        x,y=c,-r; M+= [[x,-y,1,0],[y,x,0,1]]; v+=[E,N]
    a,b,tx,ty=np.linalg.lstsq(np.array(M,float),np.array(v,float),rcond=None)[0]
    return lambda c,r:(a*c-b*(-r)+tx, b*c+a*(-r)+ty), np.hypot(a,b), np.degrees(np.arctan2(b,a))
