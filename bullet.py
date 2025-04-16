import pygame
import math
import game
from constants import BLACK


class Bullet:
    """Base class for all projectiles"""
    def __init__(self, x, y, dx, dy, damage):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = 5
        self.radius = 3
        self.damage = damage
        self.color = BLACK
    
    def update(self):
        """Update bullet position"""
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
    
    def draw(self, screen):
        """Draw the bullet"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    
    def is_off_screen(self, screen_width, screen_height):
        """Check if bullet is outside the screen"""
        return (self.x < 0 or self.x > screen_width or 
                self.y < 0 or self.y > screen_height)


class FrostBullet(Bullet):
    """Bullet that slows enemies"""
    def __init__(self, x, y, dx, dy, damage, slow_factor):
        super().__init__(x, y, dx, dy, damage)
        self.slow_factor = slow_factor
        self.color = (173, 216, 230)  # Light blue
        self.radius = 4  # Slightly bigger
    
    def apply_effect(self, enemy):
        """Apply slowing effect to enemy"""
        enemy.speed *= self.slow_factor
        enemy.slowed_timer = 180  # Slow effect lasts for 3 seconds
        return self.damage


class SplashBullet(Bullet):
    """Bullet that deals area damage"""
    def __init__(self, x, y, dx, dy, damage, splash_radius):
        super().__init__(x, y, dx, dy, damage)
        self.splash_radius = splash_radius
        self.color = (255, 140, 0)  # Orange
        self.radius = 5  # Bigger bullet
    
    def draw(self, screen):
        """Draw the splash bullet"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Optional: show splash radius when debugging
        # pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
        #                   self.splash_radius, 1)
    
    def apply_splash_damage(self, enemies, game):
        """Apply damage to all enemies in splash radius"""
        for enemy in enemies[:]:  # Copy list to avoid modification issues
            dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
            if dist < self.splash_radius:
                # Calculate damage falloff based on distance (optional)
                damage_factor = 1 - (dist / self.splash_radius) * 0.5
                actual_damage = self.damage * damage_factor
                
                enemy.health -= actual_damage
                
                # Check if enemy died
                if enemy.health <= 0 and enemy in enemies:
                    enemies.remove(enemy)
                    game.money += enemy.reward