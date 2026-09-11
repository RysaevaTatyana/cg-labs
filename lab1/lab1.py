
from math import floor
import numpy as np
import PIL.Image as Image
#img_mat = np.zeros((1000,1000), dtype = np.uint8) #черное изображение
#for i in range(1000):
#     for j in range(1000):
            # img_mat[i,j] = 255 # белый
#          
img_mat = np.zeros((2000,2000,3), dtype = np.uint8)
#трехмерное изображение
#for i in range(1000):
#     for j in range(1000):
            # img_mat[i,j,0] = 255 # красный
#            img_mat[i,j,0] = (i+j)%256 # градиент

#x0,y0, x1, y1 = 10,10,500,950

def draw_line(img_matrix, x0,y0,x1,y1):
    d_max = max(abs(floor(x0)-floor(x1)), abs(floor(y0)-floor(y1)))
    l = d_max+1
    if l==1:
        img_matrix[y0,x0] = 72,6,7
        return img_matrix
    else:
        dx = (x1-x0)/(l-1)
        dy = (y1-y0)/(l-1)
        x,y = x0,y0
        for _ in range(l):
            img_matrix[floor(y),floor(x)] = 72,6,7
            x+=dx
            y+=dy
        return img_matrix
#img_mat = draw_line(img_mat,10,10,955,955)

file = open("model.obj")
v = []
f = []
for line in file:
    sp = line.split()
    if sp[0]=='v':
        v.append([float(sp[1]),float(sp[2]), float(sp[3])])
    if sp[0]=='f':
        sf1 =sp[1].split('/')
        sf2 = sp[2].split('/')
        sf3 = sp[3].split('/')
        f.append([int(sf1[0]),int(sf2[0]),int(sf3[0])])
#print(v)
#print(f)

for i in range(len(v)):
    y =floor(-10000*v[i][1])+1000
    x = floor(10000*v[i][0])+1000
    img_mat[y,x] =72,6,7

for i in range(len(f)):
    x0 = floor(10000*v[f[i][0]-1][0])+1000
    y0 = floor(-10000*v[f[i][0]-1][1])+1000
    x1 = floor(10000*v[f[i][1]-1][0])+1000
    y1 = floor(-10000*v[f[i][1]-1][1])+1000
    x2 = floor(10000*v[f[i][2]-1][0])+1000
    y2 = floor(-10000*v[f[i][2]-1][1])+1000
    img_mat = draw_line(img_mat,x0,y0,x1,y1)
    img_mat = draw_line(img_mat,x1,y1,x2,y2)
    img_mat = draw_line(img_mat,x2,y2,x0,y0)
img = Image.fromarray(img_mat)
img.save("img.png")