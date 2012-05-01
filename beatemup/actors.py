'''
Created on Apr 29, 2012

@author: Kyle
'''

import pygame, math, random
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

class Mover(pygame.sprite.Sprite):
    """Class for a sprite that moves and animates
    Subclasses can call moveUpdate to set the image
    and rect for this sprite, and 
    advanceAnimation to handle updating the sprite
    based on the current animation
    """
    IDLE, MOVING = range(2)
    
    def __init__(self,walk_animation,idle_animation):
        pygame.sprite.Sprite.__init__(self) 
        #Our animations
        self.walk_animation = walk_animation
        self.idle_animation = idle_animation
        
        self.state = Mover.IDLE
        
        #Holds the current velocity
        self.xMove, self.yMove = (0, 0)
        
        #Holds the current animation
        self.current_animation = self.idle_animation
        
        #Initialize our rect and image
        self.image, self.rect = (self.idle_animation[0],\
                                 self.idle_animation[0].get_rect())
        
        #How many ticks have elapsed since the restart of the current animation     
        self.anim_timer = 0
        
    def moveUpdate(self,xMove,yMove):
        """
        Look at speed and see if it is nonzero
        If so, move using xMove and yMove as velocities. If
        zero, just plays the idle animation and stays still
        @effects Sets self.current_animation to the walk or idle animation
        """
        #Now we might've started moving or being idle, so
        #check and update animation and position accordingly
        if xMove != 0 or yMove != 0:
            self.current_animation = self.walk_animation  
            self.rect.move_ip(xMove,yMove)
        else:
            #idle
            self.current_animation = self.idle_animation            
    
    def advanceAnimation(self):
        """Call this every tick to advance the current animation
        frame. Uses self.current_animation"""            
        #increase animation timer
        self.anim_timer = (self.anim_timer + 1) % \
            (self.current_animation.animation_speed * len(self.current_animation))
        #calculate which frame of animation we are on
        anim_index = self.anim_timer / self.current_animation.animation_speed
        #Actually update the image to the frame we are on
        self.image = self.current_animation[anim_index]
        
class Enemy(Mover):
    """Enemy that moves sporadically towards
    player"""
    
    MOVE_SPEED = 1
    #Probability of stopping and waiting for a few ticks
    STOP_PROBABILITY = .025
    #Rect for getting punched
    HIT_BOX_IN_LOCAL = None
    #States
    IDLE_OR_MOVING, HIT = range(2)
    
    
    s_walk_animation = None
    s_hit_animation = None 
    s_idle_animation = None 
    
    def __init__(self, xPos, yPos):
        #Initialize static vars if first time
        if Enemy.s_walk_animation == None:   
            Enemy.s_walk_animation = Animation('enemy_walk_',8)
            Enemy.s_hit_animation = Animation('enemy_hit_',12)
            Enemy.s_idle_animation = Animation('enemy_idle_',8)   
              
            Enemy.HIT_BOX_IN_LOCAL = Rect(0,Enemy.s_idle_animation[0].get_rect().height/2,
                                         Enemy.s_idle_animation[0].get_rect().width,20)
            
            
        Mover.__init__(self,Enemy.s_walk_animation,Enemy.s_idle_animation)   
        
        #tracking velocity
        self.xspeed, self.yspeed = 0, 0
                
        #Set position
        self.rect.move_ip(xPos,yPos)
        
        #Number of ticks to wait before moving again
        self.wait_count = 0
        
        self.state = Enemy.IDLE_OR_MOVING
        self.prevstate = Enemy.IDLE_OR_MOVING
        
    def getPunched(self):
        """
        Call when enemy is getting punched.
        Expected to be called before update each tick
        """
        if self.state != Enemy.HIT:
            self.state = Enemy.HIT
            
    def doMove(self,hero):
        """
        choose what to do based on the position of the Hero
        """
        #Check if we are currently waiting
        if self.wait_count > 0:
            self.wait_count -= 1
            self.xspeed = self.yspeed = 0
        else:
            self.state = Enemy.IDLE_OR_MOVING
            herox, heroy = hero.rect.centerx, hero.rect.centery
            selfx, selfy = self.rect.centerx, self.rect.centery
    
            if herox > selfx:
                self.xspeed = Enemy.MOVE_SPEED
            else:
                self.xspeed = -Enemy.MOVE_SPEED
            if heroy > selfy:
                self.yspeed = Enemy.MOVE_SPEED
            else:
                self.yspeed = -Enemy.MOVE_SPEED
                
            #Randomly decide to stop
            if random.random() < Enemy.STOP_PROBABILITY:
                self.xspeed = 0
                self.yspeed = 0
                self.wait_count = random.randint(20,60)
    
    def update(self):
        if self.state == Enemy.HIT:
            #If we started to get hit, start hit animation
            if self.prevstate != Enemy.HIT:
                self.current_animation = Enemy.s_hit_animation
                self.anim_timer = 0
            #Check if we are done getting hit
            if self.anim_timer == len(Enemy.s_hit_animation) * Enemy.s_hit_animation.animation_speed - 1:
                    self.state = Enemy.IDLE_OR_MOVING
        if self.state == Enemy.IDLE_OR_MOVING:
            self.moveUpdate(self.xspeed, self.yspeed)
            
        self.advanceAnimation()
        
        self.prevstate = self.state
        

class Hero(Mover):
    """The hero class."""
    #Movement speed in pixels per tick
    MOVE_SPEED = 2
    #The walking animation, tuple of tuples of surfaces and rects
    s_walk_animation = None
    s_punch_animation = None 
    s_idle_animation = None 
    #Possible states
    MOVING_OR_IDLE,PUNCHING = range(2)
    
    #HitBox is a Rect for punching in local coordinate space, defined
    #as if hero facing right
    PUNCH_HIT_BOX_IN_LOCAL = None
    
    
    def __init__(self):
        #Initialize static vars if first time
        if Hero.s_walk_animation == None:   
            Hero.s_walk_animation = Animation('hero_walk_',8)
            Hero.s_punch_animation = Animation('hero_punch_',8)
            Hero.s_idle_animation = Animation('hero_idle_',8)     
            
            Hero.PUNCH_HIT_BOX_IN_LOCAL = Rect(Hero.s_idle_animation[0].get_rect().width/2,
                                    Hero.s_idle_animation[0].get_rect().height/2,
                                    Hero.s_idle_animation[0].get_rect().width/2 + 10,
                                    20)
        
        #End initializing static vars
        
        #Call constructor of parent
        Mover.__init__(self,Hero.s_walk_animation,Hero.s_idle_animation)   
        
        #Holds the state
        self.state = Hero.MOVING_OR_IDLE

        
    def update(self):
        """Update the sprite based on 
        current sprite state - should be called after sending move commands"""
        
        """Decide which animation we should be in"""
        #check if we are punching
        if (self.state == Hero.PUNCHING):
            #start punching if we just started
            if (self.prevState != Hero.PUNCHING):
                self.current_animation = Hero.s_punch_animation
                self.anim_timer = 0
            else:
                #Check if we should stop punching animation (if we are at the end of the animation)
                if self.anim_timer == len(Hero.s_punch_animation) * Hero.s_punch_animation.animation_speed - 1:
                    #Go back to moving if we were moving before we started punching,
                    #Otherwise become IDLE
                    self.state = Hero.MOVING_OR_IDLE
                        
        #Now we might've started moving or being idle, so
        #check and update animation and position accordingly
        #using the parent's method
        if (self.state == Hero.MOVING_OR_IDLE):
            self.moveUpdate(self.xMove,self.yMove)         
                
        #Advance the animation
        self.advanceAnimation()
                
        #remember the state from this tick
        self.prevState = self.state
        
    def move(self,event_type,key):
        """
        event_type:KEYDOWN or KEYUP
        key: keyEvent this hero should respond to
        Move the hero and update state.
        Should be called before updating"""
        
        #Check if punch command issued, change state if not 
        #already punching
        if (event_type == KEYDOWN and key == K_z and
            self.state != Hero.PUNCHING):
            self.state = Hero.PUNCHING
            return
        
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

    @staticmethod        
    def punchDetector(hero,enemy):
        """
        Detects if a hero has punched an enemy
        """
        #Transform the recs to the global coordinate space
        transformed_punch_rec = Hero.PUNCH_HIT_BOX_IN_LOCAL.move(hero.rect.left,hero.rect.top)
        transformed_hit_rec = Enemy.HIT_BOX_IN_LOCAL.move(enemy.rect.left,enemy.rect.top)
        
        return hero.state == Hero.PUNCHING and transformed_punch_rec.colliderect(transformed_hit_rec)
        
        