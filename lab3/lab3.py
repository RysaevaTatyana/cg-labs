from numba import njit
from math import ceil,floor
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
@njit
def baricentric_coordinates(x,y, x0, y0, x1 , y1,  x2,  y2):
    denom = (x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)
    if denom==0: 
        return 0,0,0, True
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2))/denom
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) /denom
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2, False
@njit
def draw_triangle(x0, y0,z0, x1, y1,z1, x2,y2, z2, a,b,c,img_mat, z_buffer):  
    xmin = floor(min(x0,min(x1,x2))) if min(x0,min(x1,x2))>=0 else 0 
    ymin = floor(min(y0,min(y1,y2))) if min(y0,min(y1,y2))>=0 else 0
    xmax = ceil(max(x0,max(x1,x2))) if max(x0,max(x1,x2))<=img_mat.shape[1]-1 else img_mat.shape[1]-1
    ymax = ceil(max(y0,max(y1,y2))) if max(y0,max(y1,y2))<=img_mat.shape[0]-1 else img_mat.shape[0]-1
    for x in range(xmin, xmax+1):
        for y in range(ymin, ymax+1):
            lambda0, lambda1, lambda2, flag  = baricentric_coordinates(x,y,x0,y0, x1,y1,x2,y2)
            if flag:
                return
            if lambda0>=0 and lambda1>=0 and lambda2>=0:
                z = lambda0*z0+lambda1*z1+lambda2*z2
                if(z>z_buffer[y,x]):
                    continue
                if(z<z_buffer[y,x]):
                   
                    img_mat[y, x, 0] = a
                    img_mat[y, x, 1] = b
                    img_mat[y, x, 2] = c
                    z_buffer[y,x] = z
@njit                    
def render_model(f,v, SCALE, z_buffer,  img_mat, C_X, C_Y):
    for i in range(len(f)):
        x0 = v[f[i][0]][0]
        y0 = v[f[i][0]][1]
        z0 = v[f[i][0]][2]

        x1 = v[f[i][1]][0]
        y1 = v[f[i][1]][1]
        z1 = v[f[i][1]][2]

        x2 = v[f[i][2]][0]
        y2 = v[f[i][2]][1]
        z2 = v[f[i][2]][2]

        px0 = x0*SCALE+C_X
        py0 = -y0*SCALE+C_Y
        px1 = x1*SCALE+C_X
        py1 = -y1*SCALE+C_Y
        px2 = x2*SCALE+C_X
        py2 = -y2*SCALE+C_Y

        ax, ay, az = x1-x2,y1-y2,z1-z2
        bx, by, bz = x1-x0,y1-y0,z1-z0
        lx, ly, lz=0,0,1
        nx = ay*bz-az*by
        ny = -(ax*bz-az*bx)
        nz = ax*by-ay*bx
        if np.sqrt(nx**2+ny**2+nz**2)==0:
            continue
        cos = (nx*lx+ny*ly+nz*lz)/(np.sqrt(nx**2+ny**2+nz**2)*np.sqrt(lx**2+ly**2+lz**2))
        
        if cos<0:
            intensity = int(-255*cos)
            draw_triangle(px0,py0,z0,px1,py1,z1,px2,py2,z2, intensity, 0, 0, img_mat, z_buffer)
class Scene:
    def __init__(self, file_name):
        self.v = []
        self.f = []
        file = open(file_name)
        for line in file:
            sp = line.split()
            if sp[0]=='v':
                self.v.append([float(sp[1]),float(sp[2]), float(sp[3])])
            if sp[0]=='f':
                sf1 =sp[1].split('/')
                sf2 = sp[2].split('/')
                sf3 = sp[3].split('/')
                self.f.append([int(sf1[0])-1,int(sf2[0])-1,int(sf3[0])-1])
        self.v = np.array(self.v)   
        self.f = np.array(self.f)        
class Renderer:
    def __init__(self, H,W, SCALE):
        self. H = H
        self.W = W
        self.C_X = H/2
        self.C_Y = W/2
        self.SCALE = SCALE
        self.img_mat = np.zeros((self.H,self.W,3), dtype = np.uint8)
        self.z_buffer= np.full((self.H,self.W), float('inf'))
    def render(self, scene):
        self.img_mat.fill(0)
        self.z_buffer.fill(np.inf)
        render_model(scene.f,scene.v, self. SCALE, self.z_buffer, self. img_mat, self.C_X, self.C_Y )

class App:
    def __init__(self, scene, renderer, win_w = 900, win_h = 900):
        self.scene = scene
        self.renderer = renderer

        # Окно верхнего уровня
        self.root = tk.Tk()
        # Размеры окна
        self.root.geometry(f"{win_w}x{win_h}")
        # Область для рисования внутри окна
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.focus_set()
        # Обновление изображения при изменении размеров окна
        self.canvas.bind('<Configure>', lambda e: self._refit())
        # Привязка обработчика клавиш
        self.root.bind('<Key>', self.on_key)

        # Изображение внутри окна
        self.photo = None
        self.full_image = None

        self.render()

    def on_key(self, event):
        k = event.keysym

        if k == '1':
            self.renderer.SCALE *= 1.1
        elif k == '2':
            self.renderer.SCALE *=0.9
        
        elif k == 'space':
            Image.fromarray(self.renderer.img_mat).save('img.png')
            return 'break'
        else:
            return

        self.render()
        # Не обрабатываем дальше – return 'break'
        return 'break'

    def render(self):
        self.renderer.render(self.scene)
        self.full_image = Image.fromarray(self.renderer.img_mat)
        self._refit()

    def _refit(self):
        # Если ещё не отрендерилось, пропускаем
        if self.full_image is None: return
        # Ширина и высота области для рисования
        ww = self.canvas.winfo_width()
        wh = self.canvas.winfo_height()
        # Если вдруг сделали область слишком маленькой
        if ww < 10 or wh < 10: return
        # Вписать с сохранением пропорций
        s = min(ww / self.renderer.W, wh / self.renderer.H)
        dw = max(1, int(self.renderer.W * s))
        dh = max(1, int(self.renderer.H * s))
        disp = self.full_image.resize((dw, dh), Image.BILINEAR)
        # Очень важно сохранить ImageTk.PhotoImage(disp) в поле класса
        # Если оно будет локальным, то удалится после выхода сборщиком мусора
        self.photo = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(ww // 2, wh // 2, image=self.photo)   

    # скопировать как есть
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    scene = Scene("model.obj")
    renderer = Renderer(1000, 1000, 5000.0)
    App(scene, renderer, 500, 500).run()
    