'''
Created on Apr 29, 2012

Entry point for beatemup. Starts the main loop

@author: Kyle
'''

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
    
    def MainLoop(self):
        """This is the Main Loop of the Game"""
        
        """Load All of our Sprites"""
        self.LoadSprites()
        
        """Create the background"""
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((255,255,255))
        
        while 1:
            #Advance clock
            self.clock.tick(60)
            
            """Let all sprites move"""
            #Let player move
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                elif event.type == KEYDOWN or event.type == KEYUP:
                    if ((event.key == K_RIGHT)
                    or (event.key == K_LEFT)
                    or (event.key == K_UP)
                    or (event.key == K_DOWN)):
                        self.hero.move(event.type, event.key)
                        
            #Let AI actors move
            
            """Let everything update"""
            self.hero.update()
            
            """Draw all sprites"""
            #Blit the screen with our black background
            self.screen.blit(self.background, (0, 0))     
            
            #draw everything   
            self.sprite_group.draw(self.screen)
            pygame.display.flip()        



#Code for starting the game
if __name__ == "__main__":
    main_window = BeatEmUpMain()
    main_window.MainLoop()