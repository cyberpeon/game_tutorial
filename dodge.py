import pygame
import sys
import os
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Character Mover - Ultimate Dodge!")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
PURPLE = (150, 50, 250)
YELLOW = (255, 215, 0)
GREEN = (50, 200, 50)

# Game States
STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2

# Global variables
char_image = None
char_rect = None
base_speed = 5
char_speed = base_speed
game_state = STATE_TITLE
score = 0
level = 1
enemies = []
items = []
enemy_spawn_timer = 0
item_spawn_timer = 0

class Enemy:
    def __init__(self, enemy_type='normal'):
        self.type = enemy_type
        self.size = random.randint(20, 40)
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        speed_mult = 1 + (level * 0.1)
        self.speed = random.randint(3, 7) * speed_mult
        
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
            self.rect.y = -self.size
            self.vel_x = random.choice([-2, -1, 0, 1, 2])
            self.vel_y = self.speed
        elif side == 'bottom':
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.size)
            self.rect.y = SCREEN_HEIGHT
            self.vel_x = random.choice([-2, -1, 0, 1, 2])
            self.vel_y = -self.speed
        elif side == 'left':
            self.rect.x = -self.size
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.size)
            self.vel_x = self.speed
            self.vel_y = random.choice([-2, -1, 0, 1, 2])
        elif side == 'right':
            self.rect.x = SCREEN_WIDTH
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.size)
            self.vel_x = -self.speed
            self.vel_y = random.choice([-2, -1, 0, 1, 2])

        if self.type == 'chase':
            self.speed *= 0.4 
            self.color = PURPLE
            self.life_timer = 180 
        else:
            self.color = RED
            self.life_timer = None

    def update(self, target_rect):
        if self.type == 'chase' and target_rect:
            dx = target_rect.centerx - self.rect.centerx
            dy = target_rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx, dy = dx / dist, dy / dist
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
            
            if self.life_timer is not None:
                self.life_timer -= 1
        else:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

    def draw(self, surface):
        if self.life_timer is not None and self.life_timer < 60:
            if (self.life_timer // 5) % 2 == 0:
                return

        pygame.draw.ellipse(surface, self.color, self.rect)
        if self.type == 'chase':
            pygame.draw.circle(surface, WHITE, (self.rect.centerx - 5, self.rect.centery - 5), 3)
            pygame.draw.circle(surface, WHITE, (self.rect.centerx + 5, self.rect.centery - 5), 3)

    def is_expired(self):
        return self.life_timer is not None and self.life_timer <= 0

    def is_off_screen(self):
        margin = 100 if self.type == 'chase' else 0
        return (self.rect.right < -margin or self.rect.left > SCREEN_WIDTH + margin or
                self.rect.bottom < -margin or self.rect.top > SCREEN_HEIGHT + margin)

class Item:
    def __init__(self):
        self.size = 20
        self.rect = pygame.Rect(random.randint(50, SCREEN_WIDTH-50), 
                                random.randint(50, SCREEN_HEIGHT-50), 
                                self.size, self.size)
        self.timer = 300 

    def update(self):
        self.timer -= 1

    def draw(self, surface):
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 5
        draw_rect = self.rect.inflate(pulse, pulse)
        pygame.draw.circle(surface, YELLOW, draw_rect.center, draw_rect.width // 2)

def process_image(file_path):
    print(f"Processing {file_path}...")
    try:
        image = pygame.image.load(file_path).convert()
        colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
        print("Done!")
        if image.get_width() > 80 or image.get_height() > 80:
            scale = 80 / max(image.get_width(), image.get_height())
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.smoothscale(image, new_size)
        return image
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def reset_game():
    global enemies, items, score, level, char_rect
    enemies = []
    items = []
    score = 0
    level = 1
    if char_rect:
        char_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

def main():
    global char_image, char_rect, game_state, score, level, enemies, items
    global enemy_spawn_timer, item_spawn_timer
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    title_font = pygame.font.SysFont(None, 64)
    
    default_img = "sample_character.png"
    if os.path.exists(default_img):
        SCREEN.fill(WHITE)
        loading_text = font.render("Loading...", True, BLACK)
        text_rect = loading_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        SCREEN.blit(loading_text, text_rect)
        pygame.display.flip()
        pygame.event.pump()
        
        char_image = process_image(default_img)
        if char_image:
            char_rect = char_image.get_rect()
            char_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.DROPFILE:
                file_path = event.file
                print(f"File dropped: {file_path}")
                new_image = process_image(file_path)
                if new_image:
                    char_image = new_image
                    char_rect = char_image.get_rect()
                    char_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            
            if game_state == STATE_TITLE or game_state == STATE_GAMEOVER:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if char_image:
                        game_state = STATE_PLAYING
                        reset_game()

        if game_state == STATE_PLAYING and char_rect:
            level = 1 + score // 1000
            
            keys = pygame.key.get_pressed()
            current_speed = base_speed

            if keys[pygame.K_LEFT] and char_rect.left > 0:
                char_rect.x -= current_speed
            if keys[pygame.K_RIGHT] and char_rect.right < SCREEN_WIDTH:
                char_rect.x += current_speed
            if keys[pygame.K_UP] and char_rect.top > 0:
                char_rect.y -= current_speed
            if keys[pygame.K_DOWN] and char_rect.bottom < SCREEN_HEIGHT:
                char_rect.y += current_speed

            spawn_rate = max(10, 40 - level * 2)
            enemy_spawn_timer += 1
            if enemy_spawn_timer > spawn_rate:
                e_type = 'chase' if level >= 3 and random.random() < 0.2 else 'normal'
                enemies.append(Enemy(e_type))
                enemy_spawn_timer = 0
            
            item_spawn_timer += 1
            if item_spawn_timer > 300:
                if random.random() < 0.5:
                    items.append(Item())
                item_spawn_timer = 0

            char_hitbox = char_rect.inflate(-15, -15)
            for enemy in enemies[:]:
                enemy.update(char_rect)
                should_remove = False
                if enemy.is_off_screen():
                    should_remove = True
                    score += 10
                elif enemy.is_expired():
                    should_remove = True
                    score += 5
                
                if should_remove:
                    enemies.remove(enemy)
                elif char_hitbox.colliderect(enemy.rect):
                    game_state = STATE_GAMEOVER
            
            for item in items[:]:
                item.update()
                if item.timer <= 0:
                    items.remove(item)
                elif char_hitbox.colliderect(item.rect):
                    items.remove(item)
                    score += 500

            score += 1

        SCREEN.fill(WHITE)
        
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(SCREEN, (240, 240, 240), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(SCREEN, (240, 240, 240), (0, y), (SCREEN_WIDTH, y))

        if char_image:
            SCREEN.blit(char_image, char_rect)
        
        if game_state == STATE_TITLE:
            title_text = title_font.render("Ultimate Dodge!", True, BLACK)
            start_text = font.render("Press SPACE to Start", True, BLUE)
            instr_text = font.render("Use Arrow Keys to Move", True, GRAY)
            
            SCREEN.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
            SCREEN.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
            SCREEN.blit(instr_text, instr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))
            
            if not char_image:
                warn_text = font.render("Drop an image file first!", True, RED)
                SCREEN.blit(warn_text, warn_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)))

        elif game_state == STATE_PLAYING:
            for item in items:
                item.draw(SCREEN)
            for enemy in enemies:
                enemy.draw(SCREEN)
            
            score_text = font.render(f"Score: {score}", True, BLACK)
            level_text = font.render(f"Level: {level}", True, RED)
            SCREEN.blit(score_text, (10, 10))
            SCREEN.blit(level_text, (10, 40))

        elif game_state == STATE_GAMEOVER:
            for enemy in enemies:
                enemy.draw(SCREEN)
                
            over_text = title_font.render("GAME OVER", True, RED)
            score_text = font.render(f"Final Score: {score}", True, BLACK)
            retry_text = font.render("Press SPACE to Retry", True, BLUE)
            
            SCREEN.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            SCREEN.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10)))
            SCREEN.blit(retry_text, retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
