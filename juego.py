import pygame
from compugrafica import *
import json
from pygame.locals import *
'''
empaquetar programas linux
'''

IZQUIERDA=1
DERECHA=0
ABAJO=2
ARRIBA=3


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
        self.mp=[]
        self.mb=[]

        for l in self.base['layers']:
            if l['name']=='muros':
                self.lm=l['data']
            if l['name']=='plataformas':
                self.mp=l['data']
            if l['name']=='escombros':
                self.mb=l['data']

        self.ancho_fondo=self.base['width']
        self.alto_fondo=self.base['height']
        self.mapa=self.Separar(self.lm, self.ancho_fondo)
        self.mapap=self.Separar(self.mp, self.ancho_fondo)
        self.mapab=self.Separar(self.mb, self.ancho_fondo)
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

    def analizarMapa(self,blocks,plataformas,todos,enemigos):
        xy=0
        for f in self.mapa:
            xp=0
            for c in f:
                if c!=0:
                    cuadro=self.tile_list[c-1]
                    b=bloque(cuadro,xp,xy)
                    blocks.add(b)
                    todos.add(b)
                xp+=self.ancho_tile
            xy+=self.alto_tile

        xy=0
        for f in self.mapab:
            xp=0
            for c in f:
                if c!=0:
                    cuadro=self.tile_list[c-1]
                    pantalla.blit(cuadro,[110,110])
                    p=escombro(cuadro,xp,xy)
                    enemigos.add(p)
                    enemigos.draw(pantalla)
                    todos.add(p)
                xp+=self.ancho_tile
            xy+=self.alto_tile

        xy=0
        for f in self.mapap:
            xp=0
            for c in f:
                if c!=0:
                    cuadro=self.tile_list[c-1]
                    pantalla.blit(cuadro,[110,110])
                    p=plataforma_map(cuadro,xp,xy)
                    plataformas.add(p)
                    plataformas.draw(pantalla)
                    todos.add(p)
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
            self.player_sheet=recortar(sheet,48,56)
            self.image= self.player_sheet[0][0]
            self.rect=self.image.get_rect()
            self.rect.x=x
            self.rect.y=y
            self.cambioy=0
            self.standing=False
            self.lock=True
            self.HP=3
            self.power=0
            self.mulsalto=1
            self.facing=DERECHA
            self.anim_cd=100
            self.anim_last=pygame.time.get_ticks()
            self.r=0
            self.c=0
            self.down=False
            self.inmune=False
            self.inmune_cd=1000
            self.inmune_last=pygame.time.get_ticks()
            self.down_last=0
            self.down_cd=250
            self.interact=False
            self.next_lvl=False
            self.abilityF=False
            self.abilityF2=False
            self.abilityF3=False
            self.abilityF4=False
            self.abilityF5=False
            self.abilityF6=False
            self.palanca=False
            self.llave=False

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
                self.standing=True
                self.cambioy=0
            if dy<0:
                self.rect.top=g.rect.bottom
                self.cambioy=-0.35

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

        ls_golpes=pygame.sprite.spritecollide(self,self.ls_mods,False)
        for m in ls_golpes:
            if isinstance(m,hiedra):
                if dx>0:
                    self.rect.right=m.rect.left
                if self.abilityF2:
                    m.kill()
            if isinstance(m,rejilla):
                if dy>0:
                    self.rect.bottom=m.rect.top
                    self.cambioy=0
                    self.standing=True
            if isinstance(m,puerta1):
                if dx>0:
                    self.rect.right=m.rect.left
                if dx<0:
                    self.rect.left=m.rect.right
                m.otra.kill()

            if isinstance(m,puerta2):
                if dx>0:
                    self.rect.right=m.rect.left
                if dx<0:
                    self.rect.left=m.rect.right
                if self.llave and m.reja!=None:
                    m.reja.kill()





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
                if self.rect.y<m.rect.y-32:
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
        if self.standing:
            self.cambioy=-8*self.mulsalto
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

        self.image=self.player_sheet[self.c][self.r]

        now=pygame.time.get_ticks()

        cap_enemigos=pygame.sprite.spritecollide(self,self.ls_enemigos,False)
        for E in cap_enemigos:
            print self.HP
            if isinstance(E, bat):
                if not self.inmune:
                    self.HP-=1
                    self.inmune=True
                    self.inmune_last=now

            if isinstance(E, golem):
                if not self.inmune:
                    self.HP-=1
                    self.inmune=True
                    self.inmune_last=now

            if isinstance(E,puas):
                self.HP=0
            if isinstance(E,escombro):
                self.HP=0

        cap_mods=pygame.sprite.spritecollide(self,self.ls_mods,False)
        for c in cap_mods:
            if isinstance(c,llama):
                self.abilityF=True
                self.power=2
                c.kill()
            if isinstance(c,llama2):
                self.abilityF2=True
                self.power=4
                c.kill()
            if isinstance(c,palanca):
                self.palanca=True
                c.completa=True
                c.kill()

            if isinstance(c,llave):
                self.llave=True
                c.kill()

            if isinstance(c,base_palanca):
                #print self.interact
                if self.palanca:
                    c.completa=True
                    if not c.accionada:
                        c.image=c.base_sheet[0][1]
                    if self.interact:
                        c.accionada=True
            if isinstance(c,llama3):
                self.abilityF3=True
                self.mulsalto=1.5
                c.kill()

            if isinstance(c,llama4):
                self.abilityF4=True
                self.power=6
                c.kill()

            if isinstance(c,llama5):
                self.abilityF5=True
                self.power=8
                c.kill()

            if isinstance(c,llama6):
                self.abilityF6=True
                self.power=12
                c.kill()

        if now - self.inmune_last >= self.inmune_cd and self.inmune:
            self.inmune=False

        if now - self.down_last >= self.down_cd and self.down:
            self.down=False

        self.interact=False

    def fire(self,imagen):
        bola=fuego(imagen,self.rect.x+7,self.rect.y+7,self.facing)
        bola.ls_block=self.ls_block
        return bola

class fuego(pygame.sprite.Sprite):
    ls_block=None

    def __init__(self,sheet,x,y,direccion):
        pygame.sprite.Sprite.__init__(self)
        self.fire_sheet=recortar(sheet,32,32)
        self.dir=direccion
        self.image=self.fire_sheet[direccion][0]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.charge=1

    def update(self):
        vel=10
        if self.dir==IZQUIERDA:
            self.rect.x-=vel
        if self.dir==ARRIBA:
            self.rect.y-=vel
        if self.dir==DERECHA:
            self.rect.x+=vel
        if self.dir==ABAJO:
            self.rect.y+=vel

        ls_golpes=pygame.sprite.spritecollide(self,self.ls_block,False)
        for g in ls_golpes:
            self.kill()


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

class  plataforma_map(pygame.sprite.Sprite):
    def __init__(self, imagen,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=imagen
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
class  escombro(pygame.sprite.Sprite):
    def __init__(self, imagen,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=imagen
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
    ls_fire=None
    player=None
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.bat_sheet=recortar(archivo,56,40)
        self.image=self.bat_sheet[0][0]
        self.rect=self.image.get_rect()
        self.HP=20
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

        cap_fuego=pygame.sprite.spritecollide(self,self.ls_fire,True)
        for f in cap_fuego:
            self.HP-=self.player.power

        if self.HP<=0:
            self.kill()


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

class llama3(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class llama4(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class llama5(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class llama6(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class golem(pygame.sprite.Sprite):
    player=None
    ls_fire=None
    ls_mods=None
    todos=None
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.golem_sheet=recortar(archivo,48,60)
        self.image=self.golem_sheet[0][2]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.HP=8
        self.cambiox=0
        self.anim_last=pygame.time.get_ticks()
        self.anim_cd=900
        self.i=0
        self.j=2


    def update(self):
        self.image=self.golem_sheet[self.i][self.j]
        now=pygame.time.get_ticks()

        self.rect.x+=self.cambiox

        if self.player.rect.x > self.rect.x +42:
            self.cambiox=1
            self.j=0
            if now - self.anim_last >= self.anim_cd:
                if self.i==0:
                    self.i=1
                else:
                    self.i=0


        if self.rect.x == self.player.rect.x:
            self.i=0
            self.j=2

        if self.player.rect.x < self.rect.x - 10:
            self.cambiox=-1
            self.j=1
            if now - self.anim_last >= self.anim_cd:
                if self.i==0:
                    self.i=1
                else:
                    self.i=0

        if self.rect.x<=2336:
            self.rect.x=2336

        cap_fuego=pygame.sprite.spritecollide(self,self.ls_fire,True)
        for f in cap_fuego:
            if self.player.abilityF4:
                self.HP-=self.player.power

        if self.HP<=0:
            self.tirar_poder()
            self.kill()

    def tirar_poder(self):

        l=llama3("image/poder3.png",self.rect.x+32,self.rect.y+32)
        self.todos.add(l)
        self.ls_mods.add(l)



class hiedra(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class palanca(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class rejilla(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class llave(pygame.sprite.Sprite):
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

class base_palanca(pygame.sprite.Sprite):
    reja=None
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.base_sheet=recortar(archivo,32,32)
        self.image=self.base_sheet[0][3]
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.completa=False
        self.accionada=False
    def update(self):
        if self.completa and self.accionada:
            self.reja.kill()
            self.image=self.base_sheet[0][2]

class puerta1(pygame.sprite.Sprite):
    otra=None
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y



class puerta2(pygame.sprite.Sprite):
    reja=None
    def __init__(self,archivo,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.image.load(archivo).convert_alpha()
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y



def Sprites_nivel(niveles,todos,blocks,moviles,enemigos,plataformas,plataformas_podridas,mods,fireball,nivelActual):
    niveles[nivelActual].analizarMapa(blocks,plataformas,todos,enemigos)
    if nivelActual==0:
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

        plata14=plataforma("image/plataforma2.png",7*32,9*32)
        plataformas.add(plata14)
        todos.add(plata14)

        plata14=plataforma("image/plataforma2.png",6*32,4*32)
        plataformas.add(plata14)
        todos.add(plata14)

        plata14=plataforma("image/plataforma1.png",93*32,12*32)
        plataformas.add(plata14)
        todos.add(plata14)


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

        batman=bat("image/bat.png",2016,64)
        batman.ls_fire=fireball
        batman.player=jp
        enemigos.add(batman)
        todos.add(batman)

        g=golem("image/golemhardcore.png",2428,416)
        g.ls_fire=fireball
        g.player=jp
        g.ls_mods=mods
        g.todos=todos
        g.add(enemigos)
        g.add(todos)

        h=hiedra("image/enredadera.png",3072,384)
        mods.add(h)
        todos.add(h)

        p=palanca("image/palanca.png",3136,448)
        mods.add(p)
        todos.add(p)

        r=rejilla("image/rejilla.png",1152,224)
        mods.add(r)
        todos.add(r)

        l=llave("image/llave.png",1248,384)
        mods.add(l)
        todos.add(l)

        b=base_palanca("image/base_palanca.png",1152-32,192)
        b.reja=r
        mods.add(b)
        todos.add(b)

        puer2=puerta2("image/puerta2.png",480,352)
        mods.add(puer2)
        todos.add(puer2)

        puer=puerta1("image/puerta1.png",0,352)
        puer.otra=puer2
        mods.add(puer)
        todos.add(puer)

        r2=rejilla("image/rejilla.png",224,480)
        mods.add(r2)
        todos.add(r2)

    if nivelActual==1:
        poder4=llama4("image/poder4.png",36*32,4*32)
        mods.add(poder4)
        todos.add(poder4)

        for i in range(25):
            p=puas("image/puas.png",14*32+32*i,18*32)
            p.add(enemigos)
            p.add(todos)




    if nivelActual==2:
        plata=plataforma("image/plataforma1.png",1920,160)
        plataformas.add(plata)
        todos.add(plata)

        plata2=plataforma("image/plataforma1.png",2080,128)
        plataformas.add(plata2)
        todos.add(plata2)

        plata4=plataforma("image/plataforma1.png",1920,128+128)
        plataformas.add(plata4)
        todos.add(plata4)

        plata6=plataforma("image/plataforma1.png",2080,256+128+32)
        plataformas.add(plata6)
        todos.add(plata6)

        plata7=plataforma("image/plataforma1.png",1920,128+128+96)
        plataformas.add(plata7)
        todos.add(plata7)

        plata8=plataforma("image/plataforma2.png",2336,160)
        plataformas.add(plata8)
        todos.add(plata8)

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

        plata14=plataforma("image/plataforma2.png",6*32,4*32)
        plataformas.add(plata14)
        todos.add(plata14)

        plata14=plataforma("image/plataforma2.png",7*32,9*32)
        plataformas.add(plata14)
        todos.add(plata14)

        plata14=plataforma("image/plataforma1.png",93*32,12*32)
        plataformas.add(plata14)
        todos.add(plata14)

        for i in range(19):
            p=puas("image/puas.png",2336+32*i,160+128)
            p.add(enemigos)
            p.add(todos)
        for i in range(3):
            p=puas("image/puas.png",1824+32*i,608)
            p.add(enemigos)
            p.add(todos)


        batman2=bat("image/bat.png",2016,64)
        batman2.ls_fire=fireball
        batman2.player=jp
        enemigos.add(batman2)
        todos.add(batman2)

        g2=golem("image/golemhardcore.png",2428,416)
        g2.player=jp
        g2.ls_fire=fireball
        g2.ls_muros=blocks
        g2.ls_mods=mods
        g2.todos=todos
        g2.add(enemigos)
        g2.add(todos)

        r2=rejilla("image/rejilla.png",224,480)
        mods.add(r2)
        todos.add(r2)

        puer2=puerta2("image/puerta1.png",0,352)
        puer2.reja=r2
        mods.add(puer2)
        todos.add(puer2)

        if not jp.palanca:
            poder2=llama2("image/poder2.png",2236+128,416)
            mods.add(poder2)
            todos.add(poder2)
            h=hiedra("image/enredadera.png",3072,384)
            mods.add(h)
            todos.add(h)
            p=palanca("image/palanca.png",3136,448)
            mods.add(p)
            todos.add(p)

        r=rejilla("image/rejilla.png",1152,224)
        mods.add(r)
        todos.add(r)
        b=base_palanca("image/base_palanca.png",1152-32,192)
        b.reja=r
        mods.add(b)
        todos.add(b)

        l=llave("image/llave.png",1248,384)
        mods.add(l)
        todos.add(l)

    if nivelActual==3:

        poder5=llama5("image/poder5.png",14*32,95*32)
        mods.add(poder5)
        todos.add(poder5)

    if nivelActual==4:
        poder6=llama6("image/poder6.png",35*32,8*32)
        mods.add(poder6)
        todos.add(poder6)














if __name__=="__main__":

    pygame.init()
    pantalla= pygame.display.set_mode([ANCHO,ALTO])
    fondo1 = pygame.image.load("fondos/map.png").convert_alpha()
    fondo2 = pygame.image.load("fondos/fondo12.png").convert_alpha()
    fondo4 = pygame.image.load("fondos/fondo2.png").convert_alpha()
    fondo3 = pygame.image.load("fondos/map.png").convert_alpha()
    fondos=[fondo1,fondo2,fondo3,fondo4]

    todos=pygame.sprite.Group()
    blocks=pygame.sprite.Group()
    moviles=pygame.sprite.Group()
    enemigos=pygame.sprite.Group()
    plataformas=pygame.sprite.Group()
    plataformas_podridas=pygame.sprite.Group()
    mods=pygame.sprite.Group()
    fireball=pygame.sprite.Group()



    nivelActual=0
    nivel1=mapa("map/mapa1.json")
    nivel2=mapa("map/mapa2.json")
    nivel3=mapa("map/mapa1.json")
    nivel4=mapa("map/mapa3.json")
    nivel5=mapa("map/mapa4.json")

    niveles=[nivel1,nivel2,nivel3,nivel4,nivel5]

    jp= jugador("image/Timmy.png",100,300)

    Sprites_nivel(niveles,todos,blocks,moviles,enemigos,plataformas,plataformas_podridas,mods,fireball,nivelActual)










    jp.ls_enemigos=enemigos
    jp.ls_block=blocks
    jp.ls_movil=moviles
    jp.ls_plataforma=plataformas
    jp.ls_plataforma_p=plataformas_podridas
    jp.ls_mods=mods
    todos.add(jp)

    posx=0
    posy=0

    camara = Camara(pantalla, jp.rect,niveles[nivelActual].ancho_fondo*niveles[nivelActual].ancho_tile,niveles[nivelActual].alto_fondo*niveles[nivelActual].alto_tile)

    reloj=pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    jp.rect.y=300
                    jp.rect.x=1400
                if event.key==pygame.K_SPACE:
                    jp.jump()
                    jp.image=jp.player_sheet[3][3]
                if event.key==pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.key==pygame.K_s:
                    if jp.standing:
                        jp.cambioy=1
                        jp.down=True
                        jp.down_last=pygame.time.get_ticks()
                if event.key==pygame.K_e:
                    jp.interact=True
                    jp.c=4
                if event.key==pygame.K_f:
                    jp.c=4

                    if jp.abilityF6:
                        bala=jp.fire("image/bala6.png")
                        bala.image=bala.fire_sheet[0][jp.facing]
                        todos.add(bala)
                        fireball.add(bala)
                    elif jp.abilityF5:
                        bala=jp.fire("image/bala5.png")
                        bala.image=bala.fire_sheet[0][jp.facing]
                        todos.add(bala)
                        fireball.add(bala)
                    elif jp.abilityF4:
                        bala=jp.fire("image/bala4.png")
                        bala.image=bala.fire_sheet[0][jp.facing]
                        todos.add(bala)
                        fireball.add(bala)
                    elif jp.abilityF2:
                        bala=jp.fire("image/bala2.png")
                        todos.add(bala)
                        fireball.add(bala)
                    elif jp.abilityF:
                        bala=jp.fire("image/bala1.png")
                        todos.add(bala)
                        fireball.add(bala)








        key = pygame.key.get_pressed()

        if key[pygame.K_a]:
            jp.move(-jp.velocidad, 0)
            jp.facing=IZQUIERDA
            jp.r=2
            now=pygame.time.get_ticks()
            if now - jp.anim_last >= jp.anim_cd:
                jp.anim_last=now
                if jp.c>=3:
                    jp.c=0
                else:
                    jp.c+=1

        if key[pygame.K_d]:

            jp.move(jp.velocidad, 0)
            jp.facing=DERECHA
            jp.r=1
            now=pygame.time.get_ticks()
            if now - jp.anim_last >= jp.anim_cd:
                jp.anim_last=now
                if jp.c>=3:
                    jp.c=0
                else:
                    jp.c+=1




        if jp.rect.x>1824 and jp.rect.y>544 and nivelActual==0:
            jp.next_lvl=True
        if nivelActual==1:
            if jp.rect.y<=0:
                jp.next_lvl=True
        if nivelActual==2:
            if jp.rect.y>544 and jp.rect.x< 1024:
                jp.next_lvl=True
                jp.mulsalto=1

        if nivelActual==3:
            if jp.abilityF5:
                jp.next_lvl=True

        if jp.next_lvl:
            nivelActual+=1
            camara = Camara(pantalla, jp.rect,niveles[nivelActual].ancho_fondo*niveles[nivelActual].ancho_tile,niveles[nivelActual].alto_fondo*niveles[nivelActual].alto_tile)
            if nivelActual==1:
                jp.rect.x=128
                jp.rect.y=32
            if nivelActual==2:
                jp.rect.x=1792
                jp.rect.y=448
            if nivelActual==3:
                jp.rect.x=160
                jp.rect.y=64
            if nivelActual==4:
                jp.rect.x=4*32
                jp.rect.y=8*32

            jp.next_lvl=False
            todos.empty()
            blocks.empty()
            moviles.empty()
            enemigos.empty()
            plataformas.empty()
            plataformas_podridas.empty()
            mods.empty()
            fireball.empty()
            todos.add(jp)
            jp.cambioy=0
            Sprites_nivel(niveles,todos,blocks,moviles,enemigos,plataformas,plataformas_podridas,mods,fireball,nivelActual)















        #print jp.rect.x
        #print camara.rect.x
        if nivelActual<4:
            pantalla.blit(fondos[nivelActual],(posx,posy))
        else:
            pantalla.fill(NEGRO)
        camara.actualizar()
        #todos.draw(pantalla)
        todos.update()
        camara.dibujarSprites(pantalla, todos)
        pygame.display.flip()
        reloj.tick(60)
        posx=-camara.rect.x
        posy=-camara.rect.y
