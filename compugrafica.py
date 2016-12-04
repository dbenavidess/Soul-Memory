import pygame
import math
import random
ALTO=1024
ANCHO=1024
BLANCO=(255,255,255)
ROJO=(255,0,0)
GRIS=(30,30,30)
UNO=(100,100,50)
AZUL=(0,0,255)
ALGO=(0,255,0)
NEGRO=(0,0,0)

def plano(p,centro):
    infop= p.get_rect()
    pini=(0,centro[1])
    pfin=(infop[2],centro[1])
    pygame.draw.line(p,UNO,pini,pfin,2)
    pini=(centro[0],0)
    pfin=(centro[0],infop[3])
    pygame.draw.line(p,UNO,pini,pfin,2)
def vector(a,b):
    return (b[0]-a[0],b[1]-a[1])    #hace el vector entre 2 puntos
def dibujarVector(p,v):
    pygame.draw.line(p,AZUL,v,(p.get_rect()[2]/2,p.get_rect()[3]/2))
def norma(a):
    return math.sqrt(a[0]**2 + a[1]**2)
def dist2p(a,b):
    v=vector(a,b)
    return norma(v)
def VectorOpuesto(a):
    return(a[0]*-1,a[1]*-1)
def ProductoPunto(a,b):
    return a[0]*b[0]+a[1]*b[1]
def Angulo2Vectores(a,b):
    n=math.fabs(ProductoPunto(a,b))
    d= norma(a) * norma(b)
    r=math.acos(n/d)
    return math.degrees(r)
def vectorIgual(a,b):
    i=a[0]/b[0]
    j=a[1]/b[1]
    return i==j
def ecuacionParam1(p,v):
    print "x = " , p[0] , " + K" , v[0] , "\n" , "y = " , p[1] , " + K" , v[1]
def ecuacionParam2(a,b):
    v=vector(a,b)
    ecuacionParam1(a,v)
def printpuntos(p,l,color):
    for e in l:
        entero=(int (e[0]),int (e[1]))
        p.set_at(entero,NEGRO)
        pygame.draw.circle(p,color,entero,5,1)
    pygame.display.flip()
def transformacion(centro,p):
    x=p[0]+centro[0]
    y=centro[1]-p[1]
    return (x,y)
def transList(centro,lista):
    new=[]
    for e in lista:
        r=transformacion(centro,e)
        new.append(r)
    return new
def puntos (n):
    l=[]

    con=0
    while con < n:
        x=random.randrange(550,700)
        y=random.randrange(64,700)
        valor=(x,y)
        l.append(valor)
        con+=1
    return l
def destransformar(centro,p):
    x=p[0]-centro[0]
    y=centro[1]-p[1]
    return (x,y)
def escalamiento(p,m):
    x=p[0]*m[0]
    y=p[1]*m[1]
    return (x,y)
def escalamientoList(p,m):
    r=[]
    for e in p:
        a=escalamiento(e,m)
        r.append(a)
    return r
def rotacion(p,a):
    x=p[0]*math.cos(a)-p[1]*math.sin(a)
    y=p[0]*math.sin(a)+p[1]*math.cos(a)
    return (x,y)
def rotacionList(p,a):
    r=[]
    for e in p:
        n=rotacion(e,a)
        r.append(n)
    return r
def escalamientoFijo(l,p,m):
    t=[]
    for e in l:
        a=(e[0]*m[0]-p[0] , e[1]*m[1]-p[1])
        t.append(a)
    return t
def poligonoRegular(r,n):
    a=360/n
    l=[]
    cont=0
    while cont<360:
        x=r * math.cos(math.radians(cont))
        y=r * math.sin(math.radians(cont))
        cont=cont+a
        l.append((x,y))
    return l
def determinantes2(m):
    return m[0][0]*m[1][1]-m[0][1]*m[1][0]
def area2vectores(a,b):
    l=[a,b]
    return determinantes2(l)

def rotacionFija (l,p,a):
    c=[]
    for e in l:
        b=(e[0]-p[0],e[1]-p[1])
        c.append(b)
    cr=rotacionList(c,a)
    c=[]
    for er in cr:
        a=(er[0]+p[0],er[1]+p[1])
        c.append(a)
    return c


def SatanStar(r):
    a=0
    l=[]
    while a<360:
        x=r * math.cos(math.radians(a))
        y=r * math.sin(math.radians(a))
        a=a+72
        l.append((x,y))
    re=[l[0],l[2],l[4],l[1],l[3]]
    return re
