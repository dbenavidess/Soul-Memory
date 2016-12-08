import pygame
from compugrafica import *
import json
from pygame.locals import *
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
    def __init__(self,archivo):
        with open(archivo) as js_ar:
            self.base=json.load(js_ar)

        self.lm=[]

        for l in self.base['layers']:
            if l['name']=='muros':
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
            xp=0
            for c in f:
                if c!=0:
                    cuadro=self.tile_list[c-1]
                    b=bloque(cuadro,xp,xy)
                    blocks.add(b)
                    todos.add(b)
                    pantalla.blit(cuadro,[xp,xy])
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

class jugador(pygame.sprite.Sprite):
    velocidad=4
    ls_block=None
    ls_movil=None
    ls_enemigos=None
    ls_plataforma=None
    ls_plataforma_p=None
    ls_enemigos=None
    ls_mods=None
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
            self.HP=3
            self.down=False
            self.inmune=False
            self.inmune_cd=1000
            self.inmune_last=pygame.time.get_ticks()
            self.down_last=0
            self.down_cd=200

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
            if dy<0:
                self.rect.top=g.rect.bottom

        ls_golpes=pygame.sprite.spritecollide(self,self.ls_movil,False)
        for m in ls_golpes:
            self.lock=True   #bloquea colisiones laterales mientras se sube a una plataforma
            if dy<0:
                self.lock=False
            if dy>0 and not self.down:
                if self.rect.y<m.rect.y:
                    self.rect.bottom=m.rect.top
                    self.standing=True
                    self.cambioy=0
                    self.rect.x+=m.mov_x


        ls_golpes=pygame.sprite.spritecollide(self,self.ls_plataforma,False)
        for m in ls_golpes:
            self.lock=True   #bloquea colisiones laterales mientras se sube a una plataforma
            if dy<1:
                self.lock=False
            if dx>0 and self.lock:
                self.rect.right=m.rect.left-1
            if dx<0 and self.lock:
                self.rect.left=m.rect.right+1
            if dy>0 and not self.down:
                if self.rect.y<m.rect.y:
                    self.rect.bottom=m.rect.top
                    self.cambioy=0
                    self.standing=True

        ls_golpes=pygame.sprite.spritecollide(self,self.ls_plataforma_p,False)
        for m in ls_golpes:
            self.lock=True   #bloquea colisiones laterales mientras se sube a una plataforma
            if dy<1:
                self.lock=False
            if dx>0 and self.lock:
                self.rect.right=m.rect.left-1
            if dx<0 and self.lock:
                self.rect.left=m.rect.right+1
            if dy>0 and not self.down:
                if self.rect.y<m.rect.y:
                    self.rect.bottom=m.rect.top
                    self.cambioy=0
                    self.standing=True
                    m.cae=True

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

        now=pygame.time.get_ticks()

        cap_enemigos=pygame.sprite.spritecollide(self,self.ls_enemigos,False)
        for E in cap_enemigos:
            print self.HP
            if isinstance(E, bat):
                if not self.inmune:
                    self.HP-=1
                    self.inmune=True
                    self.inmune_last=now

            if isinstance(E,puas):
                self.HP=0

        cap_mods=pygame.sprite.spritecollide(self,self.ls_mods,False)
        for c in cap_mods:
            if isinstance(c,llama):
                self.abilityF=True
                c.kill()
            if isinstance(c,llama2):
                self.abilityF2=True
                c.kill()


        if now - self.inmune_last >= self.inmune_cd and self.inmune:
            self.inmune=False

        if now - self.down_last >= self.down_cd and self.down:
            self.down=False

class  bloque(pygame.sprite.Sprite):
    def __init__(self, imagen,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=imagen
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class  plataforma(pygame.sprite.Sprite):
    def __init__(self, imagen,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(imagen).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class  puas(pygame.sprite.Sprite):
    def __init__(self, imagen,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(imagen).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class  plataformaPodrida(pygame.sprite.Sprite):
    def __init__(self, imagen,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(imagen).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.cae=False
        self.cae_last=0
        self.cae_time=200

    def update(self):
        now=pygame.time.get_ticks()

        if self.cae:
            if now - self.cae_last >= self.cae_time:
                self.rect.y+=3

        if self.rect.y >= ALTO:
            self.kill()


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

class bat(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.bat_sheet=recortar(archivo,56,40)
        self.image=self.bat_sheet[0][0]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.cambioy=0
        self.cd_anim=120
        self.last=pygame.time.get_ticks()
        self.r=0

    def update(self):
        now= pygame.time.get_ticks()
        if now-self.last >=self.cd_anim:
            self.last=now
            if self.r>len(self.bat_sheet):
                self.r=0
            else:
                self.r+=1

        self.image=self.bat_sheet[0][self.r]


        if self.rect.y==64:
            self.cambioy=2
        if self.rect.y==384:
            self.cambioy=-2

        self.rect.y+=self.cambioy


class llama(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class llama2(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y







if __name__=="__main__":

    pygame.init()
    pantalla= pygame.display.set_mode([ANCHO,ALTO])

    todos=pygame.sprite.Group()
    blocks=pygame.sprite.Group()
    moviles=pygame.sprite.Group()
    enemigos=pygame.sprite.Group()
    plataformas=pygame.sprite.Group()
    plataformas_podridas=pygame.sprite.Group()
    mods=pygame.sprite.Group()

    jp= jugador("image/Vlad.png",100,300)

    mapa1=mapa("map/mapa-1.json")
    mapa1.analizarMapa(blocks,todos)



    batman=bat("image/bat.png",2016,64)
    enemigos.add(batman)
    todos.add(batman)



    plata=plataforma("image/plataforma1.png",1920,160)
    plataformas.add(plata)
    todos.add(plata)

    plata2=plataforma("image/plataforma1.png",2080,128)
    plataformas.add(plata2)
    todos.add(plata2)

    plata3=plataformaPodrida("image/podrida1.png",2080,224)
    plataformas_podridas.add(plata3)
    todos.add(plata3)

    plata4=plataforma("image/plataforma1.png",1920,128+128)
    plataformas.add(plata4)
    todos.add(plata4)

    plata5=plataformaPodrida("image/podrida1.png",2080,256+64)
    plataformas_podridas.add(plata5)
    todos.add(plata5)

    plata6=plataforma("image/plataforma1.png",2080,256+128+32)
    plataformas.add(plata6)
    todos.add(plata6)

    plata7=plataforma("image/plataforma1.png",1920,128+128+96)
    plataformas.add(plata7)
    todos.add(plata7)

    plata8=plataforma("image/plataforma2.png",2336,160)
    plataformas.add(plata8)
    todos.add(plata8)

    plata9=plataformaPodrida("image/podrida2.png",2336+192,160)
    plataformas_podridas.add(plata9)
    todos.add(plata9)

    plata10=plataforma("image/plataforma2.png",2336+192,160+96)
    plataformas.add(plata10)
    todos.add(plata10)

    plata11=plataforma("image/plataforma2.png",2336+192+128+32,160)
    plataformas.add(plata11)
    todos.add(plata11)

    plata12=plataforma("image/plataforma2.png",2336+256+256,192)
    plataformas.add(plata12)
    todos.add(plata12)

    plata13=plataforma("image/plataforma2.png",3072,192)
    plataformas.add(plata13)
    todos.add(plata13)

    plata13=plataforma("image/plataforma2.png",3072,192+96)
    plataformas.add(plata13)
    todos.add(plata13)

    poder1=llama("image/poder1.png",1440,256+96+64)
    mods.add(poder1)
    todos.add(poder1)

    poder2=llama2("image/poder2.png",2236+128,416)
    mods.add(poder2)
    todos.add(poder2)




    for i in range(19):
        p=puas("image/puas.png",2336+32*i,160+128)
        p.add(enemigos)
        p.add(todos)

    jp.ls_enemigos=enemigos
    jp.ls_block=blocks
    jp.ls_movil=moviles
    jp.ls_plataforma=plataformas
    jp.ls_plataforma_p=plataformas_podridas
    jp.ls_mods=mods
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
                    jp.rect.x=2000
                if event.key==pygame.K_SPACE:
                    jp.jump()
                if event.key==pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.key==pygame.K_s:
                    if jp.standing:
                        jp.cambioy=1
                        jp.down=True
                        jp.down_last=pygame.time.get_ticks()





        key = pygame.key.get_pressed()

        if key[pygame.K_a]:
            jp.image=jp.player_sheet[1][1]
            jp.move(-jp.velocidad, 0)

        if key[pygame.K_d]:
            jp.image=jp.player_sheet[0][1]
            jp.move(jp.velocidad, 0)

        #print jp.rect.x
        pantalla.fill(NEGRO)
        camara.dibujarSprites(pantalla, todos)
        camara.actualizar()
        #todos.draw(pantalla)
        todos.update()
        pygame.display.flip()
        reloj.tick(60)
