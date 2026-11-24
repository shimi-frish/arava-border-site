# Georeference IRCICA H-791 (Jordan tourist map, DLS 1962, print 1979) on 1-degree graticule; work on 1/4 reduced image
import sys,numpy as np; sys.path.insert(0,'/mnt/project-files/non-israeli-maps/scripts')
from warp import warp
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
O='/mnt/project-files/non-israeli-maps/'
src='/tmp/claude-0/dl/irc4.png'
gp=np.array([[35,32,344,1019],[36,32,1072,1019],[37,32,1817,1013],[35,31,344,1858],[36,31,1074,1860],[37,31,1817,1853],[35,30,344,2701],[36,30,1073,2706],[37,30,1817,2700]],float)
r=warp(src,gp[:,:2],gp[:,2:],4326,O+'georef/Jordan_Tourist_1962_UTM36.tif',res=60,order=2,bounds=(640000,3240000,800000,3480000))
