import pygame
import pygame.display
import pygame.event
import pygame.font
import pygame.image
import pygame.key
import pygame.mixer
import pygame.sprite
import pygame.time
import pygame.transform 
import random
import neat

pygame.init()
display = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("The Dinosaur Game")
icon = pygame.image.load('assets/dino_icon.png').convert_alpha()
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
game_over = False

start_speed = 10
game_speed = start_speed

ground = pygame.image.load('assets/ground.png').convert_alpha()
ground_height = 40
ground = pygame.transform.scale(ground, (1280, ground_height))

ground_1 = ground.copy()
ground_1_x = 0
ground_2 = ground.copy()
ground_2_x = 1280

sky = pygame.Surface((1280, 720))
sky.fill((0, 0, 0))

class Cloud(pygame.sprite.Sprite):
    def __init__(self, start_y):
        super().__init__()
        self.image = pygame.image.load('assets/cloud.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 80))
        self.rect = self.image.get_rect(bottomleft=(1280, start_y))

    def update(self):
        self.rect.x -= game_speed

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        running_1 = pygame.image.load('assets/Dino1.png').convert_alpha()
        running_1 = pygame.transform.scale(running_1, (80, 100))
        running_2 = pygame.image.load('assets/Dino2.png').convert_alpha()
        running_2 = pygame.transform.scale(running_2, (80, 100))
        self.running_frames = [running_1, running_2]

        ducking_1 = pygame.image.load('assets/DinoDucking1.png').convert_alpha()
        ducking_1 = pygame.transform.scale(ducking_1, (110, 60))
        ducking_2 = pygame.image.load('assets/DinoDucking2.png').convert_alpha()
        ducking_2 = pygame.transform.scale(ducking_2, (110, 60))
        self.ducking_frames = [ducking_1, ducking_2]

        jumping = pygame.image.load('assets/Dino1.png').convert_alpha()
        self.jumping_frame = pygame.transform.scale(jumping, (80, 100))

        self.player_state = 0
        self.image = self.running_frames[self.player_state]
        self.rect = self.image.get_rect(midbottom=(80, 700))
        self.gravity = 0
        self.ducking = False

        self.jump_sound = pygame.mixer.Sound('assets/sfx/jump.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 700:
            self.gravity = 0
            self.gravity -= 25
            self.jump_sound.play()
        elif keys[pygame.K_DOWN]:
            if self.rect.bottom < 700:
                self.gravity += 1
            else:
                self.ducking = True        
        else:
            self.ducking = False

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 700:
            self.rect.bottom = 700
    
    def animation_state(self):
        if self.rect.bottom < 700:
            self.image = self.jumping_frame
        elif self.ducking:
            self.player_state += 0.1
            if self.player_state >= len(self.ducking_frames):
                self.player_state = 0
            self.image = self.ducking_frames[int(self.player_state)]     
            self.rect = self.image.get_rect(midbottom=(110, 700))    
        else:
            self.player_state += 0.1
            if self.player_state >= len(self.running_frames):
                self.player_state = 0
            self.image = self.running_frames[int(self.player_state)] 
            self.rect = self.image.get_rect(midbottom=(80, 700))
    
    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Ptero(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        ptero_flying_1 = pygame.image.load('assets/Ptero1.png')
        ptero_flying_2 = pygame.image.load('assets/Ptero2.png')
        self.ptero_sprites = [pygame.transform.scale(ptero_flying_1, (84, 62)), pygame.transform.scale(ptero_flying_2, (84, 62))]
        self.state_index = 0
        self.image = self.ptero_sprites[self.state_index]

        self.rect = self.image.get_rect(center=(1380, random.choice([550, 600, 650])))

    def animation_state(self):
        self.state_index += 0.1
        if self.state_index > len(self.ptero_sprites):
            self.state_index = 0
        self.image = self.ptero_sprites[int(self.state_index)]
    
    def update(self):
        self.animation_state()
        self.rect.x -= game_speed
        self.destroy()
    
    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

class Cactus(pygame.sprite.Sprite):
    def __init__(self, cactus_num):
        super().__init__()
        cactus = pygame.image.load(f'assets/cacti/cactus{cactus_num}.png')
        self.image = pygame.transform.scale(cactus, (100, 100))
        if cactus_num < 4:
            self.rect = self.image.get_rect(midbottom=(1380, 700))
        else:
            self.rect = self.image.get_rect(midbottom=(1380, 710))
    
    def update(self):
        self.rect.x -= game_speed
        self.destroy()
    
    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

def display_score(score):
    font = pygame.font.Font("./assets/PressStart2P-Regular.ttf", 24)
    score_surf = font.render(f'Score: {(int(score/10)):07}', True, (128, 128, 128))
    score_rect = score_surf.get_rect(topright = (1270,10))
    display.blit(score_surf, score_rect)

def check_collision():
	if pygame.sprite.spritecollide(player.sprite, ptero_group, False) or pygame.sprite.spritecollide(player.sprite, cacti_group, False):
		return True
	return False

# def eval_genomes():

score = 0

ptero_group = pygame.sprite.Group()

player = pygame.sprite.GroupSingle()
player.add(Player())

cloud_group = pygame.sprite.Group()

cacti_group = pygame.sprite.Group()

# Timer 
cloud_timer = pygame.USEREVENT + 1
pygame.time.set_timer(cloud_timer, 1000)

enemy_spawn_wait = 2000
obstacle_timer = pygame.USEREVENT + 2
pygame.time.set_timer(obstacle_timer, enemy_spawn_wait)

# start_time = int(pygame.time.get_ticks() / 100)

# Game Loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == cloud_timer:
            cloud_group.add(Cloud(random.randint(240, 480)))
        if event.type == obstacle_timer:
            print(enemy_spawn_wait)
            if enemy_spawn_wait > 500:
                enemy_spawn_wait = int(enemy_spawn_wait * (0.99 ** (game_speed/start_speed)))
                pygame.time.set_timer(obstacle_timer, enemy_spawn_wait)
            spawn = random.randint(1, 10)
            if  spawn <= 6:
                cacti_group.add(Cactus(spawn))
            else:
                ptero_group.add(Ptero())

    if check_collision():
        game_over = True

    if not game_over:
        game_speed += .0025
        score += game_speed

        display.blit(sky, (0, 0))

        display.blit(ground_1, (ground_1_x, 720-ground_height))
        display.blit(ground_2, (ground_2_x, 720-ground_height))

        ground_1_x -= game_speed
        ground_2_x -= game_speed

        if ground_1_x < -1280:
            ground_1_x = 1280
        elif ground_2_x < -1280:
            ground_2_x = 1280
        
        cloud_group.draw(display)
        cloud_group.update()

        cacti_group.draw(display)
        cacti_group.update()

        ptero_group.draw(display)
        ptero_group.update()

        player.draw(display)
        player.update()

        display_score(score)

        pygame.display.update()

        clock.tick(60)
    else:
        game_speed = 0

pygame.quit()