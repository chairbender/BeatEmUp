'''
Created on Apr 30, 2012
For managing game state
@author: Kyle
'''


import os, sys
import pygame
from beatemup.actors import *
from pygame.locals import *

class GameState(object):
    """
    Tracks the state of the whole game
    """
    
    def __init__(self, prev=None):
        """
        prev: previous state
        """
        
        if prev != None:
            self.hero_position = prev.hero_position
        else:
            #The position of the hero
            self.hero_position = None