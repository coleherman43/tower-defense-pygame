import pygame
from constants import GRID_SIZE, RED, BLACK, GREEN
import math

class Enemy:
    def __init__(self, x, y, enemy_type, path):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.path = path
        self.current_waypoint = 1  # Start moving toward the second waypoint
        self.radius = GRID_SIZE // 3
        self.speed = 1.5
        
        # Enemy properties based on type
        if enemy_type == "basic":
            self.color = RED
            self.health = 30
            self.max_health = 30
            self.reward = 10
            self.damage = 1
        elif enemy_type == "fast":
            self.color = (255, 165, 0)  # Orange
            self.health = 15
            self.max_health = 15
            self.speed = 3
            self.reward = 15
            self.damage = 1
        elif enemy_type == "tank":
            self.color = (139, 69, 19)  # Brown
            self.health = 100
            self.max_health = 100
            self.speed = 0.8
            self.reward = 25
            self.damage = 3
    
    def update(self):
        if self.current_waypoint < len(self.path):
            # Move toward the current waypoint
            target_x, target_y = self.path[self.current_waypoint]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < self.speed:
                # Reached waypoint, move to next
                self.x = target_x
                self.y = target_y
                self.current_waypoint += 1
            else:
                # Move toward waypoint
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
    
    def draw(self, screen):
        # Draw enemy
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)  # Border
        
        # Draw health bar
        health_ratio = self.health / self.max_health
        health_bar_width = GRID_SIZE
        pygame.draw.rect(screen, RED, (int(self.x - health_bar_width // 2), int(self.y - self.radius - 8), 
                                       health_bar_width, 5))
        pygame.draw.rect(screen, GREEN, (int(self.x - health_bar_width // 2), int(self.y - self.radius - 8), 
                                         int(health_bar_width * health_ratio), 5))