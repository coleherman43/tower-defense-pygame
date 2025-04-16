import pygame
import math
from constants import *

# Initialize pygame
pygame.init()

from tower import BaseTower
from enemy import Enemy

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.state = GAME_RUNNING
        self.money = 300
        self.lives = 20
        self.wave = 1
        self.towers = []
        self.enemies = []
        self.bullets = []
        self.spawn_timer = 0
        self.next_enemy = 0
        self.wave_in_progress = False
        self.selected_tower_type = "basic"
        
        # Define the path as a list of waypoints (x, y) - center points of the path tiles
        self.path = [
            (0, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4),
            (SCREEN_WIDTH // 2, 3 * SCREEN_HEIGHT // 4),
            (3 * SCREEN_WIDTH // 4, 3 * SCREEN_HEIGHT // 4),
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH, SCREEN_HEIGHT // 2)
        ]
        
    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (SCREEN_WIDTH, y))
    
    def draw_path(self):
        if len(self.path) > 1:
            for i in range(len(self.path) - 1):
                start = self.path[i]
                end = self.path[i + 1]
                pygame.draw.line(self.screen, YELLOW, start, end, GRID_SIZE // 2)
                pygame.draw.circle(self.screen, YELLOW, start, GRID_SIZE // 4)
            pygame.draw.circle(self.screen, YELLOW, self.path[-1], GRID_SIZE // 4)
    
    def can_place_tower(self, pos):
        # Check if position is on the grid
        grid_x = pos[0] // GRID_SIZE * GRID_SIZE + GRID_SIZE // 2
        grid_y = pos[1] // GRID_SIZE * GRID_SIZE + GRID_SIZE // 2
        
        # Check if position is on or too close to the path
        for i in range(len(self.path) - 1):
            start = self.path[i]
            end = self.path[i + 1]
            # Simple check - is tower center too close to path center?
            if self.distance_to_line_segment(grid_x, grid_y, start[0], start[1], end[0], end[1]) < GRID_SIZE:
                return False, None
        
        # Check if position overlaps with another tower
        for tower in self.towers:
            if tower.x == grid_x and tower.y == grid_y:
                return False, None
        
        return True, (grid_x, grid_y)
    
    def distance_to_line_segment(self, px, py, x1, y1, x2, y2):
        # Calculate the distance from a point (px, py) to a line segment from (x1, y1) to (x2, y2)
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:  # Line segment is actually a point
            return math.sqrt(A * A + B * B)
        
        param = dot / len_sq
        
        if param < 0:  # Closest point is x1, y1
            xx = x1
            yy = y1
        elif param > 1:  # Closest point is x2, y2
            xx = x2
            yy = y2
        else:  # Closest point is on the line segment
            xx = x1 + param * C
            yy = y1 + param * D
        
        dx = px - xx
        dy = py - yy
        return math.sqrt(dx * dx + dy * dy)
    
    def spawn_enemy(self):
        # Spawn a new enemy at the start of the path
        if self.next_enemy < len(self.enemies_to_spawn) and self.spawn_timer <= 0:
            enemy_type = self.enemies_to_spawn[self.next_enemy]
            self.enemies.append(Enemy(self.path[0][0], self.path[0][1], enemy_type, self.path))
            self.next_enemy += 1
            self.spawn_timer = 60  # Wait 1 second between spawns
    
    def start_wave(self):
        if not self.wave_in_progress:
            # Create a list of enemies for this wave
            self.enemies_to_spawn = ["basic"] * (5 + self.wave)
            if self.wave > 2:
                # Add some faster enemies in later waves
                self.enemies_to_spawn += ["fast"] * (self.wave - 2)
            if self.wave > 4:
                # Add some tank enemies in even later waves
                self.enemies_to_spawn += ["tank"] * (self.wave - 4)
            
            self.next_enemy = 0
            self.wave_in_progress = True
    
    def update(self):
        if self.state == GAME_RUNNING:
            # Update spawn timer
            if self.spawn_timer > 0:
                self.spawn_timer -= 1
            
            # Spawn enemies if wave is in progress
            if self.wave_in_progress:
                self.spawn_enemy()
                
                # Check if wave is complete
                if self.next_enemy >= len(self.enemies_to_spawn) and not self.enemies:
                    self.wave_in_progress = False
                    self.wave += 1
                    self.money += 100 + (self.wave * 10)  # Reward for completing a wave
            
            # Update towers (shooting)
            for tower in self.towers:
                tower.update(self.enemies, self.bullets)
            
            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update()
                
                # Check if enemy reached the end
                if enemy.current_waypoint >= len(self.path):
                    self.enemies.remove(enemy)
                    self.lives -= enemy.damage
                    if self.lives <= 0:
                        self.state = GAME_OVER
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update()
                
                # Check for collisions with enemies
                for enemy in self.enemies[:]:
                    if math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2) < enemy.radius + bullet.radius:
                        enemy.health -= bullet.damage
                        if bullet in self.bullets:  # Ensure bullet wasn't already removed
                            self.bullets.remove(bullet)
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.money += enemy.reward
                        break
                
                # Remove bullets that are out of bounds
                if (bullet.x < 0 or bullet.x > SCREEN_WIDTH or 
                    bullet.y < 0 or bullet.y > SCREEN_HEIGHT):
                    if bullet in self.bullets:  # Ensure bullet wasn't already removed
                        self.bullets.remove(bullet)
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw grid
        self.draw_grid()
        
        # Draw path
        self.draw_path()
        
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw tower range for selected tower
        mouse_pos = pygame.mouse.get_pos()
        can_place, grid_pos = self.can_place_tower(mouse_pos)
        if can_place and self.money >= TOWER_COST:
            # Draw ghost tower
            pygame.draw.circle(self.screen, (0, 255, 0, 128), grid_pos, GRID_SIZE // 2, 2)
            pygame.draw.circle(self.screen, (0, 255, 0, 64), grid_pos, 150, 1)  # Range indicator
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw UI
        money_text = self.font.render(f"Money: ${self.money}", True, BLACK)
        lives_text = self.font.render(f"Lives: {self.lives}", True, BLACK)
        wave_text = self.font.render(f"Wave: {self.wave}", True, BLACK)
        
        self.screen.blit(money_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(wave_text, (10, 90))
        
        # Draw "Start Wave" button if wave is not in progress
        if not self.wave_in_progress:
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH - 150, 10, 140, 40))
            start_text = self.font.render("Start Wave", True, BLACK)
            self.screen.blit(start_text, (SCREEN_WIDTH - 145, 15))
        
        # Game over screen
        if self.state == GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                               SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                             SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.state == GAME_RUNNING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Check for button clicks
                        if not self.wave_in_progress and SCREEN_WIDTH - 150 <= mouse_pos[0] <= SCREEN_WIDTH - 10 and 10 <= mouse_pos[1] <= 50:
                            self.start_wave()
                        else:
                            # Place tower
                            can_place, pos = self.can_place_tower(mouse_pos)
                            if can_place and self.money >= TOWER_COST:
                                self.towers.append(BaseTower(pos[0], pos[1]))
                                self.money -= TOWER_COST
            
            elif self.state == GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart the game
                        self.__init__()
        
        return True