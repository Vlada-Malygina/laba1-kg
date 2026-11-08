import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from math import floor
from math import ceil
from random import randint
from numba import njit



class Scene:
     def __init__(self, filename):
          self.v = []
          self.f = []
          file=open(filename)
          for s in file:
               sp=s.split()
               if (sp[0]=='v'):
                    self.v.append([float(sp[1]),float(sp[2]),float(sp[3])])
               if (sp[0]=='f'):
                         sf1=sp[1].split('/')
                         sf2=sp[2].split('/')
                         sf3=sp[3].split('/')
                         self.f.append([int(sf1[0])-1,int(sf2[0])-1,int(sf3[0])-1])
          self.v=np.array(self.v)
          self.f=np.array(self.f)
class Renderer:
     def __init__(self, W, H, scale,r,g,b):
        self.H = H
        self.W = W
        self.scale = scale
        self.cx = self.W / 2.0
        self.cy = self.H / 2.0
        self.color = np.array([r,g,b])
        self.img_mat  = np.zeros((H, W, 3), dtype=np.uint8)
        self.z_b = np.full((H, W), np.inf, dtype=np.float32)
     def render(self,scene):
          self.img_mat[...]=0
          self.z_b[...] = np.inf
          render_model(scene.f, scene.v, self.scale, self.z_b, self.img_mat, self.cx, self.cy, self.H, self.W, self.color)

@njit
def baricentr(x,y,x0,y0,x1,y1,x2,y2):
     lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
     lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
     lambda2 = 1.0 - lambda0 - lambda1
     return lambda0, lambda1, lambda2

@njit
def triangle(x0,y0,z0,x1,y1,z1,x2,y2,z2,a,b,c,z_b,img_mat,H,W):
     xmin=floor(min(x0, min(x1,x2))) if (min(x0,min(x1,x2)) >=0) else 0
     xmax=ceil(max(x0,max(x1,x2))) if (max(x0,max(x1,x2)) <=W) else W
     ymin=floor(min(y0,min(y1,y2))) if (min(y0,min(y1,y2)) >=0) else 0
     ymax=ceil(max(y0,max(y1,y2))) if (max(y0,max(y1,y2)) <=H) else H
     if((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2) == 0): return
     for x in range(xmin, xmax+1):
          for y in range(ymin, ymax+1):
                lambda0,lambda1,lambda2=baricentr(x,y,x0,y0,x1,y1,x2,y2)
                if (lambda0>=0 and lambda1>=0 and lambda2>=0):
                     z=lambda0*z0+lambda1*z1+lambda2*z2
                     if (z<z_b[y,x]): 
                          z_b[y,x]=z
                          img_mat[y,x]=a,b,c

@njit
def render_model(f, v, scale, z_b, img_mat, cx, cy, H, W, color):
     for i in range(len(f)):
          x0=(v[f[i][0]][0])
          y0=(v[f[i][0]][1])
          z0=(v[f[i][0]][2])

          x1=(v[f[i][1]][0])
          y1=(v[f[i][1]][1])
          z1=(v[f[i][1]][2])

          x2=(v[f[i][2]][0])
          y2=(v[f[i][2]][1])
          z2=(v[f[i][2]][2])

          px0=x0*scale+cx
          py0=y0*-scale+cy

          px1=x1*scale+cx
          py1=y1*-scale+cy

          px2=x2*scale+cx
          py2=y2*-scale+cy
     

          a=np.array([x1-x2,y1-y2,z1-z2])
          b=np.array([x1-x0,y1-y0,z1-z0])
          l=np.array([0,0,1])
          normal = np.array([0.0,0.0,0.0])
          normal[0]=a[1]*b[2] - a[2]*b[1]
          normal[1]=a[0]*b[2] - a[2]*b[0]
          normal[2]=a[0]*b[1] - a[1]*b[0]

          cos=normal[2] /np.sqrt(normal[0]*normal[0]+normal[1]*normal[1]+normal[2]*normal[2])
          if (cos<0):
               triangle(px0,py0,z0,px1,py1,z1,px2,py2,z2,-color[0]*cos,-color[1]*cos,-color[2]*cos, z_b,img_mat,H,W)
  
class App:
     def __init__(self, scene, renderer, win_w = 900, win_h = 900):
          self.scene = scene
          self.renderer = renderer

          # Оставляем как есть
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

          if k == 'plus':
               self.renderer.scale *= 1.1
          elif k == 'minus':
               self.renderer.scale /= 1.1
          elif k=='1':
               self.renderer.color[0]-=10
          elif k=='2':
               self.renderer.color[0]+=10
          elif k == 'space':
               Image.fromarray(self.renderer.img_mat).save('img.png')
               return 'break'
          else:
               return

          self.render()
          # Не обрабатываем дальше – return 'brake'
          return 'break'

     def render(self):
          self.renderer.render(self.scene)
          self.full_image = Image.fromarray(self.renderer.img_mat)
          self._refit()

     # скопировать как есть
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
    scene = Scene('model.obj')
    renderer = Renderer(2000, 2000, 10000.0, 60,198,141)
    App(scene, renderer, 1000, 1000).run()