game_state = "menu"
music.play("music.mp3")
music_on = True
win = False

# tilemap
TILE_SIZE = 18
COLS = 30
ROWS = 20
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

# botões do menu
btn_start = Rect((WIDTH//2 - 60, 150), (120, 40))
btn_sound = Rect((WIDTH//2 - 60, 210), (120, 40))
btn_quit = Rect((WIDTH//2 - 60, 270), (120, 40))

# Sprites
background = Actor('platformer.png')

# Posições Iniciais
pos = 270, 306

# Definindo caixas de colisão
# a cada 4 itens estão o x inicial, y inicial, x final e y final de cada seção de blocos (em linha e coluna)
boxes = [0,7,2,19,3,18,29,19,5,15,8,15,10,14,11,14,13,13,13,13,16,11,17,11,20,13,22,13,25,11,26,11,28,8,28,8,24,7,25,7,20,6,20,6,14,5,16,5,10,3,10,3,5,4,7,4,-1,-2,-1,19,30,-1,30,19]
def create_collision_boxes():
    collision_boxes = []
    for i in range(0, len(boxes), 4):
        x1, y1, x2, y2 = boxes[i], boxes[i+1], boxes[i+2], boxes[i+3]
        box = Rect(x1*TILE_SIZE, y1*TILE_SIZE,
                  (x2-x1+1)*TILE_SIZE, (y2-y1+1)*TILE_SIZE)
        collision_boxes.append(box)
    return collision_boxes
collision_boxes = create_collision_boxes()

# Definindo o Jogador
class Player:
    def __init__(self, image, pos):
        self.actor = Actor(image)
        self.actor.pos = pos
        self.vel_x = 0
        self.vel_y = 0
        self.jump_strength = 12
        self.gravity = 1
        self.on_ground = False
        self.speed = 4
        self.player_rect = Rect(
            pos[0] - self.actor.width/2 + 5,
            pos[1] - self.actor.height/2 + 1,
            self.actor.width - 10,
            self.actor.height - 1
        )

        # definindo objetivo (diamante)
        self.goal = Rect(18,90,18,18)

        # variáveis para som de andar
        self.step_timer = 0
        self.last_step_sound = 1

        # variáveis para animações do player
        self.anim_timer = 0
        self.anim_index = 0
        self.anim_state = "idle_right"
        self.animations = {"idle_right": ["player_idle_right1","player_idle_right2"],
                           "idle_left": ["player_idle_left1","player_idle_left2"],
                           "walk_right": ["player_walk_right","player_idle_right1"],
                           "walk_left": ["player_walk_left","player_idle_left1"],
                           "jump_right": ["player_walk_right"],
                           "jump_left": ["player_walk_left"]}
        self.facing = "right"
        self.actor.image = self.animations[self.anim_state][0]

    def _check_win(self):
        if self.player_rect.colliderect(self.goal):
            reset_game(True)

    def _update_animation_state(self):
        new_state = ""
        if not self.on_ground:
            new_state = f"jump_{self.facing}"
        elif self.vel_x != 0:
            new_state = f"walk_{self.facing}"
        else:
            new_state = f"idle_{self.facing}"

        # se o estado mudou então reinicia o frame da animação
        if new_state != self.anim_state:
            self.anim_state = new_state
            self.anim_index = 0
            self.anim_timer = 0
            self.actor.image = self.animations[self.anim_state][self.anim_index]

    def _update_animation_frame(self):
        frames = self.animations[self.anim_state]

        # se tiver só 1 frame não precisa animar (como o pulo)
        if len(frames) == 1:
            self.actor.image = frames[0]
            return

        self.anim_timer += 1
        if self.anim_timer >= 50: # velocidade da animação
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.actor.image = frames[self.anim_index]

    def _play_footsteps(self):
        if self.on_ground and self.vel_x != 0:
            self.step_timer += 1
            if self.step_timer > 20:  # intervalo dos sons
                if self.last_step_sound == 1:
                    sounds.step2.play()
                    self.last_step_sound = 2
                else:
                    sounds.step1.play()
                    self.last_step_sound = 1
                self.step_timer = 0
        else:
            self.step_timer = 20  # reinicia se parar de andar

    def update(self):
        self._handle_input()
        self._apply_gravity()
        self._update_animation_state()
        self._update_animation_frame()
        self._check_win()

        if music_on:
            self._play_footsteps()

        # eixo x
        self.player_rect.x += self.vel_x
        self._check_collision_x()
        # eixo y
        self.player_rect.y += self.vel_y
        self._check_collision_y()

        # atualizando sprite pelo rect
        self.actor.x = self.player_rect.x + self.player_rect.width/2 + 2
        self.actor.y = self.player_rect.y + self.player_rect.height/2 + 1

        # resetando vel_x para evitar aceleração infinita
        self.vel_x = 0

    def _handle_input(self):
        self.vel_x = 0
        if keyboard.right:
            self.vel_x = self.speed
            self.facing = "right"
        elif keyboard.left:
            self.vel_x = -self.speed
            self.facing = "left"
        if keyboard.up and self.on_ground: # Pulando
            self.vel_y = -self.jump_strength
            self.on_ground = False
            if music_on:
                sounds.jump.play()

    def _apply_gravity(self):
        self.vel_y += self.gravity
        if self.vel_y > 10:
            self.vel_y = 10 # aplica limite de velocidade de queda

    # Checando colisão horizontal
    def _check_collision_x(self):
        if self.vel_x == 0:
            return
        for box in collision_boxes:
            if self.player_rect.colliderect(box):
                if self.vel_x > 0:
                    self.player_rect.right = box.left
                elif self.vel_x < 0:
                    self.player_rect.left = box.right

    # checando colisão vertical
    def _check_collision_y(self):
        self.on_ground = False
        for box in collision_boxes:
            if self.player_rect.colliderect(box):
                if self.vel_y > 0: # caindo
                    self.player_rect.bottom = box.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0: # subindo
                    self.player_rect.top = box.bottom
                    self.vel_y = 0
    def draw(self):
        self.actor.draw()
player = Player("player_idle_right1", pos)

# Definindo os inimigos
class Enemy:
    def __init__(self, name, image, pos, direction, distance, speed):
        self.name = name
        self.actor = Actor(image)
        self.actor.pos = pos
        self.start_pos = pos
        self.direction = direction #horizontal ou vertical
        self.distance = distance
        self.speed = speed
        self.moving_forward = True

        self.pos_x = pos[0]
        self.pos_y = pos[1]

        # retângulo de colisão do inimigo
        self.rect = Rect(
                    self.actor.x - self.actor.width/2,
                    self.actor.y - self.actor.height/2,
                    self.actor.width,
                    self.actor.height
                    )
        # animação dos inimigos
        if name == "bird" or name == "fly":
            self.facing = "left"
        else:
            self.facing = "right"
        self.anim_state = self.facing

        self.anim_timer = 0
        self.anim_index = 0
        self.animations = {
            "right": [f"{name}_right1", f"{name}_right2"],
            "left": [f"{name}_left1", f"{name}_left2"]
        }
        self.actor.image = self.animations[self.anim_state][0]

    def update(self):
        # movimentação
        if self.direction == "horizontal":
            if self.moving_forward:
                self.pos_x += self.speed
                if self.pos_x > self.start_pos[0] + self.distance:
                    self.moving_forward = False
                    self.facing = "left"
                    self._update_facing_animation_frame()
            else:
                self.pos_x -= self.speed
                if self.pos_x < self.start_pos[0]:
                    self.moving_forward = True
                    self.facing = "right"
                    self._update_facing_animation_frame()
        else: #direction == "vertical"
            if self.moving_forward:
                self.pos_y += self.speed
                if self.pos_y > self.start_pos[1] + self.distance:
                    self.moving_forward = False
            else:
                self.pos_y -= self.speed
                if self.pos_y < self.start_pos[1]:
                    self.moving_forward = True
        self.anim_state = self.facing
        self.actor.pos = (int(self.pos_x), int(self.pos_y))
        self.rect.topleft = (
            self.actor.x - self.actor.width / 2,
            self.actor.y - self.actor.height / 2
        )
        #animação
        self._update_animation()

    def _update_animation(self):
        frames = self.animations[self.anim_state]
        self.anim_timer += 1
        if self.anim_timer >= 20:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.actor.image = frames[self.anim_index]

    def _update_facing_animation_frame(self):
        if self.direction == "horizontal":
            self.animations[f"{self.facing}"] = [
                f"{self.name}_{self.facing}1",
                f"{self.name}_{self.facing}2"
            ]
        self.anim_index = 0
        self.actor.image = self.animations[self.facing][0]

    def _check_collision_with_player(self, player_rect):
        return self.rect.colliderect(player_rect)

    def draw(self):
        self.actor.draw()
enemies = [
    Enemy("snake", "snake_right1", (369,226), "horizontal", 40, 0.5),
    Enemy("fly", "fly_left1", (198,108), "vertical", 85, 0.5),
    Enemy("owl", "owl_right1", (342,45), "horizontal", 180, 0.5),
    Enemy("bird", "bird_left1", (504,234), "vertical", 40, 0.5)
    ]

def reset_game(win):
    global player, enemies
    if not win and music_on:
        sounds.die.play()
    else:
        if music_on:
            sounds.win.play()
        win = False
    # Reiniciar o player na posição inicial
    player = Player("player_idle_right1", pos)

def on_mouse_down(pos):
    global game_state, music_on
    if game_state == "menu":
        if btn_start.collidepoint(pos):
            game_state = "playing"

        elif btn_sound.collidepoint(pos):
            music_on = not music_on
            if music_on:
                music.play("music.mp3")
            else:
                music.pause()

        elif btn_quit.collidepoint(pos):
            exit()

def draw():
    screen.clear()
    if game_state == "menu":
        screen.fill((30, 30, 60))
        screen.draw.text("ZIDO O ALIEN", center= (WIDTH//2, 80), fontsize=48, color="white")

        screen.draw.filled_rect(btn_start, (70, 160, 70))
        screen.draw.text("JOGAR", center=btn_start.center, fontsize=28, color="white")

        screen.draw.filled_rect(btn_sound, (70, 130, 130))
        label = "SOM"
        screen.draw.text(label, center=btn_sound.center, fontsize=28, color="white")
        if not music_on:
            screen.draw.line((WIDTH//2 - 60, 210), (WIDTH//2 + 60, 250), (255,255,255), 2)

        screen.draw.filled_rect(btn_quit, (160, 60, 60))
        screen.draw.text("SAIR", center=btn_quit.center, fontsize=28, color="white")
    else:
        background.draw()
        player.draw()
        for enemy in enemies:
            enemy.draw()

def update():
    if game_state == "menu":
        return
    player.update()
    for enemy in enemies:
        enemy.update()
        if enemy._check_collision_with_player(player.player_rect):
            reset_game(False)
            break
