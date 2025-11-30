import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("格闘ゲーム - 勝ち抜きバトル")

# 色定義
SKY_BLUE = (135, 206, 250)
GRASS_GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 223, 0)
DARK_RED = (139, 0, 0)
DARK_BLUE = (0, 0, 139)
SKIN_COLOR = (255, 220, 177)
GRAY = (100, 100, 100)
PURPLE = (128, 0, 128)

# フォント設定
def get_font(size):
    # EXE版なのでシステムフォントを優先的に探す
    font_names = ["meiryo", "msgothic", "yugothic", "arial"]
    return pygame.font.SysFont(font_names, size)

font_small = get_font(32)
font_medium = get_font(48)
font_large = get_font(72)

# FPS設定
clock = pygame.time.Clock()
FPS = 60

# ゲーム設定
GRAVITY = 0.6
JUMP_POWER = -15
GROUND_Y = 480
MOVE_SPEED = 6

class Fighter:
    """ファイタークラス"""
    
    def __init__(self, x, player_num, level=1):
        self.player_num = player_num
        self.level = level
        self.x = x
        self.y = GROUND_Y
        self.vel_y = 0
        self.vel_x = 0
        
        if player_num == 1:
            self.body_color = BLUE
            self.detail_color = DARK_BLUE
            self.name = "あなた"
        else:
            if level == 5:
                self.body_color = PURPLE
                self.detail_color = BLACK
                self.name = "BOSS"
            else:
                shade = max(50, 220 - (level * 30))
                self.body_color = (shade, 50, 50)
                self.detail_color = DARK_RED
                self.name = f"敵 Lv.{level}"
        
        self.width = 50
        self.height = 100
        
        base_hp = 100
        if player_num == 2:
            self.max_health = base_hp + (level - 1) * 20
        else:
            self.max_health = 100
            
        self.health = self.max_health
        self.facing_right = (player_num == 1)
        
        self.is_jumping = False
        self.is_punching = False
        self.is_kicking = False
        self.is_sliding = False
        
        self.action_timer = 0
        self.hit_cooldown = 0
        self.damage_flash = 0
        
    def move(self, direction):
        if not self.is_punching and not self.is_kicking:
            if not self.is_sliding:
                self.vel_x = direction * MOVE_SPEED
    
    def jump(self):
        if not self.is_jumping and not self.is_sliding:
            self.vel_y = JUMP_POWER
            self.is_jumping = True
    
    def punch(self):
        if not self.is_punching and not self.is_kicking and not self.is_sliding:
            self.is_punching = True
            self.action_timer = 20
            self.vel_x = 0
    
    def kick(self):
        if not self.is_kicking and not self.is_punching and not self.is_sliding:
            self.is_kicking = True
            self.action_timer = 30
            self.vel_x = 0
            
    def slide(self):
        if not self.is_sliding and not self.is_jumping and not self.is_punching and not self.is_kicking:
            self.is_sliding = True
            self.action_timer = 40
            speed = 12
            self.vel_x = speed if self.facing_right else -speed
    
    def update(self, opponent):
        if not self.is_sliding:
            if opponent.x > self.x:
                self.facing_right = True
            else:
                self.facing_right = False
        
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vel_y = 0
            self.is_jumping = False
        
        self.x += self.vel_x
        
        if self.is_sliding:
            self.vel_x *= 0.95
        else:
            self.vel_x *= 0.8
            
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0
            
        self.x = max(50, min(SCREEN_WIDTH - 50, self.x))
        
        if self.action_timer > 0:
            self.action_timer -= 1
            if self.action_timer == 0:
                self.is_punching = False
                self.is_kicking = False
                self.is_sliding = False
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        if self.damage_flash > 0:
            self.damage_flash -= 1
    
    def get_attack_rect(self):
        if self.is_punching:
            if 5 < self.action_timer < 15:
                if self.facing_right:
                    return pygame.Rect(self.x + 20, self.y - 70, 50, 30)
                else:
                    return pygame.Rect(self.x - 70, self.y - 70, 50, 30)
        elif self.is_kicking:
            if 5 < self.action_timer < 25:
                if self.facing_right:
                    return pygame.Rect(self.x + 20, self.y - 50, 70, 40)
                else:
                    return pygame.Rect(self.x - 90, self.y - 50, 70, 40)
        elif self.is_sliding:
            if 10 < self.action_timer < 35:
                if self.facing_right:
                    return pygame.Rect(self.x + 10, self.y - 30, 80, 30)
                else:
                    return pygame.Rect(self.x - 90, self.y - 30, 80, 30)
        return None
    
    def get_hurt_rect(self):
        if self.is_sliding:
            return pygame.Rect(self.x - 25, self.y - 50, 50, 50)
        return pygame.Rect(self.x - 25, self.y - 100, 50, 100)
    
    def take_damage(self, amount):
        if self.hit_cooldown == 0:
            self.health -= amount
            self.health = max(0, self.health)
            self.hit_cooldown = 40
            self.damage_flash = 10
            
            knockback = -10 if self.facing_right else 10
            self.vel_x = knockback
            self.vel_y = -5
            
            self.is_punching = False
            self.is_kicking = False
            self.is_sliding = False

    def draw(self, screen):
        if self.damage_flash > 0 and self.damage_flash % 4 < 2:
            return

        draw_x = int(self.x)
        draw_y = int(self.y)
        
        if self.is_sliding:
            pygame.draw.ellipse(screen, self.body_color, (draw_x - 40, draw_y - 40, 80, 40))
            head_x = draw_x + 30 if self.facing_right else draw_x - 30
            pygame.draw.circle(screen, SKIN_COLOR, (head_x, draw_y - 30), 20)
            leg_x = draw_x - 40 if self.facing_right else draw_x + 40
            pygame.draw.line(screen, self.detail_color, (draw_x, draw_y - 20), (leg_x, draw_y - 10), 8)
            return

        pygame.draw.ellipse(screen, self.body_color, (draw_x - 25, draw_y - 80, 50, 60))
        pygame.draw.circle(screen, SKIN_COLOR, (draw_x, draw_y - 90), 20)
        
        eye_color = BLACK
        if self.facing_right:
            pygame.draw.circle(screen, eye_color, (draw_x + 8, draw_y - 95), 3)
            pygame.draw.line(screen, eye_color, (draw_x + 5, draw_y - 85), (draw_x + 15, draw_y - 85), 2)
        else:
            pygame.draw.circle(screen, eye_color, (draw_x - 8, draw_y - 95), 3)
            pygame.draw.line(screen, eye_color, (draw_x - 15, draw_y - 85), (draw_x - 5, draw_y - 85), 2)

        arm_color = self.detail_color
        shoulder_y = draw_y - 70
        
        if self.is_punching:
            if self.facing_right:
                pygame.draw.line(screen, arm_color, (draw_x, shoulder_y), (draw_x + 40, shoulder_y), 8)
            else:
                pygame.draw.line(screen, arm_color, (draw_x, shoulder_y), (draw_x - 40, shoulder_y), 8)
        else:
            pygame.draw.line(screen, arm_color, (draw_x, shoulder_y), (draw_x, shoulder_y + 30), 8)

        leg_color = self.detail_color
        hip_y = draw_y - 20
        
        if self.is_kicking:
            if self.facing_right:
                pygame.draw.line(screen, leg_color, (draw_x, hip_y), (draw_x + 50, hip_y - 10), 8)
                pygame.draw.line(screen, leg_color, (draw_x, hip_y), (draw_x - 10, hip_y + 30), 8)
            else:
                pygame.draw.line(screen, leg_color, (draw_x, hip_y), (draw_x - 50, hip_y - 10), 8)
                pygame.draw.line(screen, leg_color, (draw_x, hip_y), (draw_x + 10, hip_y + 30), 8)
        else:
            if self.is_jumping:
                pygame.draw.line(screen, leg_color, (draw_x - 10, hip_y), (draw_x - 15, hip_y + 20), 8)
                pygame.draw.line(screen, leg_color, (draw_x + 10, hip_y), (draw_x + 15, hip_y + 20), 8)
            else:
                pygame.draw.line(screen, leg_color, (draw_x - 10, hip_y), (draw_x - 10, hip_y + 30), 8)
                pygame.draw.line(screen, leg_color, (draw_x + 10, hip_y), (draw_x + 10, hip_y + 30), 8)


class EnemyAI:
    def __init__(self, fighter, level):
        self.fighter = fighter
        self.level = level
        self.state = "wait"
        self.timer = 0
        self.attack_cooldown = 0
        self.aggression = max(10, 60 - level * 10) 
        self.reaction = max(5, 30 - level * 5)
        
    def update(self, player):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.timer > 0:
            self.timer -= 1
        
        dist_x = abs(player.x - self.fighter.x)
        
        if self.timer == 0:
            self._decide_action(dist_x, player)
            
        self._execute_action(player)
        
    def _decide_action(self, dist_x, player):
        attack_chance = 0.3 + (self.level * 0.1)
        
        if dist_x < 100:
            if self.attack_cooldown == 0 and random.random() < attack_chance:
                self.state = "attack"
                self.timer = 30
            else:
                if self.level >= 3 and random.random() < 0.3:
                    self.state = "jump"
                    self.timer = 20
                else:
                    self.state = "retreat" if random.random() < 0.5 else "wait"
                    self.timer = 20
                    
        elif dist_x < 300:
            if self.level >= 4 and random.random() < 0.3:
                self.state = "slide"
                self.timer = 40
            else:
                self.state = "chase"
                self.timer = 30
        else:
            self.state = "chase"
            self.timer = 40
            
    def _execute_action(self, player):
        if self.state == "chase":
            if player.x > self.fighter.x:
                self.fighter.move(1)
            else:
                self.fighter.move(-1)
                
        elif self.state == "retreat":
            if player.x > self.fighter.x:
                self.fighter.move(-1)
            else:
                self.fighter.move(1)
                
        elif self.state == "jump":
            self.fighter.jump()
            self.state = "wait"
            
        elif self.state == "slide":
            self.fighter.slide()
            self.state = "wait"
            
        elif self.state == "attack":
            if not self.fighter.is_punching and not self.fighter.is_kicking:
                roll = random.random()
                if roll < 0.4:
                    self.fighter.punch()
                elif roll < 0.7:
                    self.fighter.kick()
                elif self.level >= 2:
                    self.fighter.slide()
                else:
                    self.fighter.kick()
                    
                self.attack_cooldown = max(20, 80 - self.level * 10)
                self.state = "wait"
                
        elif self.state == "wait":
            self.fighter.move(0)


class Game:
    def __init__(self):
        self.current_level = 1
        self.max_levels = 5
        self.reset_round()
        self.game_cleared = False
        
    def reset_round(self):
        self.player = Fighter(200, 1)
        self.player.health = 100
        
        self.enemy = Fighter(1000, 2, self.current_level)
        self.enemy_ai = EnemyAI(self.enemy, self.current_level)
        
        self.round_time = 60
        self.frame_count = 0
        self.game_over = False
        self.winner = None
        self.start_delay = 60
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        move_dir = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_dir = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_dir = 1
        self.player.move(move_dir)
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player.jump()
            
        if keys[pygame.K_s] or keys[pygame.K_DOWN] or keys[pygame.K_z]:
            self.player.punch()
        if keys[pygame.K_x]:
            self.player.kick()
        if keys[pygame.K_SPACE]:
            self.player.slide()
            
        if keys[pygame.K_r] and (self.game_over or self.game_cleared):
            self.current_level = 1
            self.game_cleared = False
            self.reset_round()

    def update(self):
        if self.start_delay > 0:
            self.start_delay -= 1
            return

        if self.game_over or self.game_cleared:
            return
        
        self.player.update(self.enemy)
        self.enemy_ai.update(self.player)
        self.enemy.update(self.player)
        
        self.check_collision()
        
        self.frame_count += 1
        if self.frame_count >= FPS:
            self.frame_count = 0
            self.round_time -= 1
            if self.round_time <= 0:
                self.end_round()
                
        if self.player.health <= 0 or self.enemy.health <= 0:
            self.end_round()
            
    def check_collision(self):
        p_attack = self.player.get_attack_rect()
        if p_attack and p_attack.colliderect(self.enemy.get_hurt_rect()):
            damage = 10
            if self.player.is_kicking: damage = 15
            if self.player.is_sliding: damage = 12
            self.enemy.take_damage(damage)
                
        e_attack = self.enemy.get_attack_rect()
        if e_attack and e_attack.colliderect(self.player.get_hurt_rect()):
            damage = 10 + (self.current_level * 2)
            self.player.take_damage(damage)
                
    def end_round(self):
        self.game_over = True
        
        if self.player.health > self.enemy.health:
            self.winner = self.player
            if self.current_level < self.max_levels:
                pygame.time.delay(2000) # EXE版なのでdelayでOK
                self.current_level += 1
                self.reset_round()
            else:
                self.game_cleared = True
        elif self.enemy.health > self.player.health:
            self.winner = self.enemy
        else:
            self.winner = None
            
    def draw(self):
        screen.fill(SKY_BLUE)
        
        pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        pygame.draw.line(screen, (50, 100, 50), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
        
        self.player.draw(screen)
        self.enemy.draw(screen)
        self.draw_ui()
        
        if self.start_delay > 0:
            level_text = font_large.render(f"STAGE {self.current_level}", True, BLACK)
            screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            if self.current_level == 5:
                boss_text = font_medium.render("- FINAL BOSS -", True, RED)
                screen.blit(boss_text, (SCREEN_WIDTH//2 - boss_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        if self.game_cleared:
            self.draw_game_clear()
        elif self.game_over and self.winner != self.player:
            self.draw_game_over()
            
    def draw_ui(self):
        bar_w = 400
        bar_h = 30
        
        pygame.draw.rect(screen, GRAY, (50, 30, bar_w, bar_h))
        p_ratio = self.player.health / self.player.max_health
        pygame.draw.rect(screen, BLUE, (50, 30, int(bar_w * p_ratio), bar_h))
        pygame.draw.rect(screen, WHITE, (50, 30, bar_w, bar_h), 3)
        screen.blit(font_small.render(self.player.name, True, WHITE), (50, 65))
        
        enemy_x = SCREEN_WIDTH - 50 - bar_w
        pygame.draw.rect(screen, GRAY, (enemy_x, 30, bar_w, bar_h))
        e_ratio = self.enemy.health / self.enemy.max_health
        e_w = int(bar_w * e_ratio)
        pygame.draw.rect(screen, RED, (enemy_x + (bar_w - e_w), 30, e_w, bar_h))
        pygame.draw.rect(screen, WHITE, (enemy_x, 30, bar_w, bar_h), 3)
        screen.blit(font_small.render(self.enemy.name, True, WHITE), (enemy_x, 65))
        
        time_text = font_large.render(str(self.round_time), True, YELLOW)
        screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, 20))
        
        stage_text = font_medium.render(f"STAGE {self.current_level}/5", True, BLACK)
        screen.blit(stage_text, (SCREEN_WIDTH//2 - stage_text.get_width()//2, 80))
        
        guide = font_small.render("移動:矢印  攻撃:Z/X  スライディング:Space", True, WHITE)
        screen.blit(guide, (20, SCREEN_HEIGHT - 40))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        text = font_large.render("GAME OVER", True, RED)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        info = font_medium.render(f"到達ステージ: {self.current_level}", True, WHITE)
        screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        retry = font_medium.render("Rキーで最初から", True, WHITE)
        screen.blit(retry, (SCREEN_WIDTH//2 - retry.get_width()//2, SCREEN_HEIGHT//2 + 80))

    def draw_game_clear(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(WHITE)
        screen.blit(overlay, (0,0))
        
        text = font_large.render("ALL STAGES CLEARED!", True, YELLOW)
        text_shadow = font_large.render("ALL STAGES CLEARED!", True, BLACK)
        screen.blit(text_shadow, (SCREEN_WIDTH//2 - text.get_width()//2 + 4, SCREEN_HEIGHT//2 - 50 + 4))
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        msg = font_medium.render("おめでとうございます！完全制覇です！", True, BLACK)
        screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        retry = font_medium.render("Rキーで最初から遊ぶ", True, BLACK)
        screen.blit(retry, (SCREEN_WIDTH//2 - retry.get_width()//2, SCREEN_HEIGHT//2 + 100))


def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        game.handle_input()
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
