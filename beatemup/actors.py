'''
Created on Apr 29, 2012

@author: Kyle
'''
#TODO: Finish refactoring implementing Fighter class

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
        self.sprite_frames = getAnimation(image_prefix,True)
    
    def __getitem__(self,index):
        return self.sprite_frames[index]
    
    def __len__(self):
        return len(self.sprite_frames)
    
class HealthBar(pygame.sprite.Sprite):
    """
    Represents a bar that is given a min, max and current value
    and is drawn based on that
    """
    
    name_font = None
    
    def __init__(self,left,top,min_value,max_value,cur_value,width,height,font_name="Health"):
        pygame.sprite.Sprite.__init__(self) 
        
        #Initialize static
        if HealthBar.name_font == None:
            name = os.path.join('..\\','fonts')
            name = os.path.join(name,'shooting_dutchy.ttf')
            HealthBar.name_font = pygame.font.Font(name, 12)
        
        self.min_value = min_value
        self.max_value = max_value
        self.cur_value = cur_value
        self.width = width
        self.height = height
        self.name = font_name
        
        #Position in global coordinates
        self.rect = Rect(left,top,width,height)
        
        self.p_updateImage()
        
    def p_updateImage(self):
        """
        Update the image of the healthbar
        """
        newImage = pygame.Surface((self.width,self.height*2))
        
        #Draw the border
        pygame.draw.rect(newImage, pygame.Color(235,227,12), \
            Rect(0,0,self.width,self.height))
        
        #Draw the health part
        pygame.draw.rect(newImage,pygame.Color(255,23,23), \
                         Rect(4,4,(self.width-8)*(float(self.cur_value)/self.max_value),self.height-8))
        
        #Draw the text
        text = HealthBar.name_font.render(self.name, 1, pygame.Color(127, 10, 10), pygame.Color(255,255,255))
        newImage.blit(text,Rect(0,self.height,1,1))
        
        #Update the image
        newImage.set_colorkey((0,0,0))
        self.image = newImage
    
    def setValue(self,new_value):
        """
        CHanges the value and updates the sprite image
        """
        self.cur_value = new_value
        self.p_updateImage()
        
class Shadow(pygame.sprite.Sprite):
    """
    Represents a shadow - a black transparent oval
    """
    
    def __init__(self,area_rect):
        """
        Create a oval shadow filling in the area_rect
        """
        pygame.sprite.Sprite.__init__(self) 
        
        self.rect = area_rect
        self.image = pygame.Surface((area_rect.width,area_rect.height))
        
        #shadow
        pygame.draw.ellipse(self.image,Color(25,25,25),Rect(0,0,area_rect.width,area_rect.height))
        self.image.set_colorkey((0,0,0))
        self.image.set_alpha(100)
        
            
class Mover(pygame.sprite.Sprite):
    """Class for a sprite that moves and animates
    Subclasses can call moveUpdate to set the image
    and rect for this sprite, and 
    advanceAnimation to handle updating the sprite
    based on the current animation
    """
    IDLE, MOVING = range(2)
    #Scaling of y velocity due to high viewing angle
    YSCALE = .8
    
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
        
        #Direciton being faced (1 for right, -1 for left)
        self.facing_right = True      
        
        #Initialize our rect and image
        self.image, self.rect = (self.idle_animation[0],\
                                 self.idle_animation[0].get_bounding_rect())
        
        #How many ticks have elapsed since the restart of the current animation     
        self.anim_timer = 0
        
        
    def facePosition(self,faceX):
        """
        Turn to face the given position (overridden by movement)
        """
        self.facing_right = faceX > self.rect.centerx
        
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
            self.rect.move_ip(xMove,yMove*Mover.YSCALE)
            if xMove > 0:
                self.facing_right = True
            elif xMove < 0:
                self.facing_right = False
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
        if self.facing_right:
            self.image = self.current_animation[anim_index]
        else:
            self.image = flip(self.current_animation[anim_index], True, False)

class Fighter(Mover):
    """
    Base class for a sprite that moves, punches and gets hit.
    Also has health. Override those methods to change its stats
    """
    
    #Default health for a fighter
    DEFAULT_HEALTH = 100
    DEFAULT_DAMAGE = 5
    #How many pixels to fly back when hit
    FLY_BACK_DISTANCE = 80
    #How many pixels to move back each tick when getting knocked back
    FLY_BACK_SPEED = 2
    
    #How long to stay lying down when knocked down
    RECOVERY_TIME = 100
    
    #How long a window after an attack finishes that
    #attacking again continues the combo
    COMBO_WINDOW = 30
    
    #States
    IDLE_OR_MOVING,PUNCHING,GETTING_HIT,FLYING_BACK,FALLEN,DEAD = range(6)
    
    def __init__(self,walk_animation,idle_animation,hit_animation,fallen_animation,combo_animations,
                 name="Fighter",max_health=100):
        Mover.__init__(self,walk_animation,idle_animation)
        
        #Our animations
        self.hit_animation = hit_animation
        self.fallen_animation = fallen_animation
        #An array that is looped through to do combos
        self.combo_animations = combo_animations
        
        #Our saved state
        #Whether we are in the middle of a one time animation like getting hit or punching
        self.curState = Fighter.IDLE_OR_MOVING        
                
        #Track health
        self.health = max_health
        
        self.name = name
        
        self.max_health = max_health    
        
        #if we got hit this tick, and if we got launched
        self.start_hit = False
        self.start_getting_launched = False    
                
        #For tracking combos
        self.consecutive_punches = 0
        #counts time allowed between attacks in a combo - 
        self.punch_combo_timer = Fighter.COMBO_WINDOW
        self.started_punch = False
        self.is_launching = False #whether current punch is a launcher
        #Whether hit has landed this step of the combo
        self.hit_landed_for_combo = False
        #Amount of ticks elapsed since the fighter started flying back after getting
        #hit a bunch
        self.fly_back_ticks = 0
        #Track how long fighter has lied on the ground after being knocked down
        self.fallen_ticks = 0
        #Track the position on the ground when airborne
        self.groundTop = self.rect.top
        
    def getShadow(self):
        """
        Return a sprite representing the fighter's shadow for this tick
        (becomes invalid next tick)
        """
        if self.isAirborne():
            return Shadow(Rect(self.rect.left,self.groundTop + self.rect.height/2 + self.rect.height/4,self.rect.width,self.rect.height/2))
        else:
            return Shadow(Rect(self.rect.left,self.rect.top,self.rect.width,self.rect.height))
        
        
    def getHealthBar(self,rect_position):
        """
        Return a healthbar representing the current
        state of the fighter, positioned at the passed rect in global coordinates
        """
        return HealthBar(rect_position.left,rect_position.top,0,self.getMaxHealth(),self.getHealth(), \
                         rect_position.width,rect_position.height,self.getName())
        
    def getName(self):
        """
        Return the name of this actor, meant to be overridden
        """
        return self.name
    
    def isAirborne(self):
        """
        Return whether this enemy is in the air or not
        """
        return self.curState == Fighter.FLYING_BACK

    def getHealth(self):
        """
        Return remaining health (self.health)
        """
        return self.health
    
    def getPunched(self,enemy_fighter):
        """
        Default behavior is to set the
        self.start_hit flag and take damage
        if not already being hit. also deal with getting launchedsubclasses can
        use the self.start_hit flag in their update
        method, or override this
        """
        self.start_hit = True
        if enemy_fighter.isLaunching():
            self.start_getting_launched = True
        #Let enemy know hit landed this tick
        enemy_fighter.notifyHitLanded()        
        self.takeHit(enemy_fighter)
        
    def notifyHitLanded(self):
        """
        Notify hit landed so combo can continue
        """
        self.hit_landed_for_combo = True
    
    def getMaxHealth(self):
        """
        Return the max health of the actor
        """
        return self.max_health
    
    def takeHit(self,fighter_attacker):
        """
        Reduce health as if fighter_attacker hit
        this fighter
        """
        self.health -= fighter_attacker.getDamage()
        
    def getDamage(self):
        """
        Amount of damage done when this fighter punches something
        """
        return Fighter.DEFAULT_DAMAGE
        
    def isPunching(self):
        return self.curState == Fighter.PUNCHING
    
    def isLaunching(self):
        """
        Return true if this fighter is punching and is
        at the end of the combo
        """
        return self.is_launching
    
    def startedPunching(self):
        """
        Return whether the puncher has just initiated a punch
        """
        return self.started_punch
    
    def isGettingHit(self):
        return self.curState == Fighter.GETTING_HIT
        
    def updateMovePunchHit(self,xMove,yMove,bool_start_punch):
        """
        updates state, animations and position
        move based on the passed speed, also process punching
        and getting hit based on those boolean parameters
        """           
        #If we are getting knocked back, don't do anything else, just 
        #fly back in an arc
        if self.curState == Fighter.FLYING_BACK:
            
            #Should horizontally always move the same speed
            xMove = Fighter.FLY_BACK_SPEED
            #Should follow an arc - use equation for parabolic motion,
            #with peak = to half the distance
            #calc how many ticks it will take, in total, till the distance is reached
            end_ticks = Fighter.FLY_BACK_DISTANCE / Fighter.FLY_BACK_SPEED
            gravity = .5
            initial_velocity = -gravity*end_ticks/2
            yMove = initial_velocity + gravity*self.fly_back_ticks
            
            #actually move the fighter
            if self.facing_right:
                self.rect.move_ip(-xMove,yMove)
            else:
                self.rect.move_ip(xMove,yMove) 
            
            #increment the fly back timer
            self.fly_back_ticks += 1
            #if done, reset state
            if self.fly_back_ticks * Fighter.FLY_BACK_SPEED > Fighter.FLY_BACK_DISTANCE:
                self.curState = Fighter.FALLEN
                self.fallen_ticks = 0
        elif self.curState == Fighter.FALLEN:
            #Stay lying down and wait for timer to expire
            self.fallen_ticks += 1
            if self.fallen_ticks == Fighter.RECOVERY_TIME:
                #Check if dead
                if self.health <= 0:
                    self.curState = Fighter.DEAD
                else:
                    self.curState = Fighter.IDLE_OR_MOVING 
        elif self.curState == Fighter.DEAD:
            #Do nothing
            return
        elif self.health <= 0:
            #Start getting knocked back if not already
            if self.curState != Fighter.FLYING_BACK:
                self.curState = Fighter.FLYING_BACK
                self.fly_back_ticks = 0            
                self.current_animation = self.fallen_animation
                self.groundTop = self.rect.top 
                return               
        else:       
            #Clear the started_punch flag and launcher flag if we are past the first tick of the punch
            if self.started_punch and self.curState == Fighter.PUNCHING:
                self.started_punch = False
                self.is_launching = False
            
            #Count up the combo timer
            self.punch_combo_timer += 1
    
            #If we started to get hit, start hit animation. Can enter this at any time
            if self.start_hit:
                #If we are suposed to go flying, do so
                if self.start_getting_launched:
                    self.start_getting_launched = False
                    self.curState = Fighter.FLYING_BACK
                    self.fly_back_ticks = 0            
                    self.current_animation = self.fallen_animation
                    self.groundTop = self.rect.top 
                    return     
                else:
                    self.consecutive_hits = 0
                self.current_animation = self.hit_animation
                self.curState = Fighter.GETTING_HIT
                self.anim_timer = 0
            #start punching if we just started and aren't already animating
            if bool_start_punch and self.curState != Fighter.PUNCHING and self.curState != Fighter.GETTING_HIT:
                #Check if the combo timer hasn't expired
                if self.punch_combo_timer < Fighter.COMBO_WINDOW and self.hit_landed_for_combo and self.consecutive_punches < len(self.combo_animations)-1:
                    #increment combo counter
                    self.consecutive_punches += 1
                    #if we are at the end of the combo, 
                    #launch
                    if self.consecutive_punches == len(self.combo_animations)-1:
                        self.is_launching =True
                    
                else:
                    #Otherwise, reset it
                    self.consecutive_punches = 0
                    self.hit_landed_for_combo = False
                    self.is_launching = False
                self.current_animation = self.combo_animations[self.consecutive_punches]
                self.curState = Fighter.PUNCHING
                self.started_punch = True
                self.anim_timer = 0
            #Check if we have finished animations if we are in a one time animation
            if  (self.curState == Fighter.PUNCHING or self.curState == Fighter.GETTING_HIT) and \
                self.anim_timer == len(self.current_animation) * self.current_animation.animation_speed - 1:
                #become idle
                self.curState = Fighter.IDLE_OR_MOVING
                #Start combo timer
                self.punch_combo_timer = 0
                    
            #Move if we aren't doing something else (or do idle anim)
            if self.curState == Fighter.IDLE_OR_MOVING:
                self.moveUpdate(xMove, yMove)
            
        self.advanceAnimation()
        
    def getPunchRect(self):
        """
        get the rect in global coordinates that represents the hitbox
        of where the punch is
        """
        #Default to a little ahead of wherever they are facing, with a little band
        rightrect = Rect(self.rect.right,
                                    self.rect.centery,
                                    1,
                                    1)
        #Flip across centerx if facing left
        if self.facing_right:
            return rightrect
        else:
            return Rect(self.rect.centerx - rightrect.width - (rightrect.left - self.rect.centerx),
                                     rightrect.top, rightrect.width, rightrect.height)

    
    def getHitBox(self):
        """
        get the rect in global coordinates that represents the place
        where this sprite can get punched
        """
        #Default to a little span near the midsection
        return Rect(self.rect.left,self.rect.centery,
                                         self.rect.width,20)
    
    @staticmethod
    def checkPunches(fighter_puncher,fighter_target):
        """
        Use the fighters punchRect and hitboxes to check if puncher
        hits target (for use with spritecollide)
        """
        #Only return true if the punch JUST started

        return fighter_puncher.startedPunching() and fighter_puncher.getPunchRect().colliderect(fighter_target.getHitBox())
        
class Enemy(Fighter):
    """Enemy that moves sporadically towards
    player"""
    
    MOVE_SPEED = 1
    #Probability of stopping and waiting for a few ticks
    STOP_PROBABILITY = .010
    #Rect for getting punched
    HIT_BOX_IN_LOCAL = None
    #How long to wait before punching when in position
    PUNCH_DELAY = 45
    
    #States for punching
    NOT_READY,READYING_PUNCH = range(2)
    
    
    s_walk_animation = None
    s_hit_animation = None 
    s_idle_animation = None 
    s_punch_animation = None
    s_fallen_animation = None
    
    def __init__(self, xPos, yPos):
        #Initialize static vars if first time
        if Enemy.s_walk_animation == None:   
            Enemy.s_walk_animation = Animation('roger_walk_',8)
            Enemy.s_hit_animation = Animation('roger_hit_',20)
            Enemy.s_idle_animation = Animation('roger_idle_',8)  
            Enemy.s_punch_animation = Animation('roger_punch_',8) 
            Enemy.s_fallen_animation = Animation('roger_fallen_',8)
              
            Enemy.HIT_BOX_IN_LOCAL = Rect(0,Enemy.s_idle_animation[0].get_rect().height/2,
                                         Enemy.s_idle_animation[0].get_rect().width,20)
            
            
        Fighter.__init__(self,Enemy.s_walk_animation,Enemy.s_idle_animation,Enemy.s_hit_animation,Enemy.s_fallen_animation,
                         [Enemy.s_punch_animation,Enemy.s_punch_animation],
                         "Enemy",50)   
        
        #Set position
        self.rect.move_ip(xPos,yPos)
        
        #Number of ticks to wait before moving again
        self.wait_count = 0
        self.punch_wait_count = 20
        
        #Flags for tracking punching and hitting
        self.start_hit = self.bool_start_punch = False
        
        #Flag for tracking getting ready to punch
        self.state = Enemy.NOT_READY
            
    def doMove(self,hero):
        """
        choose what to do based on the position of the Hero
        """
        #Calculate coordinates for destination and slack
        selfx, selfy = self.rect.centerx, self.rect.centery
        #How much slack to give for going to that position (so it doesn't spaz out trying to stay
        #exactly on the dest)
        slackx = slacky = 8
        desty = hero.rect.centery
        #If hero is to our left, get in front of their right side,
        #otherwise left
        if hero.rect.centerx < selfx:
            destx = hero.rect.right + self.rect.width/4
        else:
            destx = hero.rect.left - self.rect.width/4
        
        #Check if we are currently waiting
        if self.wait_count > 0:
            self.wait_count -= 1
            self.xspeed = self.yspeed = 0
        #Check if we are in position in front of player
        elif destx > selfx - slackx and destx < selfx + slackx and \
            desty > selfy - slacky and desty < selfy + slacky:
            #Don't move
            self.xspeed = self.yspeed = 0
            #Face the hero
            self.facePosition(hero.rect.centerx)
            #If we just got in range, start the punch countdown
            if self.state == Enemy.NOT_READY:
                self.state = Enemy.READYING_PUNCH
                self.punch_wait_count = Enemy.PUNCH_DELAY
            #decrement punch wait count
            self.punch_wait_count -= 1
            #Check if we are done waiting to punch
            if self.punch_wait_count == 0:
                self.bool_start_punch = True
                self.punch_wait_count = Enemy.PUNCH_DELAY            
        else:            
            #We aren't in position
            self.state = Enemy.NOT_READY
            #Move to destination position    
            if destx > selfx:
                self.xspeed = Enemy.MOVE_SPEED
            elif destx < selfx:
                self.xspeed = -Enemy.MOVE_SPEED
            if desty > selfy:
                self.yspeed = Enemy.MOVE_SPEED
            elif desty < selfy:
                self.yspeed = -Enemy.MOVE_SPEED
                
            #Randomly decide to stop
            if random.random() < Enemy.STOP_PROBABILITY:
                self.xspeed = 0
                self.yspeed = 0
                self.wait_count = random.randint(20,60)
    
    def update(self):
        self.updateMovePunchHit(self.xspeed, self.yspeed, self.bool_start_punch)
        #clear flags
        self.start_hit = self.bool_start_punch = False
        

class Hero(Fighter):
    """The hero class."""
    #Health
    MAX_HEALTH = 100
    #Damage taken by punches
    GET_PUNCH_DAMAGE = 5
    #Movement speed in pixels per tick
    MOVE_SPEED = 2
    #The walking animation, tuple of tuples of surfaces and rects
    s_walk_animation = None
    s_punch_animation = None
    s_punch2_animation = None
    s_punch3_animation = None 
    s_idle_animation = None
    s_fallen_animation = None 
    
    #HitBox is a Rect for punching in local coordinate space, defined
    #as if hero facing right
    PUNCH_HIT_BOX_IN_LOCAL = None
    
    
    def __init__(self):
        #Initialize static vars if first time
        if Hero.s_walk_animation == None:   
            Hero.s_walk_animation = Animation('doug_walk_',8)
            Hero.s_punch_animation = Animation('doug_punch_',8)
            Hero.s_punch2_animation = Animation('doug_punch2_',8)
            Hero.s_punch3_animation = Animation('doug_punch3_',8)
            Hero.s_idle_animation = Animation('doug_idle_',10)
            Hero.s_hit_animation = Animation('doug_hit_',15)
            Hero.s_fallen_animation = Animation('doug_fallen_',8)         
            
            Hero.PUNCH_HIT_BOX_IN_LOCAL = Rect(Hero.s_idle_animation[0].get_rect().width/2,
                                    Hero.s_idle_animation[0].get_rect().height/2,
                                    Hero.s_idle_animation[0].get_rect().width/2 + 10,
                                    20)
        
        #End initializing static vars
        
        #Call constructor of parent
        Fighter.__init__(self,Hero.s_walk_animation,Hero.s_idle_animation,Hero.s_hit_animation,Hero.s_fallen_animation,
                         [Hero.s_punch_animation,Hero.s_punch2_animation,Hero.s_punch_animation,Hero.s_punch3_animation],
                         "Hero",100)   
        
        #Flags for starting animations
        self.start_punch = self.start_hit = False
    
    def update(self):
        """Update the sprite based on 
        current sprite state - should be called after sending move commands"""
        self.updateMovePunchHit(self.xMove, self.yMove, self.start_punch)
        
        #Reset the animation starting flags  
        self.start_punch = self.start_hit = False
             
        
    def move(self,event_type,key):
        """
        event_type:KEYDOWN or KEYUP
        key: keyEvent this hero should respond to
        Move the hero and update state.
        Should be called before updating"""
        
        #Check if punch command issued, change state if not 
        #already punching
        if (event_type == KEYDOWN and key == K_z and
            not self.isPunching()):
            self.start_punch = True
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

        
        