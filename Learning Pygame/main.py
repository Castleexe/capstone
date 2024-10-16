import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join #importing these to load sprites dynamically
pygame.init()

pygame.display.set_caption("Platformer") #setting window name
    
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5 #player speed

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assests", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))] #load every file that is in the dir

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha

        sprites = []
        #load each frame
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

class Player(pygame.sprite.Sprite):
    color = (255, 0, 0)
    GRAVITY = 1 #acceleration
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left" #what direction player is facing
        self.animation_count = 0 #to reset animation when going left or right
        self.fall_count = 0
    
    def move(self, dx, dy):
        self.rect.x += dx #displacement x
        self.rect.y += dy #displacement y
    
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self, fps): #run once every frame
        #self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1

    def draw(self, win):
        self.sprite = self.SPRITES["idle_" + self.direction][0]
        win.blit(self.sprite, (self.rect.x, self.rect.y))



def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _,_, width, height = image.get_rect() #_ for values we dont care about
    tiles = []

    for i in range(WIDTH // width + 1): #tells x amount tiles
        for j in range(HEIGHT // height + 1):  #tells y amount tiles
            pos = (i * width, j * height) #pos of top left tile of current tile
            tiles.append(pos)
    return tiles, image

def draw(window, background, bg_img, player):
    for tile in background:
        window.blit(bg_img, tile)

    player.draw(window)

    pygame.display.update()

def handle_move(player):
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0
    if keys[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d]:
        player.move_right(PLAYER_VEL) 

def main(window):
    clock = pygame.time.Clock()
    background, bg_img = get_background("Green.png")

    player = Player(100,100,50,50)

    run = True
    while(run):
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        player.loop(FPS)
        handle_move(player)
        draw(window, background, bg_img, player)
    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window) #this line makes it so that only call the main func only when we call it directly 