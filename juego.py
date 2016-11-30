import pygame
from compugrafica import *
'''
empaquetar programas linux
'''

def recortar(archivo,anchoc,altoc):
    imagen=pygame.image.load(archivo).convert_alpha()
    img_ancho,img_alto=imagen.get_size()
    tabla_fondos=[]
    for fondo_x in range(0,img_ancho/anchoc):
        linea=[]
        tabla_fondos.append(linea)
        for fondo_y in range (0,img_alto/altoc):
            cuadro=(fondo_x*anchoc,fondo_y*altoc,anchoc,altoc)
            linea.append(imagen.subsurface(cuadro))
    return tabla_fondos

class jugador(pygame.sprite.Sprite):
    velocidad=4
    ls_block=None
    ls_movil=None
    def __init__(self,sheet,x,y):
            pygame.sprite.Sprite.__init__(self)
            self.player_sheet=recortar(sheet,32,32)
            self.image= self.player_sheet[0][0]
            self.rect=self.image.get_rect()
            self.rect.x=x
            self.rect.y=y
            self.cambioy=0
            self.standing=False
            self.lock=True

    def move(self,dx,dy):
        if dx != 0:
            self.collide(dx, 0)
        if dy != 0:
            self.collide(0, dy)
    def collide(self,dx,dy):
        self.rect.x+=dx
        self.rect.y+=dy

        ls_golpes=pygame.sprite.spritecollide(self,self.ls_block,False)
        for g in ls_golpes:
            if dx>0:
                self.rect.right=g.rect.left
            if dx<0:
                self.rect.left=g.rect.right
            if dy>0:
                self.rect.bottom=g.rect.top
                self.cambioy=0
                self.standing=True
            '''if dy<0:
                self.rect.top=g.rect.bottom'''

        ls_golpes=pygame.sprite.spritecollide(self,self.ls_movil,False)
        for m in ls_golpes:
            self.lock=True   #bloquea colisiones laterales mientras se sube a una plataforma
            if dx>0 and self.lock:
                self.rect.right=m.rect.left-1
            elif dx<0and self.lock:
                self.rect.left=m.rect.right+1
            elif dy>0:
                if self.rect.y<m.rect.y:
                    self.rect.bottom=m.rect.top
                    self.standing=True
                    self.cambioy=0
                    self.rect.x+=m.mov_x
            if dy<0:
                self.lock=False



    def jump(self):
        self.cambioy=-8
    def gravity(self):
        if self.cambioy==0:
            self.cambioy=1
        else:
            self.cambioy+=0.35
    def update(self):
        if self.cambioy!=0:
            self.standing=False
        self.gravity()
        self.move(0,self.cambioy)



class  bloque(pygame.sprite.Sprite):
    def __init__(self, an,al,color):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface([al,an])
        self.image.fill(color)
        self.rect=self.image.get_rect()

class  bloqueMovil(bloque):
    def __init__(self, an,al,px,py,color):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.Surface([an,al])
        self.image.fill(color)
        self.rect=self.image.get_rect()
        self.mov_x=3
        self.rango=100
        self.px=px
        self.rect.x=px
        self.rect.y=py
    def update(self):
        if self.rect.x - self.px>=self.rango or self.rect.x - self.px<=-1*self.rango:
            self.mov_x=self.mov_x*-1
        self.rect.x+=self.mov_x


if __name__=="__main__":

    pygame.init()
    pantalla= pygame.display.set_mode([ANCHO,ALTO])

    todos=pygame.sprite.Group()
    blocks=pygame.sprite.Group()
    moviles=pygame.sprite.Group()

    jp= jugador("image/Vlad.png",300,300)

    bloque1=bloque(10,400,ROJO)
    bloque1.rect.y=550
    bloque1.rect.x=10
    todos.add(bloque1)
    blocks.add(bloque1)

    bloque2=bloque(100,40,ROJO)
    bloque2.rect.y=450
    bloque2.rect.x=100
    todos.add(bloque2)
    blocks.add(bloque2)

    bloque3=bloqueMovil(300,250,400,390,ROJO)
    todos.add(bloque3)
    moviles.add(bloque3)

    jp.ls_block=blocks
    jp.ls_movil=moviles
    todos.add(jp)

    reloj=pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                jp.rect.y=300
                jp.rect.x=300
            if event.key==pygame.K_SPACE:
                jp.jump()
            if event.key==pygame.K_F11:
                pygame.display.toggle_fullscreen()

    key = pygame.key.get_pressed()

    if key[pygame.K_a]:
        jp.image=jp.player_sheet[1][1]
        jp.move(-jp.velocidad, 0)

    if key[pygame.K_d]:
        jp.image=jp.player_sheet[0][1]
        jp.move(jp.velocidad, 0)

    pantalla.fill(NEGRO)
    todos.draw(pantalla)
    todos.update()
    pygame.display.flip()
    reloj.tick(60)
