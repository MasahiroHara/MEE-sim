# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 16:45:03 2018

@author: KNDLA
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 13:48:42 2018

@author: KNDLA
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from numba.decorators import jit
from multiprocessing import Pool
import pandas as pd

X=6900 #1周期分とする
Y=14   #1段すなわちGaAs一層分が14セル
Z=6    #1セルでAl/Ga一層、更に1セルでAs一層にしたいけどとりあえずはGaAs一層で1セル
Cell_sum=X*Y

@jit
def fun(n):
    area=np.empty((X,Y,Z),dtype=np.int)
    for i in range(X):
        for j in range(Y):
            for k in range(Z):
                area[i][j][k]=0
    r=1
    while r<Cell_sum+1:
      supply(area,r)
      fix(area)
      move(area)
      print(str(r))
      r_100=r*100.0
      if r_100/Cell_sum%10.0==0: #被覆率10%毎に保存
          p=r_100/Cell_sum
          draw(area,n,p)
          count(area,n,p)
      r+=1
    
    
    
@jit     
def wrap(array,x,y,z):
    #空間の連結を関数化して[x][y]が周期境界条件を満たすようにする。arrayは三次元
    if x<0:     #空間の水平方向の端を連結
        x+=X
    elif x>X-1:
        x-=X
    if y<0:     #空間の段差を下に落ちることはできる
        y+=Y                    
    elif y>Y-1:   #空間の端の段差を上に乗り越えはしないようにする
        y=Y-1
    return array[x][y][z]

#z方向は特に処理いらん？


@jit
def wrap_index(array,x,y,z):  #indexを返す。arrayは三次元
    if x<0:
        x+=X
    elif x>X-1:
        x-=X
    if y<0:
        y+=Y                    
    elif y>Y-1:   #段差を上に乗り越えはしないようにする
        y=Y-1
    return x,y,z


@jit
def fix(array):
    x=0
    z=0
    while z<Z:
        while x<X:
            y=0
            if x<X/2:   #非反転層
                while y<Y:
                    if y<Y-1:
                        if wrap(array,x,y)==1 or wrap(array,x,y)==2:
                            if wrap(array,x,y+1)==3 or wrap(array,x,y+1)==4 or wrap(array,x,y-1)==3 or wrap(array,x,y-1)==4:
                                array[wrap_index(array,x,y)[0]][wrap_index(array,x,y)[1]]+=2
                                
                    elif y==Y-1:   
                        if wrap(array,x,Y-1)==1 or wrap(array,x,Y-1)==2:
                            array[wrap_index(array,x,Y-1)[0]][wrap_index(array,x,Y-1)[1]]+=2
                            print("fixed")
                    y+=1
                
                
            
            else:   #反転層
                while y<Y:
                    if wrap(array,x,y)==1 or wrap(array,x,y)==2:
                        if wrap(array,x+1,y)==3 or wrap(array,x+1,y)==4 or wrap(array,x-1,y)==3 or wrap(array,x-1,y)==4:
                            array[wrap_index(array,x,y)[0]][wrap_index(array,x,y)[1]]+=2                
                    y+=1
                
            x+=1
        z+=1
        
        
@jit        
def move(array):
    newarray=np.empty((X,Y,Z),dtype=np.int)
    x=0
    y=0
    z=0
    while z<Z:
        while x<X:
            while y<Y:
                direction=np.empty((8,1),dtype=np.int)
#direction[0]:X方向+1 direction[1]:X方向+2 direction[2]:X方向-1 direction[3]:X方向-2 direction[4]:Y方向+1 direction[5]:Y方向+2 direction[6]:Y方向-1 direction[7]:Y方向+2
                for i in range(8):
                    direction[i]=0
        
                if wrap(array,x,y,z)==1:  #Ga原子に対しての処理
                    if wrap(array,x+1,y,z)==0:
                        direction[0]=1
                        if wrap(array,x+2,y,z)==0:
                            direction[1]=2
                    if wrap(array,x-1,y,z)==0:
                        direction[2]==-1
                        if wrap(array,x-2,y,z)==0:
                            direction[3]==-2
                    if wrap(array,x,y+1,z)==0:
                        direction[4]==1
                        if wrap(array,x,y+2,z)==0:
                            direction[5]==2
                    if wrap(array,x,y-1,z)==0:
                        direction[6]==-1
                        if wrap(array,x,y-2,z)==0:
                            direction[7]==-2
                                   
                    if x<X/2:   #非反転層
                        index=[0,1,2,3,4,4,5,5,6,6,7,7]
                        n=np.random.choice(index) #選ばれる確率を調整
                        if n==0 or n==1 or n==2 or n==3:
                            newarray[wrap_index(newarray,x,y,z)[0]][wrap_index(newarray,x,y,z)[1]]=0
                            newarray[wrap_index(newarray,x+direction[n],y,z)[0]][wrap_index(newarray,x+direction[n],y,z)[1]]=wrap(array,x,y,z)                            
                            
                        elif n==4 or n==5 or n==6 or n==7:
                            newarray[wrap_index(newarray,x,y,z)[0]][wrap_index(newarray,x,y,z)[1]]=0
                            newarray[wrap_index(newarray,x,y+direction[n],z)[0]][wrap_index(newarray,x,y+direction[n],z)[1]]=wrap(array,x,y,z)
                
                    elif X/2-1<x:   #反転層
                        index=[0,0,1,1,2,2,3,4,5,6,7]
                        n=np.random.choice(index)   #選ばれる確率を調整
                        if n==0 or n==1 or n==2 or n==3:
                            newarray[wrap_index(newarray,x,y,z)[0]][wrap_index(newarray,x,y,z)[1]]=0
                            newarray[wrap_index(newarray,x+direction[n],y,z)[0]][wrap_index(newarray,x+direction[n],y,z)[1]]=wrap(array,x,y,z)
                        elif n==4 or n==5 or n==6 or n==7:
                            newarray[wrap_index(newarray,x,y)[0]][wrap_index(newarray,x,y)[1]]=0
                            newarray[wrap_index(newarray,x,y+direction[n],z)[0]][wrap_index(newarray,x,y+direction[n],z)[1]]=wrap(array,x,y,z)
                
                elif wrap(array,x,y,z)==2:    #Al原子に対しての処理
                    if wrap(array,x+1,y,z)==0:
                        direction[0]=1
                    if wrap(array,x-1,y,z)==0:
                        direction[2]==-1
                    if wrap(array,x,y+1,z)==0:
                        direction[4]==1
                    if wrap(array,x,y-1,z)==0:
                        direction[6]==-1
                    #[1],[3],[5],[7]は全て0のまま→動かない
                
                    if x<X/2:   #非反転層
                        index=[0,2,4,4,6,6]
                        n=np.random.choice(index) #選ばれる確率を調整
                        if n==0 or n==1 or n==2 or n==3:
                            newarray[wrap_index(newarray,x,y,z)[0]][wrap_index(newarray,x,y,z)[1]]=0
                            newarray[wrap_index(newarray,x+direction[n],y,z)[0]][wrap_index(newarray,x+direction[n],y,z)[1]]=wrap(array,x,y,z)
                        elif n==4 or n==5 or n==6 or n==7:
                            newarray[wrap_index(newarray,x,y,z)[0]][wrap_index(newarray,x,y,z)[1]]=0
                            newarray[wrap_index(newarray,x,y+direction[n],z)[0]][wrap_index(newarray,x,y+direction[n],z)[1]]=wrap(array,x,y,z)
                
                    elif X/2-1<x:   #反転層
                        index=[0,0,2,2,4,6]
                        n=np.random.choice(0,0,2,2,4,6)   #選ばれる確率を調整
                        if n==0 or n==1 or n==2 or n==3:
                            newarray[wrap_index(newarray,x,y,z)[0]][wrap_index(newarray,x,y,z)[1]]=0
                            newarray[wrap_index(newarray,x+direction[n],y,z)[0]][wrap_index(newarray,x+direction[n],y,z)[1]]=wrap(array,x,y,z)
                        elif n==4 or n==5 or n==6 or n==7:
                            newarray[wrap_index(newarray,x,y,z)[0]][wrap_index(newarray,x,y,z)[1]]=0
                            newarray[wrap_index(newarray,x,y+direction[n],z)[0]][wrap_index(newarray,x,y+direction[n],z)[1]]=wrap(array,x,y,z)
                        
                array=np.copy(newarray)
                y+=1
            x+=1
        z+=1
        
        
@jit    
def supply(array,r):  #乱数で座標を指定して、一個供給するまで試行する
    if r<2500:    #始めに一定量の固定Ga/Alを撒く
        n=0
        while n==0:
            x=np.random.randint(0,X)
            y=np.random.randint(0,Y)
            z=np.random.randint(0,Z)
            if z==0:
                if array[x][y][z]==0:
                    array[x][y][z]=np.random.randint(3,5)
                    n+=1
            elif array[x][y][z-1]!=0:
                if array[x][y][z]==0:
                    array[x][y][z]=np.random.randint(3,5)
                    n+=1
            else:
                continue
            
    else:
        n=0
        while n==0:
            x=np.random.randint(0,X)
            y=np.random.randint(0,Y)
            z=np.random.randint(0,Z)
            if z==0:
                if array[x][y][z]==0:
                    array[x][y][z]=np.random.randint(1,3)
                    n+=1
            elif array[x][y][z-1]!=0:   #一個下の層が0のときは再試行
                if array[x][y][z]==0:
                    array[x][y][z]=np.random.randint(1,3)
                    n+=1
            else:
                continue
            
            
@jit        
def count(array,n,p):
    Ga_sum_yzaxis=np.empty((X),dtype=np.int)
    for k in range(X):
        Ga_sum_yzaxis[k]=0
    
    for i in range(X):
        for j in range(Y):
            for k in range(Z):
                if array[i][j][k]==3 or array[i][j][k]==1:
                    Ga_sum_yzaxis[i]+=1
                else:
                    continue
    plt.plot(Ga_sum_yzaxis[6850:6950])
    plt.savefig("figure_Ga_composition"+str(n)+str(int(p))+"percent.png")
    plt.close()
    
    sum=0
    for i in range(X):
        sum+=Ga_sum_yzaxis[i]
    s = pd.Series(Ga_sum_yzaxis)
    s.to_csv("output"+str(n)+"-"+str(int(p))+"percent.csv",header=False, index=False)
    print(str(sum)+","+str(n)+"times tried")
    
    
@jit 
def draw(array,r,p):
    img = Image.new("RGB", (X, Y), (255,255,255))
    draw = ImageDraw.Draw(img)
    for z in range(Z):
        for y in range(Y):
            for x in range(X//2):
                if array[x][y][z]==3:    #固定Ga
                    draw.point((x,y,z),(51,0,255))
                elif array[x][y][z]==4:  #固定Al
                    draw.point((x,y,z),(51,204,255))
                elif array[x][y][z]==1:    #遊離Ga
                    draw.point((x,y,z),(255,0,51))
                elif array[x][y][z]==2:    #遊離Al
                    draw.point((x,y,z),(255,204,51))
            for x in range(X//2,X):
                if array[x][y][z]==3:    #固定Ga
                    draw.point((x,y,z),(51,0,255))
                elif array[x][y][z]==4:  #固定Al
                    draw.point((x,y,z),(51,204,255))
                elif array[x][y][z]==1:
                    draw.point((x,y,z),(255,0,51))
                elif array[x][y][z]==2:
                    draw.point((x,y,z),(255,204,51))
            img.save(str(r)+"try,z="+str(z)+str(int(p))+"percent.png","PNG")
       
    
if __name__ == '__main__':
    with Pool(1) as p:
        p.map(fun, range(1,1001))
        p.close()