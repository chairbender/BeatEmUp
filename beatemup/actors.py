'''
Created on Apr 29, 2012

@author: Kyle
'''

import pygame
from pygame.transform import *
from beatemup.util import *

class Hero(pygame.sprite.Sprite):
    """The hero class."""
    #Movement speed in pixels per tick
    MOVE_SPEED = 1.5
    #The walking animation, tuple of tuples of surfaces and rects
    s_walk_animation = None 
    #The speed of animation (ticks per frame)
    ANIMATION_SPEED = 8
    #Possible states
    IDLE, MOVING = range(2)
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        
        #Initialize static vars
        Hero.s_walk_animation = (load_image('hero_walk_0000.png',-1), \
                        load_image('hero_walk_0001.png',-1))  
        #End initializing static vars
        
        #Holds the state
        self.state = Hero.IDLE
        #Whether we've moved this tick
        self.hasMoved = False
        
        #Holds the current velocity
        self.xMove, self.yMove = (0, 0)

        
        self.image, self.rect = Hero.s_walk_animation[0]  
        #How many ticks have elapsed since the restart of the current animation     
        self.anim_timer = 0
        #images are surfaces, so stretch
        #self.image = scale(self.image,(128,128))
        
    def update(self):
        #Update position
        self.rect.move_ip(self.xMove,self.yMove)
        
        """Update animation frame"""
        #increase animation timer
        self.anim_timer = (self.anim_timer + 1) % (Hero.ANIMATION_SPEED * len(Hero.s_walk_animation))
        #calculate which frame of animation we are on
        anim_index = self.anim_timer / Hero.ANIMATION_SPEED
        if self.xMove != 0 or self.yMove != 0:
            self.state = Hero.MOVING
            self.image = Hero.s_walk_animation[anim_index][0]
        else:
            self.state = Hero.IDLE
            self.image = Hero.s_walk_animation[0][0]
        
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