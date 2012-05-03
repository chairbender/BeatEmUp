'''
Created on Apr 30, 2012
For managing game state
@author: Kyle
'''
import os, sys
import pygame
from beatemup.actors import *
from pygame.locals import *
import xml.dom.minidom

"""
As a programmer, I want to specify a saved level file and have the user play it,
returning when the level is over, and letting me know the return state (did he win, die, or what)
"""

class Level(object):
    """
    A playable level. Has a background, a length,
    the positions of enemies, and the ability to play it
    """
    
    def __init__(self,screen,background_image):
        """
        Initialize the level, using the passed screen as the surface to draw on.
        For a level that is level_width pixels long (but only screen size portion displayed
        at a time)
        """
        self.screen = screen
        
        self.width = self.screen.get_rect().width
        self.height = self.screen.get_rect().height
        
        self.level_width = background_image.get_rect().width
        self.background = background_image
        
        #Our fields
        self.hero = None
        #Holds all of our sprites
        self.sprite_group = pygame.sprite.RenderPlain()
        self.enemy_sprite_group = pygame.sprite.RenderPlain()
        self.health_bar_group = pygame.sprite.RenderPlain()
        # clock for ticking
        self.clock = pygame.time.Clock()
        #The actual level surface
        self.level_surface = pygame.Surface((self.level_width,self.height))
        
    def addActor(self,actor):
        """
        adds the passed actor to the level.
        """
        self.enemy_sprite_group.add(actor)
        
    def play(self):
        """
        play the level, returning when hero dead or wins
        """        
        self.p_initializePlay()
        
        """Initialize UI related vars"""
        #For showing/hiding the enemy's health bar when they get hit
        enemy_bar_timer = 0               
        #Last enemy hit
        last_enemy = None                       
        #Rect where hero health bar will go
        hero_healthbar_rect = Rect(5,5,self.width/4,self.height/16)        
        #Position on the screen where the enemy health bar will be
        enemy_healthbar_rect = Rect(self.width*(3.0/4) - 5,5,self.width - self.width*(3.0/4), self.height/16)
        #How long to wait till hiding the bar for an enemy
        ENEMY_HEALTHBAR_HIDE_TIME = 120
        #track how far the level is scrolled horizontally
        level_scroll = 0
        
        
        """Main loop"""
        while 1:
            #Advance clock
            self.clock.tick(60)
            
            """Let all sprites move"""
            #Let player move
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                elif event.type == KEYDOWN or event.type == KEYUP:
                    self.hero.move(event.type, event.key)
             
            #Let AI actors move
            for enemy in self.enemy_sprite_group:
                enemy.doMove(self.hero)
                                            
            """Check for collisions"""
            #keep all sprites into the movement area (the bottom half of the screen)
            for group in self.sprite_group, self.enemy_sprite_group:
                for sprite in group:
                    sprite.rect.top = max(self.height/2,sprite.rect.top)
                    sprite.rect.bottom = min(self.height,sprite.rect.bottom)
            
            #If the hero goes left or right outside the screen, scroll left or right
            #if not out of level bounds
            if self.hero.rect.right > self.width + level_scroll:
                #If out of level bounds, stop
                self.hero.rect.right = min(self.hero.rect.right,self.level_width)
                level_scroll += self.hero.rect.right - (self.width + level_scroll)
            elif self.hero.rect.left < level_scroll:
                #if out of bounds, stop
                self.hero.rect.left = max(self.hero.rect.left,0)
                level_scroll += self.hero.rect.left - level_scroll
            #Will hold the last enemy hit
            #Check for collisions between punching player and enemy and resolve
            #Track whether we hit an enemy
            enemy_hit = False
            punched_enemy_list = pygame.sprite.spritecollide(self.hero, self.enemy_sprite_group, False, Fighter.checkPunches)
            for enemy in punched_enemy_list:
                last_enemy = enemy
                enemy_bar_timer = ENEMY_HEALTHBAR_HIDE_TIME
                enemy_hit = True
                enemy.getPunched(self.hero)
            #Check for player getting punched and resolve (only can get punched 1ce per tick
            for enemy in self.enemy_sprite_group:
                if pygame.sprite.spritecollide(enemy, self.sprite_group, False, Fighter.checkPunches):
                    self.hero.getPunched(enemy)
                    break

            """Let everything update"""
            self.hero.update()
            self.enemy_sprite_group.update()
            
            #Update the health bars
            #If no enemy was hit, count down the healthbar hide time and stop showing the
            #enemy health if it reaches zero
            if not enemy_hit:
                enemy_bar_timer -= 1
                if enemy_bar_timer == 0:
                    #set this to none so the healthbar won't be drawn this tick
                    last_enemy = None
            #Refresh the health bar group (might be slow, TODO)
            self.health_bar_group.empty()
            self.health_bar_group.add(self.hero.getHealthBar(hero_healthbar_rect))
            #Only show health bar if there
            if last_enemy != None:
                self.health_bar_group.add(last_enemy.getHealthBar(enemy_healthbar_rect))

            
            """Draw all sprites"""
            #Blit the screen with our black background
            self.level_surface.blit(self.background, (0, 0))    
             
            #draw sprites
            self.sprite_group.draw(self.level_surface)
            self.enemy_sprite_group.draw(self.level_surface)
            
            viewport = self.level_surface.subsurface(Rect(level_scroll,0,self.width,self.height))
            #Draw UI
            self.health_bar_group.draw(viewport)
            
            #Now put it on the screen
            self.screen.blit(viewport,(0,0))
            pygame.display.flip()      
        
    
    def p_initializePlay(self):
        """
        Initialize all the stuff before going into the main loop
        """
        self.p_loadSprites()
        

    def p_loadSprites(self):
        """Initialize all of the sprites we contain, add them
        to the overall sprite group"""
        self.hero = Hero()
        self.sprite_group.add(self.hero)
        #Make hero start in the center of the screen
        self.hero.setPosition((self.width/2,self.height/2))
        
    @staticmethod
    def loadLevelFromFile(self,screen,level_file_name):
        """
        Load level saved in the .lev XML format and return it
        The format is described in level_format.txt        
        level_file_name should be the name of the .xml file in the levels folder
        """
        
        
        fullname = os.path.join('..\\','levels')
        fullname = os.path.join(fullname, level_file_name)
        level_file = xml.dom.minidom.parse(fullname)
        #Get the background image
        for level in level_file.getElementsByTagName('Level'):
            level_background = level.attributes["background"].value
        #Load the background image
        fullname = os.path.join('..\\','backgrounds')
        fullname = os.path.join(fullname, level_background)
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print 'Cannot load image:', fullname
            raise SystemExit, message
        image = image.convert()
        
        #Can now create the level object
        result_level = Level(screen,image)
        
        #Now add enemies
        for enemy in level_file.getElementsByTagName('Enemy'):
            x = int(enemy.attributes['x'].value)
            y = int(enemy.attributes['y'].value)
            new_enemy = Enemy(x,y)
            result_level.addActor(new_enemy)
        
        return result_level
        
        