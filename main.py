# main.py

import pygame
import sys
from game import Game

def main():
    # Initialize pygame
    pygame.init()
    
    # Create game instance
    game = Game()
    running = True
    
    # Main game loop
    while running:
        # Handle events
        running = game.handle_events()
        
        # Update game state
        game.update()
        
        # Draw the game
        game.draw()
        
        # Cap the frame rate
        game.clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()