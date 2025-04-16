import pygame
import math

# Constants (could be imported from a constants.py file)
GRID_SIZE = 40
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

class BaseTower:
    """Base class for all towers"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 150
        self.damage = 10
        self.fire_rate = 60  # Frames between shots
        self.fire_timer = 0
        self.color = BLUE
        self.type = "base"  # For identification
        self.cost = 100
        self.level = 1
        self.max_level = 3
    
    def update(self, enemies, bullets):
        """Update tower state and attack enemies"""
        # Decrease fire timer
        if self.fire_timer > 0:
            self.fire_timer -= 1
        
        # Find the closest enemy in range
        target = self.find_target(enemies)
        
        # Fire at the target if possible
        if target and self.fire_timer <= 0:
            self.fire_at(target, bullets)
            self.fire_timer = self.fire_rate
    
    def find_target(self, enemies):
        """Find suitable target within range"""
        target = None
        min_dist = float('inf')
        
        for enemy in enemies:
            dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
            if dist < self.range and dist < min_dist:
                target = enemy
                min_dist = dist
        
        return target
    
    def fire_at(self, target, bullets):
        """Create a bullet aimed at the target"""
        # Calculate direction
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        
        # Create a bullet (assuming Bullet class is imported)
        from bullet import Bullet
        bullets.append(Bullet(self.x, self.y, dx, dy, self.damage))
    
    def draw(self, screen):
        """Draw the tower"""
        pygame.draw.circle(screen, self.color, (self.x, self.y), GRID_SIZE // 2)
        pygame.draw.circle(screen, BLACK, (self.x, self.y), GRID_SIZE // 2, 2)  # Border
    
    def upgrade(self):
        """Upgrade the tower if possible"""
        if self.level < self.max_level:
            self.level += 1
            self.damage *= 1.5
            self.range *= 1.2
            return True
        return False
    
    def get_upgrade_cost(self):
        """Calculate cost to upgrade"""
        return self.cost * self.level

    @classmethod
    def get_tower_types(cls):
        """Return list of available tower types"""
        return {
            "basic": BasicTower,
            "sniper": SniperTower,
            "machine_gun": MachineGunTower,
            "frost": FrostTower,
            "splash": SplashTower
        }
    
    @classmethod
    def create_tower(cls, tower_type, x, y):
        """Factory method to create a tower"""
        tower_classes = cls.get_tower_types()
        if tower_type in tower_classes:
            return tower_classes[tower_type](x, y)
        else:
            return BasicTower(x, y)  # Default


class BasicTower(BaseTower):
    """Standard balanced tower"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "basic"
        self.color = BLUE
        self.damage = 10
        self.range = 150
        self.fire_rate = 60
        self.cost = 100


class SniperTower(BaseTower):
    """Long-range high-damage tower with slow fire rate"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "sniper"
        self.color = (0, 100, 0)  # Dark green
        self.damage = 30
        self.range = 250
        self.fire_rate = 120
        self.cost = 150


class MachineGunTower(BaseTower):
    """Fast-firing low-damage tower"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "machine_gun"
        self.color = (100, 100, 100)  # Gray
        self.damage = 5
        self.range = 120
        self.fire_rate = 20
        self.cost = 200


class FrostTower(BaseTower):
    """Tower that slows enemies"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "frost"
        self.color = (173, 216, 230)  # Light blue
        self.damage = 5
        self.range = 130
        self.fire_rate = 45
        self.slow_factor = 0.5
        self.cost = 175
    
    def fire_at(self, target, bullets):
        """Create a frost bullet that slows enemies"""
        # Calculate direction
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        
        # Create a frost bullet
        from bullet import FrostBullet
        bullets.append(FrostBullet(self.x, self.y, dx, dy, self.damage, self.slow_factor))
    
    def upgrade(self):
        """Override upgrade to also improve slow factor"""
        if super().upgrade():
            self.slow_factor *= 0.8  # Stronger slowing effect (lower is slower)
            return True
        return False


class SplashTower(BaseTower):
    """Tower that deals area damage"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "splash"
        self.color = (255, 140, 0)  # Orange
        self.damage = 15
        self.range = 140
        self.fire_rate = 80
        self.splash_radius = 50
        self.cost = 225
    
    def fire_at(self, target, bullets):
        """Create a splash bullet with area effect"""
        # Calculate direction
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            dx /= dist
            dy /= dist
        
        # Create a splash bullet
        from bullet import SplashBullet
        bullets.append(SplashBullet(self.x, self.y, dx, dy, self.damage, self.splash_radius))
    
    def upgrade(self):
        """Override upgrade to also improve splash radius"""
        if super().upgrade():
            self.splash_radius *= 1.3
            return True
        return False