"""

"""

import pygame
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576
FPS = 60

# Colors - Dark horror theme
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 25)
BLOOD_RED = (139, 0, 0)
CREEPY_RED = (200, 0, 0)
SONIC_BLUE = (0, 100, 255)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3


class Player(pygame.sprite.Sprite):
    """Sonic - the player character"""
    
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 50
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity_y = 0
        self.velocity_x = 0
        self.speed = 6
        self.jump_power = -14
        self.gravity = 0.6
        self.on_ground = False
        self.rings_collected = 0
        self.invincible = 0
        self.flash_timer = 0
        
    def update(self, platforms):
        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += int(self.velocity_y)
        self.rect.x += int(self.velocity_x)
        
        # Keep in bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            
        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                    
        # Decrease invincibility
        if self.invincible > 0:
            self.invincible -= 1
            self.flash_timer = (self.flash_timer + 1) % 10
            
    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False
            
    def draw(self, screen):
        # Simple Sonic representation - blue hedgehog
        if self.invincible > 0 and self.flash_timer < 5:
            color = WHITE  # Flash when hit
        else:
            color = SONIC_BLUE
            
        pygame.draw.ellipse(screen, color, self.rect)
        # Eyes
        eye_y = self.rect.centery - 10
        pygame.draw.circle(screen, WHITE, (self.rect.centerx - 8, eye_y), 6)
        pygame.draw.circle(screen, WHITE, (self.rect.centerx + 8, eye_y), 6)
        pygame.draw.circle(screen, BLACK, (self.rect.centerx - 6, eye_y), 3)
        pygame.draw.circle(screen, BLACK, (self.rect.centerx + 10, eye_y), 3)
        # Spikes (hair)
        points = [
            (self.rect.right - 5, self.rect.centery - 15),
            (self.rect.right + 15, self.rect.centery),
            (self.rect.right - 5, self.rect.centery + 15),
        ]
        pygame.draw.polygon(screen, color, points)


class SonicExe(pygame.sprite.Sprite):
    """The creepy Sonic.EXE - chases the player"""
    
    def __init__(self, x, y):
        super().__init__()
        self.width = 45
        self.height = 55
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 3
        self.phase_timer = 0
        self.teleport_timer = random.randint(180, 300)
        self.visible = True
        self.blink_timer = 0
        
    def update(self, player, platforms):
        self.phase_timer += 1
        self.teleport_timer -= 1
        self.blink_timer += 1
        
        # Creepy blinking
        if self.blink_timer % 60 < 3:
            self.visible = False
        else:
            self.visible = True
            
        if not self.visible:
            return
            
        # Chase player - move towards player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx = (dx / distance) * self.speed
            dy = (dy / distance) * self.speed
            self.rect.x += int(dx)
            self.rect.y += int(dy)
            
        # Teleport behind player sometimes
        if self.teleport_timer <= 0:
            self.rect.x = player.rect.x - 100
            self.rect.y = player.rect.y
            self.teleport_timer = random.randint(120, 240)
            
    def draw(self, screen):
        if not self.visible:
            return
            
        # Creepy black Sonic with red eyes
        pygame.draw.ellipse(screen, BLACK, self.rect)
        # Blood-red eyes
        eye_y = self.rect.centery - 8
        pygame.draw.ellipse(screen, BLOOD_RED, (self.rect.centerx - 15, eye_y - 5, 12, 15))
        pygame.draw.ellipse(screen, BLOOD_RED, (self.rect.centerx + 3, eye_y - 5, 12, 15))
        pygame.draw.ellipse(screen, CREEPY_RED, (self.rect.centerx - 12, eye_y - 2, 6, 10))
        pygame.draw.ellipse(screen, CREEPY_RED, (self.rect.centerx + 6, eye_y - 2, 6, 10))
        # Dark spikes
        points = [
            (self.rect.right - 5, self.rect.centery - 18),
            (self.rect.right + 18, self.rect.centery),
            (self.rect.right - 5, self.rect.centery + 18),
        ]
        pygame.draw.polygon(screen, (30, 30, 30), points)


class Ring(pygame.sprite.Sprite):
    """Collectible rings"""
    
    def __init__(self, x, y):
        super().__init__()
        self.radius = 12
        self.rect = pygame.Rect(x, y, self.radius*2, self.radius*2)
        self.animation = 0
        
    def update(self):
        self.animation = (self.animation + 0.2) % (2 * math.pi)
        
    def draw(self, screen):
        # Rotating ring effect
        cx = self.rect.centerx
        cy = self.rect.centery
        r = self.radius * (0.7 + 0.3 * math.sin(self.animation))
        pygame.draw.ellipse(screen, GOLD, (cx - r, cy - r/2, r*2, r), 3)
        pygame.draw.ellipse(screen, (255, 255, 100), (cx - r*0.7, cy - r*0.35, r*1.4, r*0.7), 2)


class Platform(pygame.sprite.Sprite):
    """Ground platforms"""
    
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
        pygame.display.set_caption("Sonic.EXE - RUN!")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 36)
        self.state = MENU
        self.reset_game()
        
    def reset_game(self):
        self.player = Player(100, 400)
        self.sonic_exe = SonicExe(SCREEN_WIDTH - 150, 300)
        self.rings = []
        self.platforms = []
        
        # Create platforms
        ground = Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        self.platforms.append(ground)
        
        for i in range(8):
            x = 200 + i * 120
            y = SCREEN_HEIGHT - 150 - random.randint(0, 100)
            w = random.randint(80, 150)
            self.platforms.append(Platform(x, y, w, 20))
            
        # Create rings
        for i in range(25):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            self.rings.append(Ring(x, y))
            
        self.game_over_timer = 0
        self.win_rings = 20  # Collect 20 rings to win
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if self.state == MENU and event.key == pygame.K_SPACE:
                        self.state = PLAYING
                        self.reset_game()
                    if self.state == GAME_OVER or self.state == WIN:
                        if event.key == pygame.K_SPACE:
                            self.state = MENU
                            self.reset_game()
                            
            if self.state == PLAYING:
                self.handle_input()
                self.update()
                
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.velocity_x = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.velocity_x = self.player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.player.jump()
            
    def update(self):
        self.player.update(self.platforms)
        self.sonic_exe.update(self.player, self.platforms)
        
        for ring in self.rings[:]:
            ring.update()
            if self.player.rect.colliderect(ring.rect):
                self.rings.remove(ring)
                self.player.rings_collected += 1
                if self.player.rings_collected >= self.win_rings:
                    self.state = WIN
                    self.game_over_timer = 180
                    
        # Check if caught by Sonic.EXE
        if self.player.rect.colliderect(self.sonic_exe.rect) and self.sonic_exe.visible:
            if self.player.invincible <= 0:
                if self.player.rings_collected > 0:
                    self.player.rings_collected -= 5
                    if self.player.rings_collected < 0:
                        self.player.rings_collected = 0
                    self.player.invincible = 90
                    self.player.rect.x -= 80
                else:
                    self.state = GAME_OVER
                    self.game_over_timer = 180
                    
    def draw(self):
        # Dark atmospheric background
        self.screen.fill(DARK_GRAY)
        
        # Creepy red vignette effect
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        vignette.set_alpha(80)
        for i in range(4):
            pygame.draw.rect(vignette, BLOOD_RED, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 40 - i*10)
        self.screen.blit(vignette, (0, 0))
        
        if self.state == MENU:
            self.draw_menu()
        elif self.state == PLAYING:
            self.draw_game()
        elif self.state == GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        elif self.state == WIN:
            self.draw_game()
            self.draw_win()
            
    def draw_menu(self):
        # Creepy title
        title = self.font_large.render("SONIC.EXE", True, BLOOD_RED)
        subtitle = self.font.render("He's coming for you...", True, GRAY)
        instruct = self.font.render("Press SPACE to run", True, WHITE)
        instruct2 = self.font.render("Arrow keys or WASD to move, SPACE to jump", True, GRAY)
        
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 180))
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 270))
        self.screen.blit(instruct, (SCREEN_WIDTH//2 - instruct.get_width()//2, 380))
        self.screen.blit(instruct2, (SCREEN_WIDTH//2 - instruct2.get_width()//2, 420))
        
        # Blinking "RUN"
        if pygame.time.get_ticks() % 1000 < 500:
            run_text = self.font.render(">>> RUN <<<", True, CREEPY_RED)
            self.screen.blit(run_text, (SCREEN_WIDTH//2 - run_text.get_width()//2, 480))
            
    def draw_game(self):
        for platform in self.platforms:
            platform.draw(self.screen)
            
        for ring in self.rings:
            ring.draw(self.screen)
            
        self.player.draw(self.screen)
        self.sonic_exe.draw(self.screen)
        
        # HUD
        rings_text = self.font.render(f"Rings: {self.player.rings_collected}/{self.win_rings}", True, GOLD)
        self.screen.blit(rings_text, (10, 10))
        
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        
        text = self.font_large.render("GAME OVER", True, BLOOD_RED)
        subtext = self.font.render("Sonic.EXE got you...", True, WHITE)
        instruct = self.font.render("Press SPACE to return to menu", True, GRAY)
        
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 220))
        self.screen.blit(subtext, (SCREEN_WIDTH//2 - subtext.get_width()//2, 300))
        self.screen.blit(instruct, (SCREEN_WIDTH//2 - instruct.get_width()//2, 380))
        
    def draw_win(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        text = self.font_large.render("ESCAPED!", True, GOLD)
        subtext = self.font.render("You collected enough rings and escaped Sonic.EXE!", True, WHITE)
        instruct = self.font.render("Press SPACE to play again", True, GRAY)
        
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 220))
        self.screen.blit(subtext, (SCREEN_WIDTH//2 - subtext.get_width()//2, 300))
        self.screen.blit(instruct, (SCREEN_WIDTH//2 - instruct.get_width()//2, 380))


if __name__ == "__main__":
    game = Game()
    game.run()
