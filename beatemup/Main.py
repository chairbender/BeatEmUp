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
from beatemup.game import *
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
        
        level = Level(self.screen,1024)
        level.play()
        
#Code for starting the game
if __name__ == "__main__":
    main_window = BeatEmUpMain()