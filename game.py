import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 480
TITLE = "Simple Platformer"

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"
STATE_WIN = "win"

game_state = STATE_MENU
music_on = False  # começa desligada para combinar com o botão

platforms = [
    Rect(0, HEIGHT - 20, WIDTH, 20),
    Rect(450, 380, 150, 20),
    Rect(650, 400, 130, 20),
]

class Button:
    def __init__(self, text, center):
        self.text = text
        self.width = 200
        self.height = 50
        self.rect = Rect(center[0]-100, center[1]-25, self.width, self.height)
    def draw(self):
        screen.draw.filled_rect(self.rect, (50,100,50))
        screen.draw.text(self.text, center=self.rect.center, fontsize=30, color="white")
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

btn_start = Button("Start Game", (WIDTH//2, 180))
btn_music = Button("Music OFF", (WIDTH//2, 250))  # inicia OFF
btn_exit = Button("Exit", (WIDTH//2, 320))

class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 50
        self.y = HEIGHT - 20 - self.height
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.lives = 3
        self.dead = False
        self.frame = 0
        self.frame_counter = 0
        self.rect = Rect(self.x, self.y, self.width, self.height)
    def update(self):
        if self.dead:
            return
        self.vy += 0.8
        self.y += self.vy
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat) and self.vy >= 0:
                self.y = plat.top - self.height
                self.vy = 0
                self.on_ground = True
                self.rect = Rect(self.x, self.y, self.width, self.height)
        self.x += self.vx
        self.rect = Rect(self.x, self.y, self.width, self.height)
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vx > 0:
                    self.x = plat.left - self.width
                elif self.vx < 0:
                    self.x = plat.right
                self.rect = Rect(self.x, self.y, self.width, self.height)
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
        if self.on_ground and abs(self.vx) > 0:
            self.frame_counter += 1
            if self.frame_counter > 10:
                self.frame = (self.frame + 1) % 2
                self.frame_counter = 0
        else:
            self.frame = 0
    def draw(self):
        if self.dead:
            screen.blit("aliengreen_hurt", (self.x, self.y))
        elif not self.on_ground:
            screen.blit("aliengreen_jump", (self.x, self.y))
        else:
            img = "aliengreen_walk1" if self.frame == 0 else "aliengreen_walk2"
            if abs(self.vx) > 0:
                screen.blit(img, (self.x, self.y))
            else:
                screen.blit("aliengreen", (self.x, self.y))

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.width = 40
        self.height = 40
        self.x = x
        self.y = y
        self.type = enemy_type
        self.alive = True
        self.dead_timer = 0
        self.direction = 1
        self.speed = 1.5
        self.frame = 0
        self.frame_counter = 0
        self.left_limit = x - 50
        self.right_limit = x + 50
        self.rect = Rect(self.x, self.y, self.width, self.height)
    def update(self):
        if not self.alive:
            self.dead_timer += 1
            return
        self.x += self.speed * self.direction
        if self.x < self.left_limit or self.x > self.right_limit:
            self.direction *= -1
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.frame_counter += 1
        if self.frame_counter > 15:
            self.frame = (self.frame + 1) % 2
            self.frame_counter = 0
    def draw(self):
        if not self.alive:
            if self.dead_timer < 60:
                screen.blit(f"{self.type}_dead", (self.x, self.y))
            return
        if self.type == "bee":
            img = "bee_fly" if self.frame == 0 else "bee"
        elif self.type == "frog":
            img = "frog_leap" if self.frame == 0 else "frog"
        else:
            img = "worm_walk" if self.frame == 0 else "worm"
        screen.blit(img, (self.x, self.y))

player = Player()
enemies = [
    Enemy(470, 380 - 40, "frog"),
    Enemy(670, 400 - 40, "worm"),
    Enemy(200, HEIGHT - 20 - 40, "bee"),
]
goal_rect = Rect(WIDTH - 80, HEIGHT - 120, 60, 80)

def update():
    global game_state
    if game_state != STATE_PLAYING:
        return
    player.update()
    for enemy in enemies:
        enemy.update()
    for enemy in enemies:
        if enemy.alive and player.rect.colliderect(enemy.rect):
            if player.vy > 0 and player.y + player.height/2 < enemy.y:
                enemy.alive = False
                player.vy = -10
            else:
                player.lives -= 1
                if player.lives <= 0:
                    player.dead = True
                    game_state = STATE_GAMEOVER
                    if music_on:
                        music.play("lose")
                else:
                    player.x = 50
                    player.y = HEIGHT - 20 - player.height
                break
    if player.rect.colliderect(goal_rect):
        game_state = STATE_WIN
    keys = keyboard
    player.vx = 0
    if keys.left:
        player.vx = -3
    if keys.right:
        player.vx = 3
    if keys.up and player.on_ground:
        player.vy = -12
        sounds.jump.play()

def draw():
    screen.clear()
    screen.blit("backgroundcolorgrass", (0,0))
    if game_state == STATE_MENU:
        btn_start.draw()
        btn_music.text = "Music ON" if music_on else "Music OFF"
        btn_music.draw()
        btn_exit.draw()
    elif game_state == STATE_PLAYING:
        for plat in platforms:
            screen.draw.filled_rect(plat, (50,150,50))
        screen.blit("hud_gem_blue", (goal_rect.x, goal_rect.y))
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for i in range(player.lives):
            screen.blit("hud_heartfull", (10 + i*40, 10))
    elif game_state == STATE_GAMEOVER:
        screen.draw.text("Game Over!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="red")
        screen.draw.text("Press Enter to return", center=(WIDTH//2, HEIGHT//2+50), fontsize=30, color="black")
    elif game_state == STATE_WIN:
        screen.draw.text("You Win!", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="green")
        screen.draw.text("Press Enter to return", center=(WIDTH//2, HEIGHT//2+50), fontsize=30, color="black")

def on_mouse_down(pos):
    global game_state, music_on
    if game_state == STATE_MENU:
        if btn_start.is_clicked(pos):
            start_game()
        elif btn_music.is_clicked(pos):
            music_on = not music_on
            if music_on:
                music.play("theme")
            else:
                music.stop()
        elif btn_exit.is_clicked(pos):
            exit()

def start_game():
    global game_state, player, enemies
    player.__init__()
    enemies.clear()
    enemies.extend([
        Enemy(470, 380 - 40, "frog"),
        Enemy(670, 400 - 40, "worm"),
        Enemy(200, HEIGHT - 20 - 40, "bee"),
    ])
    game_state = STATE_PLAYING
    if music_on:
        music.play("theme")

def on_key_down(key):
    global game_state
    if game_state in (STATE_GAMEOVER, STATE_WIN):
        if key == keys.RETURN:
            game_state = STATE_MENU
            music.stop()

pgzrun.go()