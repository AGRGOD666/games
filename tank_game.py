import pygame
import math
import asyncio
import platform
import random
import pygame.gfxdraw

# 初始化Pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 600
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

# 游戏状态
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_GAMEOVER = 2
game_state = GAME_STATE_MENU

# 坦克类
class Tank:
    def __init__(self, x, y, color=GREEN, is_player=True):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 3 if is_player else random.uniform(0.5, 2)
        self.size = 30
        self.color = color
        self.is_player = is_player
        self.last_shot = 0
        self.shoot_interval = 1000 if is_player else 2000  # 敌人射击间隔增加到2秒
        self.alive = True
        self.explosion_time = 0
        self.explosion_duration = 500  # 爆炸效果持续0.5秒

    def move(self, keys=None):
        if self.is_player:
            if keys[pygame.K_w]:  # 向前移动
                self.x += self.speed * math.cos(math.radians(self.angle))
                self.y -= self.speed * math.sin(math.radians(self.angle))
            if keys[pygame.K_s]:  # 向后移动
                self.x -= self.speed * math.cos(math.radians(self.angle))
                self.y += self.speed * math.sin(math.radians(self.angle))
            if keys[pygame.K_a]:  # 左转
                self.angle += 3
            if keys[pygame.K_d]:  # 右转
                self.angle -= 3
            if keys[pygame.K_UP]:  # 向前移动
                self.x += self.speed * math.cos(math.radians(self.angle))
                self.y -= self.speed * math.sin(math.radians(self.angle))
            if keys[pygame.K_DOWN]:  # 向后移动
                self.x -= self.speed * math.cos(math.radians(self.angle))
                self.y += self.speed * math.sin(math.radians(self.angle))
            if keys[pygame.K_LEFT]:  # 左转
                self.angle += 3
            if keys[pygame.K_RIGHT]:  # 右转
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

    def draw(self, current_time):
        if not self.alive:
            if current_time - self.explosion_time < self.explosion_duration:
                # 绘制爆炸效果
                radius = 10 + (current_time - self.explosion_time) / self.explosion_duration * 20
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y), radius), 0)
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y), radius / 2), 0)
            return

        # 绘制坦克阴影
        shadow_offset = 5
        points = [
            (self.x + self.size * math.cos(math.radians(self.angle + 45)) + shadow_offset, self.y - self.size * math.sin(math.radians(self.angle + 45)) + shadow_offset),
            (self.x + self.size * math.cos(math.radians(self.angle + 135)) + shadow_offset, self.y - self.size * math.sin(math.radians(self.angle + 135)) + shadow_offset),
            (self.x + self.size * math.cos(math.radians(self.angle + 225)) + shadow_offset, self.y - self.size * math.sin(math.radians(self.angle + 225)) + shadow_offset),
            (self.x + self.size * math.cos(math.radians(self.angle + 315)) + shadow_offset, self.y - self.size * math.sin(math.radians(self.angle + 315)) + shadow_offset)
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

    def shoot(self, current_time):
        if not self.alive:
            return None
        if self.is_player:
            bullet_x = self.x + self.size * math.cos(math.radians(self.angle))
            bullet_y = self.y - self.size * math.sin(math.radians(self.angle))
            return Bullet(bullet_x, bullet_y, self.angle, is_player=True)
        else:
            if current_time - self.last_shot > self.shoot_interval:
                self.last_shot = current_time
                angle_to_player = math.degrees(math.atan2(self.y - player.y, player.x - self.x))
                # 添加随机偏移降低命中率
                angle_to_player += random.uniform(-15, 15)
                bullet_x = self.x + self.size * math.cos(math.radians(angle_to_player))
                bullet_y = self.y - self.size * math.sin(math.radians(angle_to_player))
                return Bullet(bullet_x, bullet_y, angle_to_player, is_player=False)
        return None

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
player = Tank(WIDTH // 2, HEIGHT // 2, GREEN, True)
enemies = [Tank(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50), BLUE, False) for _ in range(2)]  # 减少到2个敌人
bullets = []
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
    start_text = font.render("按 ENTER 开始游戏", True, GREEN)
    quit_text = font.render("按 Q 退出游戏", True, RED)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2))
    screen.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, HEIGHT // 2 + 60))
    pygame.display.flip()

def handle_menu():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # ENTER键开始游戏
                reset_game()
                return True
            if event.key == pygame.K_q:  # Q键退出游戏
                return False
    return None

def restart_screen():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("游戏结束", True, RED)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))

    font = pygame.font.Font(None, 50)
    restart_text = font.render("按 R 重新开始", True, GREEN)
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

def reset_game():
    global player, enemies, bullets
    player = Tank(WIDTH // 2, HEIGHT // 2, GREEN, True)
    enemies = [Tank(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50), BLUE, False) for _ in range(2)]
    bullets = []

def setup():
    pass

async def main():
    global game_state
    setup()
    running = True
    while running:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

def update_loop():
    global game_state
    
    if game_state == GAME_STATE_MENU:
        draw_menu()
        result = handle_menu()
        if result is False:
            pygame.quit()
            exit()
        elif result is True:
            game_state = GAME_STATE_PLAYING
        return
    
    if game_state == GAME_STATE_GAMEOVER:
        action = restart_screen()
        if action == "restart":
            reset_game()
            game_state = GAME_STATE_PLAYING
        elif action == "menu":
            game_state = GAME_STATE_MENU
        elif action == "quit":
            pygame.quit()
            exit()
        return

    # 游戏进行中的逻辑
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_j, pygame.K_SPACE] and player.alive:  # 玩家按下 J 或 SPACE 键射击
                bullet = player.shoot(pygame.time.get_ticks())
                if bullet:
                    bullets.append(bullet)

    # 获取键盘输入
    keys = pygame.key.get_pressed()
    if player.alive:
        player.move(keys)

    # 更新敌人
    current_time = pygame.time.get_ticks()
    for enemy in enemies:
        if enemy.alive:
            enemy.move()
            bullet = enemy.shoot(current_time)
            if bullet:
                bullets.append(bullet)

    # 更新子弹并检查碰撞
    for bullet in bullets[:]:
        bullet.move()
        if bullet.off_screen():
            bullets.remove(bullet)
            continue
        # 检查子弹与坦克的碰撞
        if bullet.is_player:
            for enemy in enemies:
                if enemy.alive and math.hypot(bullet.x - enemy.x, bullet.y - enemy.y) < enemy.size:
                    enemy.alive = False
                    enemy.explosion_time = current_time
                    bullets.remove(bullet)
                    break
        else:
            if player.alive and math.hypot(bullet.x - player.x, bullet.y - player.y) < player.size:
                player.alive = False
                player.explosion_time = current_time
                bullets.remove(bullet)

    # 绘制
    draw_background()
    if player.alive or current_time - player.explosion_time < player.explosion_duration:
        player.draw(current_time)
    for enemy in enemies:
        if enemy.alive or current_time - enemy.explosion_time < enemy.explosion_duration:
            enemy.draw(current_time)
    for bullet in bullets:
        bullet.draw()
    pygame.display.flip()

    # 控制帧率
    clock.tick(FPS)

    # 检查玩家失败
    if not player.alive and pygame.time.get_ticks() - player.explosion_time >= player.explosion_duration:
        game_state = GAME_STATE_GAMEOVER

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())