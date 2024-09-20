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
import visualize

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

num_gens = 0
high_score = 0

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

def display_score(score, num_bots):
    font = pygame.font.Font("./assets/PressStart2P-Regular.ttf", 24)
    score_surf = font.render(f'Score: {(int(score/10)):07}', True, (128, 128, 128))
    score_rect = score_surf.get_rect(topright = (1270,10))
    hi_surf = font.render(f'High Score: {(int(high_score/10)):07}', True, (128, 128, 128))
    hi_rect = hi_surf.get_rect(topright = (1270,60))
    gen_surf = font.render(f'Generation: {(num_gens):02}', True, (128, 128, 128))
    gen_rect = gen_surf.get_rect(topleft = (10,10))
    alive_surf = font.render(f'Alive: {(num_bots):02}', True, (128, 128, 128))
    alive_rect = gen_surf.get_rect(topleft = (10,60))
    display.blit(gen_surf, gen_rect)
    display.blit(score_surf, score_rect)
    display.blit(alive_surf, alive_rect)
    display.blit(hi_surf, hi_rect)

def check_collision(sprite, pteros, cacti):
	if pygame.sprite.spritecollide(sprite, pteros, False) or pygame.sprite.spritecollide(sprite, cacti, False):
		return True
	return False

def euclid_dist(player, object):
    dx = player.rect.x - object.rect.x
    dy = player.rect.y - object.rect.y
    return math.sqrt(dx**2 + dy**2)/100

def get_closest_obj(player, objects):
    if len(objects) == 0:
        return (-1, None)
    min = (euclid_dist(player, objects[0]), objects[0])
    for obj in objects:
        dist = euclid_dist(player, obj)
        if dist < min[0]:
            min = (dist, obj)
    return min

def get_params(player, pteros, cacti):
    near_dist, near_obj = get_closest_obj(player, (pteros + cacti))
    obs_height = 0
    obs_width = 0
    # ptero_height = -1
    obj_y = -1
    obj_class = -1
    if near_obj != None:
        obs_height = near_obj.image.get_height()/100
        obs_width = near_obj.image.get_width()/100
        obj_y = near_obj.rect.y/720
        # if len(pteros) != 0:
        #     _, near_ptero = get_closest_obj(player, pteros)
        #     ptero_height = near_ptero.height
        if near_obj in pteros:
            obj_class = 0
        elif near_obj in cacti:
            obj_class = 1
    
    # return [near_dist, obs_height, obs_width, ptero_height, obj_class]
    return [near_dist, obs_height, obs_width, obj_y, obj_class]

def ducking_score(dino, ptero, out):
    if ptero.height == 0:
        if (dino.rect.x + dino.image.get_width()) > ptero.rect.x and dino.rect.x < (ptero.rect.x + ptero.image.get_width()):
            if out == 2:
                return 100
            else:
                return -100
    return 0

def eval_genomes(genomes, config):
    global display, game_speed, ground, num_gens, high_score
    ground_1 = ground.copy()
    ground_2 = ground.copy()
    sky = pygame.Surface((1280, 720))
    sky.fill((0, 0, 0))

    dino_bots = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        sprite = pygame.sprite.GroupSingle()
        sprite.add(Player())
        dino_bots.append((genome_id, genome, net, sprite))

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
    while len(dino_bots) > 0:
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

        for bot in dino_bots:
            if check_collision(bot[3].sprite, ptero_group, cacti_group):
                bot[1].fitness -= 500
                if high_score >= 1000000:
                    bot[1].fitness = high_score
                dino_bots.remove(bot)

        if len(dino_bots) > 0:
            game_speed += .0025
            score += game_speed
            if score > high_score:
                high_score = score

            for bot in dino_bots:
                bot[1].fitness += game_speed

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

            for bot in dino_bots:
                bot[3].draw(display)
                params = get_params(bot[3].sprite, ptero_group.sprites(), cacti_group.sprites())

                params.append((game_speed-start_speed)/start_speed)
                params.append(bot[3].sprite.rect.y/720)
                params.append(0.3)
                out = bot[2].activate(params)

                # print(bot[0], out)

                action = out.index(max(out))
                if len(ptero_group.sprites()) > 0:
                    _, closest_ptero = get_closest_obj(bot[3].sprite, ptero_group.sprites())
                    bot[1].fitness += ducking_score(bot[3].sprite, closest_ptero, action)
                bot[3].update(action)

            display_score(score, len(dino_bots))

            pygame.display.update()

            clock.tick(60)
        else:
            game_speed = 0
    num_gens += 1

def run(config_file):
    # loading NEAT config settings
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                         config_file)
    # Create the initial population (top-level obj for a run of NEAT)
    p = neat.Population(config)
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(eval_genomes, 50)
    node_names = {-1: 'near_obj_dist', -2: 'obs_height', -3: 'obs_width',
                   -4: 'bird_height', -5: 'obj_type', -6: 'game_speed', 
                   -7: 'dino_y', -8: 'bias', 0: 'big_jump', 
                   1: 'small_jump', 2: 'duck'}
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)   

    pygame.quit()

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)   