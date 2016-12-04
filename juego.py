import pygame
from compugrafica import *
import json
from pygame.locals import *
'''
empaquetar programas linux
'''

def RelRect(actor, camara):
    return pygame.Rect(actor.rect.x-camara.rect.x, actor.rect.y-camara.rect.y, actor.rect.w, actor.rect.h)

class Camara(object): #clase camara

    def __init__(self, pantalla, jugador, anchoNivel, largoNivel):
        self.jugador = jugador
        self.rect = pantalla.get_rect()
        self.rect.center = self.jugador.center
        self.mundo_rect = Rect(0, 0, anchoNivel, largoNivel)

    def actualizar(self):
      if self.jugador.centerx > self.rect.centerx + 25:
          self.rect.centerx = self.jugador.centerx - 25

      if self.jugador.centerx < self.rect.centerx - 25:
          self.rect.centerx = self.jugador.centerx + 25

      if self.jugador.centery > self.rect.centery + 25:
          self.rect.centery = self.jugador.centery - 25

      if self.jugador.centery < self.rect.centery - 25:
          self.rect.centery = self.jugador.centery + 25
      self.rect.clamp_ip(self.mundo_rect)

    def dibujarSprites(self, pantalla, sprites):
        for s in sprites:
            if s.rect.colliderect(self.rect):
                pantalla.blit(s.image, RelRect(s, self))


class mapa(object):
    jp=None
    def __init__(self,archivo):
        with open(archivo) as js_ar:
            self.base=json.load(js_ar)

        self.lm=[]

        for l in self.base['layers']:
            if l['name']=='muro':
                self.lm=l['data']

        self.ancho_fondo=self.base['width']
        self.alto_fondo=self.base['height']
        self.mapa=self.Separar(self.lm, self.ancho_fondo)
        self.ancho_tile=self.base["tilewidth"]
        self.alto_tile=self.base["tileheight"]
        self.tile_list=self.listarTiles()

    def listarTiles(self):
        lin=[]
        for l in self.base['tilesets']:
            nom_arc=l['image']
            al_c=l['tileheight']
            an_c=l['tilewidth']
            lin_r=self.Recortar(nom_arc, an_c, al_c)
            for temp in lin_r:
                lin.append(temp)
        return lin

    def analizarMapa(self,blocks,todos):
        xy=0
        for f in self.mapa:
            #xp=jp.rect.x-ANCHO
            xp=0
            for c in f:
                if c!=0:
                    cuadro=self.tile_list[c-1]
                    b=bloque(cuadro,xp,xy)
                    blocks.add(b)
                    todos.add(b)
                    #pantalla.blit(cuadro,[xp,xy])
                xp+=self.ancho_tile
            xy+=self.alto_tile

    def Separar(self,l, ancho):
        con=0
        matriz=[]
        linea=[]
        for i in l:
            linea.append(i)
            con+=1
            if con==ancho:
                matriz.append(linea)
                linea=[]
                con=0
        return matriz

    def Recortar(self,archivo, anc, alc):
        linea=[]
        imagen=pygame.image.load(archivo).convert_alpha()
        i_ancho, i_alto=imagen.get_size()
        #print i_ancho, ' ', i_alto
        for y in range(0, i_alto/alc):
            for x in range(0,i_ancho/anc):
                cuadro=(x*anc, y*alc, anc, alc)
                linea.append(imagen.subsurface(cuadro))
        return linea





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
            elif dx<0 and self.lock:
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
    def __init__(self, imagen,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=imagen
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class  bloqueMovil(pygame.sprite.Sprite):
    def __init__(self, imagen,x,y,px):
        pygame.sprite.Sprite.__init__(self)
        self.image=imagen
        self.rect=self.image.get_rect()
        self.mov_x=3
        self.rango=100
        self.px=px
        self.rect.x=x
        self.rect.y=y
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

    jp= jugador("image/Vlad.png",100,300)

    mapa1=mapa("mapa1.json")
    mapa1.jp=jp
    mapa1.analizarMapa(blocks,todos)

    jp.ls_block=blocks
    jp.ls_movil=moviles
    todos.add(jp)
    camara = Camara(pantalla, jp.rect,mapa1.ancho_fondo*mapa1.ancho_tile,mapa1.alto_fondo*mapa1.alto_tile)

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
        camara.dibujarSprites(pantalla, todos)
        camara.actualizar()
        todos.update()
        pantalla.blit(mapa1.tile_list[1006], [0,0])
        pygame.display.flip()
        reloj.tick(60)
