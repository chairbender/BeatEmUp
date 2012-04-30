#! /usr/bin/env python

import os, sys
import pygame
from pygame.locals import *

def load_image(name, colorkey=None):
    fullname = os.path.join('..\\','sprites')
    fullname = os.path.join(fullname, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def getAnimation(image_prefix):
    """Return a list of images in order
    representing the frames of the animation
    given by the passed prefix (image_prefix should
    include the final underscore)
    Expects images in the sprites folder of the form
    name_of_animation_####.png where #### is the 4 digit frame number
    and sprite is in png format
    (i.e. as exported from GraphicsGale)
    """
    
    fullname_prefix = os.path.join('..\\','sprites')
    fullname_prefix = os.path.join(fullname_prefix, image_prefix)
    
    #Make sure at least the first frame is there
    try:
        image = pygame.image.load(fullname_prefix + '0000.png')
    except pygame.error, message:
        print 'Cannot load image:', image_prefix + \
            '0000.png not found in images folder'
        raise SystemExit, message
    
    #Loop through the frames
    result = []
    index = 0
    while True:
        suffix = "%04d" % index
        try:
            result.append(pygame.image.load(fullname_prefix + suffix + '.png'))
        except pygame.error, message:
            #Done loading frames, break
            break
        index += 1
    return result