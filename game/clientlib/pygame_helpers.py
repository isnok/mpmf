import os
import pygame

from pygame.locals import *

def rect_from_picture(image, position=None):
    image_obj = pygame.image.load("assets/"+str(image))
    rect = image_obj.get_rect()
    if position is not None:
        rect[0] = position[0]
        rect[1] = position[1]

    return rect

def load_image(name, colorkey=None, scale=None):
    fullname = os.path.join('assets', name)

    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        output('Cannot load image: %s' % name, 'error')
        raise SystemExit, message

    if scale is not None:
        image = pygame.transform.scale(image, scale)

    image = image.convert()

    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()

def load_sound(name):
    fullname = os.path.join('assets', name)

    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer:
        return NoneSound()

    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        output('Cannot load sound: %s' % name, 'error')
        raise SystemExit, message

    return sound
