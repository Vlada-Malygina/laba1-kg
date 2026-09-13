import numpy as np
from PIL import Image
from math import floor
img_mat=np.zeros((2000,2000,3),dtype=np.uint8)
def line(img_mat,x0,y0,x1,y1):
    d_max=max(abs(floor(x0)-floor(x1)), abs(floor(y0)-floor(y1)))
    l=d_max+1
    if l==1: img_mat[floor(y0),floor(x0)]=255,2,141
    else: 
        dx= (x1-x0)/(l-1)
        dy= (y1-y0)/(l-1)
        x,y=x0,y0
        for _ in range(l):
            img_mat[floor(y),floor(x)]=255,2,141
            x=x+dx
            y=y+dy
# line(img_mat,0,0,999,999)
# line(img_mat,0,999,999,0)
v=[]
f=[]
file=open('model.obj')
for s in file:
    sp=s.split()
    if (sp[0]=='v'):
        v.append([float(sp[1]),float(sp[2]),float(sp[3])])
    if (sp[0]=='f'):
            sf1=sp[1].split('/')
            sf2=sp[2].split('/')
            sf3=sp[3].split('/')
            f.append([int(sf1[0]),int(sf2[0]),int(sf3[0])])
for i in range(len(v)):
    img_mat[floor(-10000*v[i][1])+1000, floor(10000*v[i][0])+1000]=255,2,141
for i in range(len(f)):
     x0=floor(10000*v[f[i][0]-1][0])+1000
     y0=floor(-10000*v[f[i][0]-1][1])+1000
     x1=floor(10000*v[f[i][1]-1][0])+1000
     y1=floor(-10000*v[f[i][1]-1][1])+1000
     x2=floor(10000*v[f[i][2]-1][0])+1000
     y2=floor(-10000*v[f[i][2]-1][1])+1000
     line(img_mat,x0,y0,x1,y1)
     line(img_mat,x2,y2,x1,y1)
     line(img_mat,x0,y0,x2,y2)
     

img=Image.fromarray(img_mat)
img.save('img.png')