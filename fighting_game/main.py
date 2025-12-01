import asyncio
import pygame
import sys
import random

# 初期化
pygame.init()

# 画面設定
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fighting Game - Battle Royale")

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
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)

# フォント設定 - Pygbag対応
def get_font(size):
    return pygame.font.Font(None, size)

font_small = get_font(32)
font_medium = get_font(48)
font_large = get_font(72)

# FPS設定
clock = pygame.time.Clock()
FPS = 60

# ゲーム設定
GRAVITY = 0.6
GROUND_Y = 480

# キャラクタータイプ定義
CHAR_TYPES = {
    "BALANCE": {
        "color": BLUE, "detail": DARK_BLUE, "hp": 100, "speed": 6, "power": 1.0, "jump": -15,
        "desc": "Standard Fighter. Has Hadoken."
    },
    "POWER": {
        "color": DARK_RED, "detail": BLACK, "hp": 140, "speed": 4, "power": 1.5, "jump": -12,
        "desc": "High HP & Attack. Slow speed."
    },
    "SPEED": {
        "color": YELLOW, "detail": ORANGE, "hp": 80, "speed": 9, "power": 0.8, "jump": -18,
        "desc": "Fast & High Jump. Low HP."
    }
}

class Projectile:
    def __init__(self, x, y, facing_right, owner):
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.owner = owner
        self.speed = 10 if facing_right else -10
        self.radius = 15
        self.color = CYAN
        self.active = True
        self.life = 100 # Frames until disappear
        
    def update(self):
        self.x += self.speed
        self.life -= 1
        if self.life <= 0 or self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.active = False
            
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 5)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class Fighter:
    """ファイタークラス"""
    
    def __init__(self, x, player_num, char_type_name="BALANCE", level=1):
        self.player_num = player_num
        self.level = level
        self.char_type = CHAR_TYPES[char_type_name]
        self.x = x
        self.y = GROUND_Y
        self.vel_y = 0
        self.vel_x = 0
        
        # キャラクター性能の設定
        self.move_speed = self.char_type["speed"]
        self.jump_power = self.char_type["jump"]
        self.power_mult = self.char_type["power"]
        
        if player_num == 1:
            self.body_color = self.char_type["color"]
            self.detail_color = self.char_type["detail"]
            self.name = f"P1 ({char_type_name})"
        else:
            # 敵の見た目調整
            if level == 5:
                self.body_color = PURPLE
                self.detail_color = BLACK
                self.name = "BOSS"
                self.move_speed = 7
                self.power_mult = 1.5
                base_hp = 200
            else:
                shade = max(50, 220 - (level * 30))
                self.body_color = (shade, 50, 50)
                self.detail_color = DARK_RED
                self.name = f"Enemy Lv.{level}"
                base_hp = 100 + (level - 1) * 20
        
        self.width = 50
        self.height = 100
        
        if player_num == 1:
            self.max_health = self.char_type["hp"]
        else:
            self.max_health = base_hp
            
        self.health = self.max_health
        self.facing_right = (player_num == 1)
        
        self.is_jumping = False
        self.is_punching = False
        self.is_kicking = False
        self.is_sliding = False
        self.is_guarding = False
        self.is_shooting = False
        
        self.action_timer = 0
        self.hit_cooldown = 0
        self.damage_flash = 0
        self.shoot_cooldown = 0
        
        # コマンド入力用バッファ [(frame_count, input_mask), ...]
        # input_mask: 1=UP, 2=DOWN, 4=LEFT, 8=RIGHT
        self.input_buffer = []
        self.buffer_timer = 0
        
    def move(self, direction):
        if not self.is_punching and not self.is_kicking and not self.is_guarding and not self.is_shooting:
            if not self.is_sliding:
                self.vel_x = direction * self.move_speed
    
    def jump(self):
        if not self.is_jumping and not self.is_sliding and not self.is_guarding and not self.is_shooting:
            self.vel_y = self.jump_power
            self.is_jumping = True
    
    def punch(self):
        if not self.is_punching and not self.is_kicking and not self.is_sliding and not self.is_guarding and not self.is_shooting:
            self.is_punching = True
            self.action_timer = 20
            self.vel_x = 0
    
    def kick(self):
        if not self.is_kicking and not self.is_punching and not self.is_sliding and not self.is_guarding and not self.is_shooting:
            self.is_kicking = True
            self.action_timer = 30
            self.vel_x = 0
            
    def slide(self):
        if not self.is_sliding and not self.is_jumping and not self.is_punching and not self.is_kicking and not self.is_guarding and not self.is_shooting:
            self.is_sliding = True
            self.action_timer = 40
            speed = self.move_speed * 2
            self.vel_x = speed if self.facing_right else -speed

    def guard(self, active):
        if active:
            if not self.is_jumping and not self.is_punching and not self.is_kicking and not self.is_sliding and not self.is_shooting:
                self.is_guarding = True
                self.vel_x = 0
        else:
            self.is_guarding = False

    def shoot(self, game_ref):
        if self.shoot_cooldown == 0 and not self.is_punching and not self.is_kicking and not self.is_sliding and not self.is_guarding and not self.is_shooting:
            self.is_shooting = True
            self.action_timer = 30
            self.vel_x = 0
            self.shoot_cooldown = 60
            
            # 飛び道具生成
            proj_x = self.x + (40 if self.facing_right else -40)
            proj_y = self.y - 60
            proj = Projectile(proj_x, proj_y, self.facing_right, self)
            game_ref.projectiles.append(proj)

    def update_input(self, inputs):
        # inputs: {"UP": bool, "DOWN": bool, "LEFT": bool, "RIGHT": bool}
        mask = 0
        if inputs["UP"]: mask |= 1
        if inputs["DOWN"]: mask |= 2
        if inputs["LEFT"]: mask |= 4
        if inputs["RIGHT"]: mask |= 8
        
        # 同じ入力が続いている場合は追加しない（または一定間隔で追加）
        # ここではシンプルに変化があった時と、一定時間経過で追加
        self.buffer_timer += 1
        if not self.input_buffer or self.input_buffer[-1][1] != mask or self.buffer_timer > 5:
            self.input_buffer.append((pygame.time.get_ticks(), mask))
            if len(self.input_buffer) > 20: # 履歴は最新20個まで
                self.input_buffer.pop(0)
            self.buffer_timer = 0

    def check_special_move(self):
        # 簡易波動拳コマンド: 下(2) -> 前(8 or 4) + 攻撃ボタン
        # 実際には: 直近の履歴に「下」があり、その後に「前」があるか確認
        
        now = pygame.time.get_ticks()
        # 過去0.5秒以内の入力のみ有効
        valid_buffer = [x for x in self.input_buffer if now - x[0] < 500]
        
        if len(valid_buffer) < 2:
            return False
            
        has_down = False
        has_forward = False
        
        target_forward = 8 if self.facing_right else 4 # 8=RIGHT, 4=LEFT
        
        for _, mask in valid_buffer:
            if mask & 2: # DOWN
                has_down = True
            if has_down and (mask & target_forward): # DOWNの後にFORWARD
                has_forward = True
                
        return has_forward

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
                self.is_shooting = False
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        if self.damage_flash > 0:
            self.damage_flash -= 1
            
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
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
            if self.is_guarding:
                amount = int(amount * 0.2) # 80% damage reduction
                self.hit_cooldown = 20 # Shorter cooldown on block
            else:
                self.hit_cooldown = 40
                
            self.health -= amount
            self.health = max(0, self.health)
            self.damage_flash = 10
            
            knockback = -10 if self.facing_right else 10
            if self.is_guarding:
                knockback //= 2 # Less knockback on block
                
            self.vel_x = knockback
            self.vel_y = -5
            
            self.is_punching = False
            self.is_kicking = False
            self.is_sliding = False
            self.is_shooting = False

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
        
        if self.is_guarding:
            # Guard pose
            if self.facing_right:
                pygame.draw.line(screen, arm_color, (draw_x, shoulder_y), (draw_x + 20, shoulder_y - 20), 8)
                pygame.draw.line(screen, arm_color, (draw_x + 20, shoulder_y - 20), (draw_x + 20, shoulder_y + 10), 8)
            else:
                pygame.draw.line(screen, arm_color, (draw_x, shoulder_y), (draw_x - 20, shoulder_y - 20), 8)
                pygame.draw.line(screen, arm_color, (draw_x - 20, shoulder_y - 20), (draw_x - 20, shoulder_y + 10), 8)
        elif self.is_shooting:
            # Shooting pose (Hadoken pose)
            if self.facing_right:
                pygame.draw.line(screen, arm_color, (draw_x, shoulder_y), (draw_x + 30, shoulder_y), 8)
                pygame.draw.line(screen, arm_color, (draw_x + 30, shoulder_y), (draw_x + 40, shoulder_y), 8)
            else:
                pygame.draw.line(screen, arm_color, (draw_x, shoulder_y), (draw_x - 30, shoulder_y), 8)
                pygame.draw.line(screen, arm_color, (draw_x - 30, shoulder_y), (draw_x - 40, shoulder_y), 8)
        elif self.is_punching:
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
    def __init__(self, fighter, level, game_ref):
        self.fighter = fighter
        self.level = level
        self.game_ref = game_ref
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
                elif self.level >= 2 and random.random() < 0.3:
                    self.state = "guard"
                    self.timer = 30
                else:
                    self.state = "retreat" if random.random() < 0.5 else "wait"
                    self.timer = 20
                    
        elif dist_x < 400:
            # 遠距離でたまに飛び道具
            if self.level >= 3 and self.attack_cooldown == 0 and random.random() < 0.1:
                self.state = "shoot"
                self.timer = 40
            elif self.level >= 4 and random.random() < 0.3:
                self.state = "slide"
                self.timer = 40
            else:
                self.state = "chase"
                self.timer = 30
        else:
            if self.level >= 3 and self.attack_cooldown == 0 and random.random() < 0.2:
                self.state = "shoot"
                self.timer = 40
            else:
                self.state = "chase"
                self.timer = 40
            
    def _execute_action(self, player):
        if self.state != "guard":
            self.fighter.guard(False)

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
        
        elif self.state == "guard":
            self.fighter.guard(True)
            
        elif self.state == "shoot":
            self.fighter.shoot(self.game_ref)
            self.attack_cooldown = 100
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
        self.state = "SELECT" # SELECT, GAME, GAMEOVER
        self.selected_char = "BALANCE"
        self.char_list = list(CHAR_TYPES.keys())
        self.char_index = 0
        
        self.current_level = 1
        self.max_levels = 5
        self.game_cleared = False
        self.projectiles = []
        
    def start_game(self):
        self.state = "GAME"
        self.current_level = 1
        self.game_cleared = False
        self.reset_round()
        
    def reset_round(self):
        self.player = Fighter(200, 1, self.selected_char)
        
        self.enemy = Fighter(1000, 2, "BALANCE", self.current_level)
        self.enemy_ai = EnemyAI(self.enemy, self.current_level, self)
        
        self.projectiles = []
        self.round_time = 60
        self.frame_count = 0
        self.game_over = False
        self.winner = None
        self.start_delay = 60
        
    def handle_input(self):
        if self.state == "SELECT":
            self.handle_select_input()
        elif self.state == "GAME":
            self.handle_game_input()

    def handle_select_input(self):
        # キーボードのイベント処理はメインループで行われているが、
        # ここでは長押し防止のためイベントベースで処理したいところだが、
        # 簡易的にキー状態とタイマーで処理するか、メインループのイベントを渡す必要がある。
        # ここではシンプルにキー状態を見るが、押しっぱなしで高速移動しないようにタイマーを入れる。
        pass # イベントループで処理する形に変更するため、main関数側でイベントを渡す設計にするのが良いが、
             # 既存構造を維持するため、キー押下直後のフラグ管理などは難しい。
             # 仕方ないので、pygame.event.get() を main() で呼んでいるのを利用し、
             # Gameクラスにイベントを渡すメソッドを作る。

    def handle_events(self, event):
        if self.state == "SELECT":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.char_index = (self.char_index - 1) % len(self.char_list)
                    self.selected_char = self.char_list[self.char_index]
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.char_index = (self.char_index + 1) % len(self.char_list)
                    self.selected_char = self.char_list[self.char_index]
                elif event.key == pygame.K_z or event.key == pygame.K_RETURN:
                    self.start_game()

    def handle_game_input(self):
        keys = pygame.key.get_pressed()
        
        # 入力状態の更新（コマンド判定用）
        inputs = {
            "UP": keys[pygame.K_w] or keys[pygame.K_UP],
            "DOWN": keys[pygame.K_s] or keys[pygame.K_DOWN],
            "LEFT": keys[pygame.K_a] or keys[pygame.K_LEFT],
            "RIGHT": keys[pygame.K_d] or keys[pygame.K_RIGHT]
        }
        self.player.update_input(inputs)
        
        move_dir = 0
        if inputs["LEFT"]:
            move_dir = -1
        elif inputs["RIGHT"]:
            move_dir = 1
        self.player.move(move_dir)
        
        if inputs["UP"]:
            self.player.jump()
            
        # 攻撃・アクション
        if keys[pygame.K_z]:
            # コマンド判定
            if self.player.check_special_move():
                self.player.shoot(self)
            else:
                self.player.punch()
                
        if keys[pygame.K_x]:
            self.player.kick()
        if keys[pygame.K_SPACE]:
            self.player.slide()
            
        # Guard input
        if inputs["DOWN"]:
            self.player.guard(True)
        else:
            self.player.guard(False)
            
        if keys[pygame.K_r] and (self.game_over or self.game_cleared):
            self.state = "SELECT" # リスタート時はキャラ選択へ

    def update(self):
        if self.state != "GAME":
            return

        if self.start_delay > 0:
            self.start_delay -= 1
            return

        if self.game_over or self.game_cleared:
            return
        
        self.player.update(self.enemy)
        self.enemy_ai.update(self.player)
        self.enemy.update(self.player)
        
        # 飛び道具の更新
        for p in self.projectiles[:]:
            p.update()
            if not p.active:
                self.projectiles.remove(p)
        
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
        # 通常攻撃の判定
        p_attack = self.player.get_attack_rect()
        if p_attack and p_attack.colliderect(self.enemy.get_hurt_rect()):
            damage = 10 * self.player.power_mult
            if self.player.is_kicking: damage = 15 * self.player.power_mult
            if self.player.is_sliding: damage = 12 * self.player.power_mult
            self.enemy.take_damage(damage)
                
        e_attack = self.enemy.get_attack_rect()
        if e_attack and e_attack.colliderect(self.player.get_hurt_rect()):
            damage = 10 + (self.current_level * 2)
            damage *= self.enemy.power_mult
            self.player.take_damage(damage)
            
        # 飛び道具の判定
        for p in self.projectiles:
            if not p.active: continue
            
            target = None
            if p.owner == self.player:
                target = self.enemy
            else:
                target = self.player
                
            if p.get_rect().colliderect(target.get_hurt_rect()):
                damage = 15 * p.owner.power_mult
                target.take_damage(damage)
                p.active = False # 当たったら消える
                
    def end_round(self):
        self.game_over = True
        
        if self.player.health > self.enemy.health:
            self.winner = self.player
            if self.current_level < self.max_levels:
                pygame.time.delay(2000) 
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
        
        if self.state == "SELECT":
            self.draw_select_screen()
        elif self.state == "GAME":
            self.draw_game_screen()
            
    def draw_select_screen(self):
        screen.fill(BLACK)
        title = font_large.render("CHARACTER SELECT", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # キャラクター表示
        for i, char_name in enumerate(self.char_list):
            data = CHAR_TYPES[char_name]
            color = data["color"]
            if char_name == self.selected_char:
                # 選択中のキャラを強調
                pygame.draw.rect(screen, WHITE, (150 + i*300 - 10, 200 - 10, 220, 320), 5)
                
            # 簡易的なキャラの絵
            x = 150 + i*300 + 100
            y = 400
            pygame.draw.ellipse(screen, color, (x - 25, y - 80, 50, 60))
            pygame.draw.circle(screen, SKIN_COLOR, (x, y - 90), 20)
            
            name_text = font_medium.render(char_name, True, WHITE)
            screen.blit(name_text, (x - name_text.get_width()//2, 450))
            
            # パラメータ表示
            stats = f"HP:{data['hp']} SPD:{data['speed']} PWR:{data['power']}"
            stat_text = font_small.render(stats, True, GRAY)
            screen.blit(stat_text, (x - stat_text.get_width()//2, 490))
            
        desc = CHAR_TYPES[self.selected_char]["desc"]
        desc_text = font_medium.render(desc, True, YELLOW)
        screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, 550))

    def draw_game_screen(self):
        pygame.draw.rect(screen, GRASS_GREEN, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        pygame.draw.line(screen, (50, 100, 50), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 3)
        
        self.player.draw(screen)
        self.enemy.draw(screen)
        
        for p in self.projectiles:
            p.draw(screen)
            
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
        
        guide = font_small.render("Move:Arrow  Attack:Z/X  Guard:Down  Hadoken:Down->Fwd+Z", True, WHITE)
        screen.blit(guide, (20, SCREEN_HEIGHT - 40))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        text = font_large.render("GAME OVER", True, RED)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        info = font_medium.render(f"Reached Stage: {self.current_level}", True, WHITE)
        screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        retry = font_medium.render("Press R to Select Character", True, WHITE)
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
        
        msg = font_medium.render("Congratulations! You won!", True, BLACK)
        screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        retry = font_medium.render("Press R to Select Character", True, BLACK)
        screen.blit(retry, (SCREEN_WIDTH//2 - retry.get_width()//2, SCREEN_HEIGHT//2 + 100))



async def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # イベントをGameクラスに渡す
            game.handle_events(event)
        
        game.handle_input()
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)  # Essential for pygbag

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
