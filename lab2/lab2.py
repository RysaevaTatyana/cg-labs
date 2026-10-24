from math import ceil,floor
import numpy as np
import PIL.Image as Image
img_mat = np.zeros((2000,2000,3), dtype = np.uint8)
z_buffer= np.full((2000,2000), float('inf'))
def baricentric_coordinates(x,y, x0, y0, x1 , y1,  x2,  y2):
    denom = (x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2))/denom
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) /denom
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2
def draw_triangle(x0, y0,z0, x1, y1,z1, x2,y2, z2, a,b,c, z_buffer):
    xmin = floor(min(x0,x1,x2)) if min(x0,x1,x2)>=0 else 0 
    ymin = floor(min(y0,y1,y2)) if min(y0,y1,y2)>=0 else 0
    xmax = ceil(max(x0,x1,x2)) if max(x0,x1,x2)<=2000 else 2000
    ymax = ceil(max(y0,y1,y2)) if max(y0,y1,y2)<=2000 else 2000
    if (x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)==0:
        return
    for x in range(xmin, xmax+1):
        for y in range(ymin, ymax+1):
            lambda0, lambda1, lambda2 = baricentric_coordinates(x,y,x0,y0, x1,y1,x2,y2)
            if lambda0>=0 and lambda1>=0 and lambda2>=0:
                z = lambda0*z0+lambda1*z1+lambda2*z2
                if(z>z_buffer[y,x]):
                    continue
                if(z<z_buffer[y,x]):
                    img_mat[y,x] = a,b,c
                    z_buffer[y,x] = z

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

for i in range(len(f)):
    x0 = (10000*v[f[i][0]-1][0])+1000
    y0 = (-10000*v[f[i][0]-1][1])+1000
    z0 = (10000*v[f[i][0]-1][2])+1000

    x1 = (10000*v[f[i][1]-1][0])+1000
    y1 = (-10000*v[f[i][1]-1][1])+1000
    z1 = (10000*v[f[i][1]-1][2])+1000

    x2 = (10000*v[f[i][2]-1][0])+1000
    y2 = (-10000*v[f[i][2]-1][1])+1000
    z2 = (10000*v[f[i][2]-1][2])+1000

    a = np.array([x1-x2,y1-y2,z1-z2])
    b = np.array([x1-x0,y1-y0,z1-z0])
    l = np.array([0,0,1])
    normal = -np.cross(a,b)
    cos = np.dot(normal, l)/(np.linalg.norm(normal)*np.linalg.norm(l))
    if cos<0:
        draw_triangle(x0,y0,z0,x1,y1,z1,x2,y2,z2, -255*cos, 0, 0, z_buffer)
img = Image.fromarray(img_mat)
img.save("img.png")
