import pygame
import math
import random
import pygame.gfxdraw

# 初始化Pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 1000, 800  # 加大地图尺寸
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("坦克游戏")

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
BLUE = (0, 0, 200)
DARK_BLUE = (0, 0, 150)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
PLAYER1_COLOR = (0, 200, 0)  # 绿色
PLAYER2_COLOR = (200, 0, 0)  # 红色

# 游戏状态
GAME_STATE_MENU = 0
GAME_STATE_PLAYING_SINGLE = 1
GAME_STATE_PLAYING_COOP = 2  # 添加双人模式状态
GAME_STATE_GAMEOVER = 3
GAME_STATE_VICTORY = 4
game_state = GAME_STATE_MENU

# 障碍物类
class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        # 添加阴影效果
        shadow = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, (100, 100, 100), shadow)
        pygame.draw.rect(screen, self.color, self.rect)
        # 添加边框
        pygame.draw.rect(screen, BLACK, self.rect, 2)

# 坦克类
class Tank:
    def __init__(self, x, y, color=GREEN, is_player=True, player_id=1):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 3 if is_player else random.uniform(0.5, 2)
        self.size = 30
        self.color = color
        self.is_player = is_player
        self.last_shot = 0
        self.shoot_interval = 1000 if is_player else 4000  # 增加敌人射击间隔到4秒
        self.alive = True
        self.explosion_time = 0
        self.explosion_duration = 500  # 爆炸效果持续0.5秒
        self.lives = 3 if is_player else 1  # 玩家有3条命，敌人1条命
        self.respawn_time = 0  # 重生计时器
        self.respawn_delay = 2000  # 重生延迟2秒
        self.armor = 3 if is_player else 1  # 玩家3点护甲，敌人1点护甲
        self.max_armor = 3 if is_player else 1
        self.invincible_time = 0  # 无敌时间
        self.invincible_duration = 3000  # 重生后3秒无敌
        self.player_id = player_id  # 添加玩家ID
        self.controls = {
            1: {  # 玩家1控制
                'up': pygame.K_w,
                'down': pygame.K_s,
                'left': pygame.K_a,
                'right': pygame.K_d,
                'shoot': pygame.K_SPACE
            },
            2: {  # 玩家2控制
                'up': pygame.K_UP,
                'down': pygame.K_DOWN,
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'shoot': pygame.K_RETURN
            }
        }
        self.shooting = False  # 添加射击状态标志
        self.shoot_cooldown = 500  # 射击后禁止移动的时间（毫秒）
        self.shoot_start_time = 0  # 记录开始射击的时间

    def is_invincible(self, current_time):
        return current_time - self.respawn_time < self.invincible_duration

    def move(self, keys=None):
        # 如果正在射击冷却中，禁止移动
        if self.shooting:
            return

        old_x, old_y = self.x, self.y
        if self.is_player:
            controls = self.controls[self.player_id]
            if keys[controls['up']]:  # 向前移动
                self.x += self.speed * math.cos(math.radians(self.angle))
                self.y -= self.speed * math.sin(math.radians(self.angle))
            if keys[controls['down']]:  # 向后移动
                self.x -= self.speed * math.cos(math.radians(self.angle))
                self.y += self.speed * math.sin(math.radians(self.angle))
            if keys[controls['left']]:  # 左转
                self.angle += 3
            if keys[controls['right']]:  # 右转
                self.angle -= 3
        else:
            # 敌人随机移动
            if random.random() < 0.02:
                self.speed = random.uniform(0.5, 2)
                self.angle = random.randint(0, 360)
            self.x += self.speed * math.cos(math.radians(self.angle))
            self.y -= self.speed * math.sin(math.radians(self.angle))

        # 边界检查
        self.x = max(self.size, min(WIDTH - self.size, self.x))
        self.y = max(self.size, min(HEIGHT - self.size, self.y))

        # 检查与障碍物的碰撞
        tank_rect = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
        for obstacle in obstacles:
            if tank_rect.colliderect(obstacle.rect):
                self.x, self.y = old_x, old_y
                break

    def draw(self, current_time):
        if not self.alive:
            if current_time - self.explosion_time < self.explosion_duration:
                # 增强爆炸效果
                progress = (current_time - self.explosion_time) / self.explosion_duration
                radius = int(10 + progress * 30)
                # 绘制爆炸光环
                for r in range(radius, radius-10, -2):
                    alpha = int(255 * (1 - progress))
                    explosion_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(explosion_surface, (*YELLOW, alpha), (r, r), r)
                    screen.blit(explosion_surface, (int(self.x-r), int(self.y-r)))
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), radius // 2)
            return

        # 无敌状态闪烁效果
        if self.is_invincible(current_time) and int(current_time / 200) % 2 == 0:
            return

        # 绘制坦克阴影
        shadow_offset = 5
        points = [
            (self.x + self.size * math.cos(math.radians(self.angle + 45)) + shadow_offset, 
             self.y - self.size * math.sin(math.radians(self.angle + 45)) + shadow_offset),
            (self.x + self.size * math.cos(math.radians(self.angle + 135)) + shadow_offset, 
             self.y - self.size * math.sin(math.radians(self.angle + 135)) + shadow_offset),
            (self.x + self.size * math.cos(math.radians(self.angle + 225)) + shadow_offset, 
             self.y - self.size * math.sin(math.radians(self.angle + 225)) + shadow_offset),
            (self.x + self.size * math.cos(math.radians(self.angle + 315)) + shadow_offset, 
             self.y - self.size * math.sin(math.radians(self.angle + 315)) + shadow_offset)
        ]
        pygame.gfxdraw.filled_polygon(screen, points, GRAY)

        # 绘制履带
        track_width = 8
        track_points = [
            (self.x + (self.size + track_width) * math.cos(math.radians(self.angle + 45)), 
             self.y - (self.size + track_width) * math.sin(math.radians(self.angle + 45))),
            (self.x + (self.size + track_width) * math.cos(math.radians(self.angle + 135)), 
             self.y - (self.size + track_width) * math.sin(math.radians(self.angle + 135))),
            (self.x + (self.size + track_width) * math.cos(math.radians(self.angle + 225)), 
             self.y - (self.size + track_width) * math.sin(math.radians(self.angle + 225))),
            (self.x + (self.size + track_width) * math.cos(math.radians(self.angle + 315)), 
             self.y - (self.size + track_width) * math.sin(math.radians(self.angle + 315)))
        ]
        pygame.gfxdraw.filled_polygon(screen, track_points, DARK_GREEN if self.is_player else DARK_BLUE)

        # 绘制坦克主体
        points = [
            (self.x + self.size * math.cos(math.radians(self.angle + 45)), self.y - self.size * math.sin(math.radians(self.angle + 45))),
            (self.x + self.size * math.cos(math.radians(self.angle + 135)), self.y - self.size * math.sin(math.radians(self.angle + 135))),
            (self.x + self.size * math.cos(math.radians(self.angle + 225)), self.y - self.size * math.sin(math.radians(self.angle + 225))),
            (self.x + self.size * math.cos(math.radians(self.angle + 315)), self.y - self.size * math.sin(math.radians(self.angle + 315)))
        ]
        pygame.gfxdraw.filled_polygon(screen, points, self.color)
        # 添加金属质感轮廓线
        pygame.gfxdraw.aapolygon(screen, points, BLACK)

        # 绘制装甲板凸起效果
        armor_size = self.size * 0.7
        armor_points = [
            (self.x + armor_size * math.cos(math.radians(self.angle + 45)), 
             self.y - armor_size * math.sin(math.radians(self.angle + 45))),
            (self.x + armor_size * math.cos(math.radians(self.angle + 135)), 
             self.y - armor_size * math.sin(math.radians(self.angle + 135))),
            (self.x + armor_size * math.cos(math.radians(self.angle + 225)), 
             self.y - armor_size * math.sin(math.radians(self.angle + 225))),
            (self.x + armor_size * math.cos(math.radians(self.angle + 315)), 
             self.y - armor_size * math.sin(math.radians(self.angle + 315)))
        ]
        pygame.gfxdraw.filled_polygon(screen, armor_points, DARK_GREEN if self.is_player else DARK_BLUE)

        # 绘制增强的炮管
        barrel_width = 6
        barrel_length = self.size * 1.2
        angle_rad = math.radians(self.angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        # 炮管主体
        end_x = self.x + barrel_length * cos_angle
        end_y = self.y - barrel_length * sin_angle
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), barrel_width)
        
        # 炮管末端加粗
        pygame.draw.circle(screen, BLACK, (int(end_x), int(end_y)), barrel_width//2)
        
        # 炮管基座
        pygame.draw.circle(screen, DARK_GREEN if self.is_player else DARK_BLUE, 
                         (int(self.x), int(self.y)), barrel_width+2)

        # 在坦克上方显示护甲值（仅对玩家显示）
        if self.is_player:
            armor_width = 40
            armor_height = 4
            armor_x = self.x - armor_width//2
            armor_y = self.y - self.size - 10
            # 绘制护甲条背景
            pygame.draw.rect(screen, GRAY, (armor_x, armor_y, armor_width, armor_height))
            # 绘制当前护甲值
            armor_remaining = (armor_width * self.armor) // self.max_armor
            if self.armor > 0:
                pygame.draw.rect(screen, BLUE, (armor_x, armor_y, armor_remaining, armor_height))

    def shoot(self, current_time):
        if not self.alive or self.shooting:
            return None
            
        # 设置射击状态和时间
        self.shooting = True
        self.shoot_start_time = current_time

        # 计算炮管末端位置的通用函数
        def get_barrel_end_position(angle):
            barrel_length = self.size * 1.2  # 与绘制炮管时使用的长度相同
            end_x = self.x + barrel_length * math.cos(math.radians(angle))
            end_y = self.y - barrel_length * math.sin(math.radians(angle))
            return end_x, end_y

        if self.is_player:
            bullet_x, bullet_y = get_barrel_end_position(self.angle)
            return Bullet(bullet_x, bullet_y, self.angle, is_player=True)
        else:
            if current_time - self.last_shot > self.shoot_interval:
                self.last_shot = current_time
                # 计算瞄准玩家的角度
                angle_to_player = math.degrees(math.atan2(self.y - player.y, player.x - self.x))
                # 添加随机偏移来降低命中率
                firing_angle = angle_to_player + random.uniform(-15, 15)
                # 从当前朝向的炮管末端发射
                bullet_x, bullet_y = get_barrel_end_position(firing_angle)
                self.angle = firing_angle  # 更新坦克朝向，使其面向射击方向
                return Bullet(bullet_x, bullet_y, firing_angle, is_player=False)
        return None

    def respawn(self, current_time):
        if not self.alive and self.lives > 0 and current_time - self.explosion_time >= self.explosion_duration:
            self.alive = True
            # 在安全位置重生
            self.x, self.y = find_safe_position(self.size)
            self.angle = random.randint(0, 360)
            self.lives -= 1
            self.armor = self.max_armor  # 重置护甲值
            self.respawn_time = current_time
            return True
        return False

# 子弹类
class Bullet:
    def __init__(self, x, y, angle, is_player=True):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 7
        self.radius = 5
        self.is_player = is_player

    def move(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))
        
        # 检查与障碍物的碰撞
        bullet_rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                                self.radius * 2, self.radius * 2)
        for obstacle in obstacles:
            if bullet_rect.colliderect(obstacle.rect):
                return True  # 返回True表示子弹击中障碍物
        return False

    def draw(self):
        color = RED if self.is_player else BLACK
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        # 添加子弹尾迹
        tail_length = 10
        tail_x = self.x - tail_length * math.cos(math.radians(self.angle))
        tail_y = self.y + tail_length * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, YELLOW, (self.x, self.y), (tail_x, tail_y), 2)

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

# 游戏变量
player = None
player2 = None
enemies = []
bullets = []
obstacles = []
score = 0
FPS = 60
clock = pygame.time.Clock()

def draw_gradient_background():
    for y in range(HEIGHT):
        color = (
            240 - int(100 * (y / HEIGHT)),  # 渐变的红色分量
            240 - int(100 * (y / HEIGHT)),  # 渐变的绿色分量
            240  # 固定的蓝色分量
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def draw_background():
    draw_gradient_background()
    # 绘制网格
    grid_size = 50
    for x in range(0, WIDTH, grid_size):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, grid_size):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)

def draw_menu():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    title = font.render("坦克大战", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))

    font = pygame.font.Font(None, 50)
    single_text = font.render("按 1 进入单人模式", True, GREEN)
    coop_text = font.render("按 2 进入双人模式", True, BLUE)
    quit_text = font.render("按 Q 退出游戏", True, RED)
    
    screen.blit(single_text, (WIDTH // 2 - single_text.get_width() // 2, HEIGHT // 2))
    screen.blit(coop_text, (WIDTH // 2 - coop_text.get_width() // 2, HEIGHT // 2 + 60))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 120))
    pygame.display.flip()

def handle_menu():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:  # 1键进入单人模式
                reset_game(is_coop=False)
                return "single"
            if event.key == pygame.K_2:  # 2键进入双人模式
                reset_game(is_coop=True)
                return "coop"
            if event.key == pygame.K_q:
                return False
    return None

def restart_screen():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("游戏结束", True, RED)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

    # 显示得分
    font = pygame.font.Font(None, 50)
    score_text = font.render(f"最终得分: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 60))

    restart_text = font.render("按 R 重新开始", True, GREEN)
    menu_text = font.render("按 M 返回主菜单", True, BLUE)
    quit_text = font.render("按 Q 退出游戏", True, RED)
    
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 60))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 120))

    # 添加游戏说明
    font = pygame.font.Font(None, 36)
    hint_text = font.render("WASD或方向键控制移动，空格或J键发射", True, BLACK)
    screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT - 50))
    
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return "restart"
            if event.key == pygame.K_m:
                return "menu"
            if event.key == pygame.K_q:
                return "quit"
    return None

def draw_victory_screen():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("胜利!", True, GREEN)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

    font = pygame.font.Font(None, 50)
    score_text = font.render(f"最终得分: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 60))

    restart_text = font.render("按 R 再来一局", True, GREEN)
    menu_text = font.render("按 M 返回主菜单", True, BLUE)
    quit_text = font.render("按 Q 退出游戏", True, RED)
    
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 60))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 120))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return "restart"
            if event.key == pygame.K_m:
                return "menu"
            if event.key == pygame.K_q:
                return "quit"
    return None

def game_over_screen():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("你失去了一条生命!", True, RED)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

    font = pygame.font.Font(None, 50)
    if player.lives > 0:
        continue_text = font.render("按 SPACE 继续游戏", True, GREEN)
        screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2))
    else:
        game_over_text = font.render("游戏结束", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    
    menu_text = font.render("Press M back to menu. ", True, BLUE)
    quit_text = font.render("Press Q to quit game.", True, RED)
    screen.blit(menu_text, (WIDTH // 2 - menu_text.get_width() // 2, HEIGHT // 2 + 60))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 120))
    
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player.lives > 0:
                return "continue"
            if event.key == pygame.K_m:
                return "menu"
            if event.key == pygame.K_q:
                return "quit"
    return None

def is_valid_position(x, y, size):
    # 检查位置是否与任何障碍物重叠
    tank_rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
    for obstacle in obstacles:
        if tank_rect.colliderect(obstacle.rect):
            return False
    return True

def find_safe_position(size, zone="any"):
    """增强的安全位置查找函数，支持区域选择"""
    for _ in range(100):
        if zone == "player1":
            x = random.randint(size, WIDTH // 4)  # 左侧1/4地图
            y = random.randint(size, HEIGHT - size)
        elif zone == "player2":
            x = random.randint(WIDTH * 3 // 4, WIDTH - size)  # 右侧1/4地图
            y = random.randint(size, HEIGHT - size)
        elif zone == "enemy":
            x = random.randint(WIDTH // 3, WIDTH * 2 // 3)  # 中间1/3地图
            y = random.randint(size, HEIGHT - size)
        else:
            x = random.randint(size, WIDTH - size)
            y = random.randint(size, HEIGHT - size)
        
        if is_valid_position(x, y, size):
            return x, y
    return WIDTH // 2, HEIGHT // 2

def reset_game(is_coop=False):
    global player, player2, enemies, bullets, obstacles, score, WIDTH, HEIGHT
    
    # 设置更大的地图
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    # 先创建障碍物，增加到15个
    obstacles = []
    for _ in range(15):
        width = random.randint(40, 100)
        height = random.randint(40, 100)
        x = random.randint(0, WIDTH - width)
        y = random.randint(0, HEIGHT - height)
        obstacles.append(Obstacle(x, y, width, height))
    
    # 在左侧创建玩家1
    x, y = find_safe_position(30, "player1")
    player = Tank(x, y, PLAYER1_COLOR, True, player_id=1)
    player.lives = 3
    
    # 创建玩家2（如果是双人模式）
    player2 = None
    if is_coop:
        x, y = find_safe_position(30, "player2")
        player2 = Tank(x, y, PLAYER2_COLOR, True, player_id=2)
        player2.lives = 3
    
    # 在中间区域生成敌人
    enemies = []
    enemy_count = 6 if is_coop else 3
    for _ in range(enemy_count):
        x, y = find_safe_position(30, "enemy")
        enemy = Tank(x, y, BLUE, False)
        # 双人模式下降低敌人属性
        if is_coop:
            enemy.speed = random.uniform(0.2, 1.0)  # 降低速度
            enemy.shoot_interval = 5000  # 增加射击间隔到5秒
            enemy.armor = 2  # 降低护甲
        else:
            enemy.speed = random.uniform(0.3, 1.5)
            enemy.shoot_interval = 3000
        enemies.append(enemy)
    
    bullets = []
    score = 0

def draw_score():
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"得分: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

def draw_lives():
    if not player:
        return
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f"生命值: {player.lives}  护甲值: {player.armor}", True, RED)
    screen.blit(lives_text, (10, 50))
    if player2:
        lives_text2 = font.render(f"玩家2生命值: {player2.lives}  护甲值: {player2.armor}", True, RED)
        screen.blit(lives_text2, (10, 90))

def setup():
    global game_state, player
    game_state = GAME_STATE_MENU
    # Initialize a temporary player for menu state
    x, y = find_safe_position(30, "player1")
    player = Tank(x, y, PLAYER1_COLOR, True, player_id=1)

def update_loop():
    global game_state, score, player, player2
    
    current_time = pygame.time.get_ticks()

    # Menu state handling
    if game_state == GAME_STATE_MENU:
        draw_menu()
        result = handle_menu()
        if result is False:
            return False
        elif result == "single":
            game_state = GAME_STATE_PLAYING_SINGLE
            reset_game(is_coop=False)
        elif result == "coop":
            game_state = GAME_STATE_PLAYING_COOP
            reset_game(is_coop=True)
        return True

    # Only update shooting status during gameplay if player exists
    if game_state in [GAME_STATE_PLAYING_SINGLE, GAME_STATE_PLAYING_COOP] and player:
        if player.shooting and current_time - player.shoot_start_time > player.shoot_cooldown:
            player.shooting = False
        if player2 and player2.shooting and current_time - player2.shoot_start_time > player2.shoot_cooldown:
            player2.shooting = False
        for enemy in enemies:
            if enemy.shooting and current_time - enemy.shoot_start_time > enemy.shoot_cooldown:
                enemy.shooting = False

    # 在游戏状态检查之前添加重生检查
    if game_state in [GAME_STATE_PLAYING_SINGLE, GAME_STATE_PLAYING_COOP]:
        if not player.alive:
            if player.respawn(current_time):
                # 重置敌人位置，避免重生后立即被击中
                for enemy in enemies:
                    if enemy.alive:
                        enemy.x = random.randint(50, WIDTH-50)
                        enemy.y = random.randint(50, HEIGHT-50)
            elif player.lives <= 0:
                game_state = GAME_STATE_GAMEOVER
        if player2 and not player2.alive:
            if player2.respawn(current_time):
                for enemy in enemies:
                    if enemy.alive:
                        enemy.x = random.randint(50, WIDTH-50)
                        enemy.y = random.randint(50, HEIGHT-50)
            elif player2.lives <= 0:
                game_state = GAME_STATE_GAMEOVER
    
    if game_state == GAME_STATE_GAMEOVER:
        action = game_over_screen()
        if action == "continue":
            player.respawn(current_time)
            if player2:
                player2.respawn(current_time)
            game_state = GAME_STATE_PLAYING_SINGLE if not player2 else GAME_STATE_PLAYING_COOP
        elif action == "menu":
            game_state = GAME_STATE_MENU
        elif action == "quit":
            pygame.quit()
            exit()
        return True

    if game_state == GAME_STATE_VICTORY:
        action = draw_victory_screen()
        if action == "restart":
            reset_game(is_coop=(game_state == GAME_STATE_PLAYING_COOP))
            game_state = GAME_STATE_PLAYING_SINGLE if not player2 else GAME_STATE_PLAYING_COOP
        elif action == "menu":
            game_state = GAME_STATE_MENU
        elif action == "quit":
            pygame.quit()
            exit()
        return True

    # 游戏进行中的逻辑
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if player.alive and event.key == player.controls[player.player_id]['shoot']:  # 玩家1射击
                bullet = player.shoot(pygame.time.get_ticks())
                if bullet:
                    bullets.append(bullet)
            if player2 and player2.alive and event.key == player2.controls[player2.player_id]['shoot']:  # 玩家2射击
                bullet = player2.shoot(pygame.time.get_ticks())
                if bullet:
                    bullets.append(bullet)

    # 获取键盘输入
    keys = pygame.key.get_pressed()
    if player.alive:
        player.move(keys)
    if player2 and player2.alive:
        player2.move(keys)

    # 更新敌人
    for enemy in enemies:
        if enemy.alive:
            enemy.move()
            bullet = enemy.shoot(current_time)
            if bullet:
                bullets.append(bullet)

    # 更新子弹并检查碰撞
    for bullet in bullets[:]:
        if bullet.move():  # 如果子弹击中障碍物
            bullets.remove(bullet)
            continue
        if bullet.off_screen():
            bullets.remove(bullet)
            continue
        # 检查子弹与坦克的碰撞
        if bullet.is_player:
            for enemy in enemies:
                if enemy.alive and math.hypot(bullet.x - enemy.x, bullet.y - enemy.y) < enemy.size:
                    enemy.armor -= 1
                    if enemy.armor <= 0:
                        enemy.alive = False
                        enemy.explosion_time = current_time
                        score += 100
                    bullets.remove(bullet)
                    break
        else:
            if player.alive and math.hypot(bullet.x - player.x, bullet.y - player.y) < player.size:
                if not player.is_invincible(current_time):
                    player.armor -= 1
                    if player.armor <= 0:
                        player.alive = False
                        player.explosion_time = current_time
                bullets.remove(bullet)
                continue
            if player2 and player2.alive and math.hypot(bullet.x - player2.x, bullet.y - player2.y) < player2.size:
                if not player2.is_invincible(current_time):
                    player2.armor -= 1
                    if player2.armor <= 0:
                        player2.alive = False
                        player2.explosion_time = current_time
                bullets.remove(bullet)
                continue

    # 绘制
    draw_background()
    for obstacle in obstacles:
        obstacle.draw()
    if player.alive or current_time - player.explosion_time < player.explosion_duration:
        player.draw(current_time)
    if player2 and (player2.alive or current_time - player2.explosion_time < player2.explosion_duration):
        player2.draw(current_time)
    for enemy in enemies:
        if enemy.alive or current_time - enemy.explosion_time < enemy.explosion_duration:
            enemy.draw(current_time)
    for bullet in bullets:
        bullet.draw()
    draw_score()  # 显示得分
    draw_lives()  # 添加生命值显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(FPS)

    # 检查胜利条件
    if player.alive and all(not enemy.alive for enemy in enemies):
        game_state = GAME_STATE_VICTORY

    # 检查玩家失败
    if not player.alive and pygame.time.get_ticks() - player.explosion_time >= player.explosion_duration:
        game_state = GAME_STATE_GAMEOVER
    if player2 and not player2.alive and pygame.time.get_ticks() - player2.explosion_time >= player2.explosion_duration:
        game_state = GAME_STATE_GAMEOVER

    return True

def main():
    global game_state
    setup()
    running = True
    while running:
        running = update_loop()
    pygame.quit()

if __name__ == "__main__":
    main()