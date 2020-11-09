#Andreé Toledo
#Final Raycaster Project

import pygame
from pygame.sprite import Sprite
import pygame.freetype

from math import cos
from math import sin
from math import pi
from math import atan2

#FPS
FPS = 120/2
FPS_POSITION = (5, 5)

#Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
GREEN = (0, 100, 0)
BLUE = (0, 0, 220)

BACKGROUND = (114,19,225)
background = pygame.image.load('background.jpg')
Bomber = pygame.image.load('bomber.png')
Bomber = pygame.transform.scale(Bomber, (170, 170))

textures = {
    '1' : pygame.image.load('diamante.png'),
    '2' : pygame.image.load('diamante.png'),
    '3' : pygame.image.load('E1.png'),
    '4' : pygame.image.load('E2.png'),
    '5' : pygame.image.load('E3.png'),
    '6' : pygame.image.load('E4.png')
    }



class Raycaster(object):
    def __init__(self,screen):

        self.screen = screen

        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.blocksize = 50
        self.wallHeight = 50

        self.stepSize = 5

        self.player = {
            "x" : 75,
            "y" : 175,
            "angle" : 0,
            "fov" : 60
            }

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def drawRect(self, x, y, tex):
        tex = pygame.transform.scale(tex, (self.blocksize, self.blocksize))
        rect = tex.get_rect()
        rect = rect.move( (x,y) )
        self.screen.blit(tex, rect)

    def drawPlayerIcon(self,color):
        rect = (int(self.player['x'] - 2), int(self.player['y'] - 2), 5, 5)
        self.screen.fill(color, rect)
    
    def drawSprite(self, sprite, size):
        spriteDist = ((self.player['x'] - sprite['x'])**2 + (self.player['y'] - sprite['y'])**2) ** 0.5
        spriteAngle = atan2(sprite['y'] - self.player['y'], sprite['x'] - self.player['x'])

        aspectRatio = sprite["texture"].get_width() / sprite["texture"].get_height()
        spriteHeight = (self.height / spriteDist) * size
        spriteWidth = spriteHeight * aspectRatio

        angleRads = self.player['angle'] * pi / 180
        fovRads = self.player['fov'] * pi / 180

        startX = (self.width * 3 / 4) + (spriteAngle - angleRads)*(self.width/2) / fovRads - (spriteWidth/2)
        startY = (self.height / 2) - (spriteHeight / 2)
        startX = int(startX)
        startY = int(startY)

        for x in range(startX, int(startX + spriteWidth)):
            for y in range(startY, int(startY + spriteHeight)):
                if (self.width / 2) < x < self.width:
                    if self.zbuffer[ x - int(self.width/2)] >= spriteDist:
                        tx = int( (x - startX) * sprite["texture"].get_width() / spriteWidth )
                        ty = int( (y - startY) * sprite["texture"].get_height() / spriteHeight )
                        texColor = sprite["texture"].get_at((tx, ty))
                        if texColor[3] > 128 and texColor != RED:
                            self.screen.set_at((x,y), texColor)
                            self.zbuffer[ x - int(self.width/2)] = spriteDist

    def castRay(self, a):
        rads = a * pi / 180
        dist = 0
        while True:
            x = int(self.player['x'] + dist * cos(rads))
            y = int(self.player['y'] + dist * sin(rads))

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if self.map[j][i] != ' ':
                hitX = x - i*self.blocksize
                hitY = y - j*self.blocksize

                if 1 < hitX < self.blocksize - 1:
                    maxHit = hitX
                else:
                    maxHit = hitY

                tx = maxHit / self.blocksize

                return dist, self.map[j][i], tx

            self.screen.set_at((x,y), WHITE)

            dist += 2

    def play_music(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.mixer.music.load("audio.mp3")
        pygame.mixer.music.play(10)
    

    def render(self):

        halfWidth = int(self.width / 2)
        halfHeight = int(self.height / 2)

        for x in range(0, halfWidth, self.blocksize):
            for y in range(0, self.height, self.blocksize):
                
                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if self.map[j][i] != ' ':
                    self.drawRect(x, y, textures[self.map[j][i]])

        self.drawPlayerIcon(BLACK)

        for i in range(halfWidth):
            angle = self.player['angle'] - self.player['fov'] / 2 + self.player['fov'] * i / halfWidth
            dist, wallType, tx = self.castRay(angle)

            x = halfWidth + i 
            h = self.height / (dist * cos( (angle - self.player['angle']) * pi / 180 )) * self.wallHeight

            start = int( halfHeight - h/2)
            end = int( halfHeight + h/2)

            img = textures[wallType]
            tx = int(tx * img.get_width())

            for y in range(start, end):
                ty = (y - start) / (end - start)
                ty = int(ty * img.get_height())
                texColor = img.get_at((tx, ty))
                self.screen.set_at((x, y), texColor)

        for i in range(self.height):
            self.screen.set_at( (halfWidth, i), BLACK)
            self.screen.set_at( (halfWidth+1, i), BLACK)
            self.screen.set_at( (halfWidth-1, i), BLACK)

def textsurface(text, font_size, text_rgb, bg_rgb):
        font = pygame.freetype.SysFont("dejavusansmono", font_size, bold=True)
        surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
        return surface.convert_alpha()

class UIElement(Sprite):


    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        
        
        self.mouse_over = True  
        default_image = textsurface(
            text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        highlighted_image = textsurface(
            text=text, font_size=font_size * 1.2, text_rgb=text_rgb, bg_rgb=bg_rgb
        )

        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position),
        ]
        self.action = action 

      
        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]

    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

   
    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False

    def draw(self, surface): 
        surface.blit(self.image, self.rect)



def main():
    pygame.init()
    screen = pygame.display.set_mode((1000,500), pygame.DOUBLEBUF | pygame.HWACCEL) #, pygame.FULLSCREEN)
    game_state = 0

    while True:
        if game_state == 0:
            return title_screen(screen)   
        if game_state == 1:
            return play_level(screen)
        if game_state == -1:
            return pygame.quit
            



def title_screen(screen):

    pygame.mixer.music.load("audio.mp3")
    pygame.mixer.music.play()
    
    
    #agregar fonts
    #font1 = pygame.font.Font("main-font.ttf", 72)
    #font2 = pygame.font.Font("secondary-font.otf", 400)

    ON = UIElement(
        center_position=(500, 275),
        font_size=75,
        bg_rgb=WHITE,
        text_rgb=BLUE,
        text="BOMBERMAN",
    )
    GO = UIElement(
        center_position=(325, 400),
        font_size=42,
        bg_rgb=WHITE,
        text_rgb=BLUE,
        text="Inicio",
        action= play_level(screen),
    )
    OFF = UIElement(
        center_position=(625, 400),
        font_size=42,
        bg_rgb=WHITE,
        text_rgb=RED,
        text="Salir",
        action= -1,
    )

    buttons = [ON, GO, OFF]

    while True:
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
        screen.blit(background, (-600,-75))
        screen.blit(Bomber, (400,325))
        

        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(screen)

        pygame.display.flip()    

def play_level(screen):
    
    pygame.init()
    screen = pygame.display.set_mode((1000,500), pygame.DOUBLEBUF | pygame.HWACCEL) #, pygame.FULLSCREEN)
    screen.set_alpha(None)
    pygame.display.set_caption('Proyecto RayCaster')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("dejavusansmono", 30)

    def updateFPS():
        fps = "FPS:" + str(int(clock.get_fps()))
        fps = font.render(fps, 1, pygame.Color("lightgray"))
        return fps

    r = Raycaster(screen)

    r.load_map('map.txt')

    isRunning = True

    while isRunning:

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                isRunning = False

            newX = r.player['x']
            newY = r.player['y']

            if ev.type == pygame.KEYDOWN:
                r.play_music
                if ev.key == pygame.K_ESCAPE:
                    isRunning = False
                elif ev.key == pygame.K_w:
                    newX += cos(r.player['angle'] * pi / 180) * r.stepSize
                    newY += sin(r.player['angle'] * pi / 180) * r.stepSize
                elif ev.key == pygame.K_s:
                    newX -= cos(r.player['angle'] * pi / 180) * r.stepSize
                    newY -= sin(r.player['angle'] * pi / 180) * r.stepSize
                elif ev.key == pygame.K_a:
                    newX -= cos((r.player['angle'] + 90) * pi / 180) * r.stepSize
                    newY -= sin((r.player['angle'] + 90) * pi / 180) * r.stepSize
                elif ev.key == pygame.K_d:
                    newX += cos((r.player['angle'] + 90) * pi / 180) * r.stepSize
                    newY += sin((r.player['angle'] + 90) * pi / 180) * r.stepSize
                elif ev.key == pygame.K_q:
                    r.player['angle'] -= 5
                elif ev.key == pygame.K_e:
                    r.player['angle'] += 5


                i = int(newX / r.blocksize)
                j = int(newY / r.blocksize)

                if r.map[j][i] == ' ':
                    r.player['x'] = newX
                    r.player['y'] = newY

        #BACKPART
        screen.fill(pygame.Color("gray")) 

        #UP
        screen.fill(pygame.Color("saddlebrown"), (int(r.width / 2), 0, int(r.width / 2),int(r.height / 2)))
        
        #DOWN
        screen.fill(pygame.Color("dimgray"), (int(r.width / 2), int(r.height / 2), int(r.width / 2),int(r.height / 2)))

        r.render()
        
        #FPS
        screen.fill(pygame.Color("black"), (0,0,60,25))
        screen.blit(updateFPS(), (0,0))
        clock.tick(30)  
        
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()