'''
Created on Apr 29, 2012

Entry point for beatemup. Starts the main loop

@author: Kyle
'''
#TODO: Implement displaying the health bar of the last enemy that was hit,
#for a few ticks

import os, sys
import pygame
from beatemup.actors import *
from pygame.locals import *

class BeatEmUpMain:
    """The Main PyMan Class - This class handles the main 
    initialization and creating of the Game."""
    
    
    def __init__(self, width=640,height=480):
        #Our fields
        self.hero = None
        #Holds all of our sprites
        self.sprite_group = pygame.sprite.RenderPlain()
        self.enemy_sprite_group = pygame.sprite.RenderPlain()
        self.health_bar_group = pygame.sprite.RenderPlain()
        # clock for ticking
        self.clock = pygame.time.Clock()
        
        """Initialize"""
        """Initialize PyGame"""
        pygame.init()
        """Set the window Size"""
        self.width = width
        self.height = height
        """Create the Screen"""
        self.screen = pygame.display.set_mode((self.width
                                               , self.height))
        
        
    def LoadSprites(self):
        """Initialize all of the sprites we contain, add them
        to the overall sprite group"""
        self.hero = Hero()
        self.sprite_group.add(self.hero)
        #Make hero start in the center of the screen
        self.hero.setPosition((self.width/2,self.height/2))
        
        self.enemy = Enemy(self.width/2 + 20,self.height/2 + 20)
        self.enemy_sprite_group.add(self.enemy)
        
    def MainLoop(self):
        """This is the Main Loop of the Game"""
        
        """Load All of our Sprites"""
        self.LoadSprites()
        
        """Create the background"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((255,255,255))
        
        """INitialize UI related vars"""
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
            self.screen.blit(self.background, (0, 0))     
            
            #draw everything   
            self.sprite_group.draw(self.screen)
            self.enemy_sprite_group.draw(self.screen)
            self.health_bar_group.draw(self.screen)
            pygame.display.flip()        



#Code for starting the game
if __name__ == "__main__":
    main_window = BeatEmUpMain()
    main_window.MainLoop()