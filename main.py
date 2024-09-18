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
import os
import math

pygame.init()
display = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("The Dinosaur Game")
icon = pygame.image.load('assets/dino_icon.png').convert_alpha()
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
game_speed = 0

ground = pygame.image.load('assets/ground.png').convert_alpha()
ground_height = 40
ground = pygame.transform.scale(ground, (1280, ground_height))

class Cloud(pygame.sprite.Sprite):
    def __init__(self, start_y):
        super().__init__()
        self.image = pygame.image.load(r'C:\Users\kchon\Documents\Github\Dino_AI\assets\cloud.png').convert_alpha()
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

        # self.jump_sound = pygame.mixer.Sound('assets/sfx/jump.mp3')
        # self.jump_sound.set_volume(0.5)

    def player_input(self, action):
        if action == 2:
            if self.rect.bottom < 700:
                self.gravity += 1
            else:
                self.ducking = True   
        else:
            self.ducking = False
            if action == 0 and self.rect.bottom >= 700:
                self.gravity = 0
                self.gravity -= 25
                # self.jump_sound.play()
            elif action == 1 and self.rect.bottom >= 700:
                self.gravity = 0
                self.gravity -= 15
                # self.jump_sound.play()       


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
    
    def update(self, action):
        self.player_input(action)
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
        self.height = random.randint(0, 2)
        if self.height == 0:
            self.rect = self.image.get_rect(center=(1380, 550))
        elif self.height == 1:
            self.rect = self.image.get_rect(center=(1380, 600))
        else:
            self.rect = self.image.get_rect(center=(1380, 650))

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

def check_collision(sprite, pteros, cacti):
	if pygame.sprite.spritecollide(sprite, pteros, False) or pygame.sprite.spritecollide(sprite, cacti, False):
		return True
	return False

def euclid_dist(a, b):
    dx = a.rect.x - b.rect.x
    dy = a.rect.y - b.rect.y
    return math.sqrt(dx**2 + dy**2)/(100)

def get_params(player, pteros, cacti):
    # dist to next, height of obstacle, width of obstacle, obstacle y pos, bird height, speed, players y pos, gap between obstacles
    ptero_dists = []
    for ptero in pteros:
        ptero_dists.append((euclid_dist(player, ptero), ptero))

    cactus_dists = []
    for cactus in cacti:
        cactus_dists.append((euclid_dist(player, cactus), cactus))

    objs = ptero_dists + cactus_dists
    if len(objs) > 0:
        objs.sort(key=lambda x: x[0])
        near_obj_dist, near_obj_sprite = objs[0]
        obj_type = -1
        if near_obj_sprite in cacti:
            obj_type = 0
        else:
            obj_type = 1
        obs_height = near_obj_sprite.image.get_height()/100
        obs_width = near_obj_sprite.image.get_width()/100
        
        if len(ptero_dists) > 0:
            ptero_dists.sort(key=lambda x: x[0])
            _, bird_sprite = ptero_dists[0]
            bird_height = bird_sprite.height
        else:
            bird_height = -1

    else:
        return [0, 0, 0, 0, 0]

    return [near_obj_dist, obs_height, obs_width, bird_height, obj_type]
    
def eval_genomes(genomes, config):
    global display, game_speed, ground
    ground_1 = ground.copy()
    ground_2 = ground.copy()
    sky = pygame.Surface((1280, 720))
    sky.fill((0, 0, 0))

    players = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        sprite = pygame.sprite.GroupSingle()
        sprite.add(Player())
        players.append((genome_id, genome, net, sprite))

    start_speed = 10
    game_speed = start_speed

    ground_1_x = 0
    ground_2_x = 1280

    score = 0

    ptero_group = pygame.sprite.Group()
    cloud_group = pygame.sprite.Group()
    cacti_group = pygame.sprite.Group()

    # Timer 
    cloud_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(cloud_timer, 1500)

    enemy_spawn_wait = 1000
    obstacle_timer = pygame.USEREVENT + 2
    pygame.time.set_timer(obstacle_timer, enemy_spawn_wait)

    start_time = pygame.time.get_ticks()

    # Game Loop
    while len(players) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == cloud_timer:
                cloud_group.add(Cloud(random.randint(240, 480)))
            if event.type == obstacle_timer:
                if pygame.time.get_ticks()-start_time > 10000:
                    spawn = random.randint(1, 10)
                    if  spawn <= 6:
                        cacti_group.add(Cactus(spawn))
                    else:
                        ptero_group.add(Ptero())
                else:
                    spawn = random.randint(1, 6)
                    cacti_group.add(Cactus(spawn))

        players = [p for p in players if check_collision(p[3].sprite, ptero_group, cacti_group) == False]

        if len(players) > 0:
            game_speed += .0025
            score += game_speed

            for i in range(len(players)):
                players[i][1].fitness = score/10

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

            for dino in players:
                dino[3].draw(display)
                params = get_params(dino[3].sprite, ptero_group.sprites(), cacti_group.sprites())
                params.append(1/(1+math.exp(-1*(game_speed/start_speed))))
                params.append(dino[3].sprite.rect.y/240)
                out = dino[2].activate(params)
                # print(dino[0], out)
                action = out.index(max(out))
                dino[3].update(action)

            display_score(score)

            pygame.display.update()

            clock.tick(60)
        else:
            game_speed = 0
    for genome_id, genome in genomes:
        print(genome_id, genome.fitness)

def run(config_file):
    # loading NEAT config settings
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                         config_file)
    # Create the initial population (top-level obj for a run of NEAT)
    p = neat.Population(config)

    winner = p.run(eval_genomes, 50)

    pygame.quit()

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)   