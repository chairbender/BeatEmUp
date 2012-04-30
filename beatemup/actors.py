'''
Created on Apr 29, 2012

@author: Kyle
'''

import pygame
from pygame.transform import *
from beatemup.util import *

class Animation:
    """Stores a sequence of sprites and
    an animation speed
    Can access using array indices, returns the image surface
    representing the frame at the specified index
    (len works, too)
    """
    
    def __init__(self,image_prefix,speed):
        """
        image_prefix: the prefix of the batch of images
        to load in the sprites folder for this animation -
        to load sprites of the form image_prefix_####.png in the sprites folder
        (image_prefix should include the final underscore)
        speed: speed of animation in ticks per frame (so higher = slower)
        """
        #Speed of animation
        self.animation_speed = speed
        
        #Will hold the sprite frames
        self.sprite_frames = getAnimation(image_prefix)
    
    def __getitem__(self,index):
        return self.sprite_frames[index]
    
    def __len__(self):
        return len(self.sprite_frames)
        

class Hero(pygame.sprite.Sprite):
    """The hero class."""
    #Movement speed in pixels per tick
    MOVE_SPEED = 1.5
    #The walking animation, tuple of tuples of surfaces and rects
    s_walk_animation = None 
    #Possible states
    IDLE, MOVING = range(2)
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        
        #Initialize static vars if first time
        if Hero.s_walk_animation == None:   
            Hero.s_walk_animation = Animation('hero_walk_',8)  
        #End initializing static vars
        
        #Holds the state
        self.state = Hero.IDLE
        #Whether we've moved this tick
        self.hasMoved = False
        
        #Holds the current velocity
        self.xMove, self.yMove = (0, 0)

        
        self.image, self.rect = (Hero.s_walk_animation[0],\
                                 Hero.s_walk_animation[0].get_rect())
                                 
        #How many ticks have elapsed since the restart of the current animation     
        self.anim_timer = 0
        #images are surfaces, so stretch
        #self.image = scale(self.image,(128,128))
        
    def update(self):
        #Update position
        self.rect.move_ip(self.xMove,self.yMove)
        
        """Update animation frame"""
        #increase animation timer
        self.anim_timer = (self.anim_timer + 1) % \
            (Hero.s_walk_animation.animation_speed * len(Hero.s_walk_animation))
        #calculate which frame of animation we are on
        anim_index = self.anim_timer / Hero.s_walk_animation.animation_speed
        if self.xMove != 0 or self.yMove != 0:
            self.state = Hero.MOVING
            self.image = Hero.s_walk_animation[anim_index]
        else:
            self.state = Hero.IDLE
            self.image = Hero.s_walk_animation[0]
        
    def move(self,event_type,key):
        """
        event_type:KEYDOWN or KEYUP
        key: keyEvent this hero should respond to
        Move the hero and update state.
        Should be called before updating"""
        
        #If KEYUP, stop moving in that direction
        if (event_type == KEYUP):
            if (key == K_RIGHT or key == K_LEFT):
                self.xMove = 0
            elif (key == K_UP or key == K_DOWN):
                self.yMove = 0
        else:
            #Keydown, start moving in that direction
            if (key == K_RIGHT):
                self.xMove = Hero.MOVE_SPEED
            elif (key == K_LEFT):
                self.xMove = -Hero.MOVE_SPEED
            elif (key == K_UP):
                self.yMove = -Hero.MOVE_SPEED
            elif (key == K_DOWN):
                self.yMove = Hero.MOVE_SPEED
        
    
    def setPosition(self,position):
        """position: the (x,y) tuple to set the
        position of this hero to in the current map"""
        self.rect.move_ip(position[0],position[1])