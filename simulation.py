import pygame
from time import sleep, time
from math import pi
import numpy as np
import neat


ship_image = pygame.transform.scale(pygame.image.load(
    "./PNG/spaceShips_001.png"), (50, 50))
red_bullet_image = pygame.transform.scale(pygame.image.load(
    "./PNG/spaceMissiles_015.png"), (8, 19))
blue_bullet_image = pygame.transform.scale(pygame.image.load(
    "./PNG/spaceMissiles_016.png"), (8, 19))
background_image = pygame.image.load("./PNG/background.png")

ships = []
bullets = []

MAX_STOCK = 3
RECHARGE_TIME = 1
BASE_HEALTH = 100
BULLET_DAMAGE = 5
DELTA_MULTIPLIER = 1


def center(ships, screen):
    if len(ships) == 2:
        x = ((ships[0].x + ships[1].x) / 2)-(screen.get_width() / 2)
        y = ((ships[0].y + ships[1].y) / 2)-(screen.get_height() / 2)
    else:
        x = ships[0].x + (screen.get_width() / 2)
        y = ships[0].y + (screen.get_height() / 2)

    return (x, y)


def distance(a, b):
    return np.sqrt((a.x - b.x)**2 + (a.y-b.y)**2)


class Ship:
    def __init__(self, x, y, color, genome, config):
        self.genome = genome
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)

        self.x = x
        self.y = y
        self.v = 0
        self.color = color
        self.health = BASE_HEALTH

        self.theta = 0
        self.omega = 0

        self.bullet_stock = MAX_STOCK
        self.time_to_recharge = 0

        self.enemy = None

    def set_enemy(self, enemy):
        self.enemy = enemy

    def die(self):
        pass

    def step(self, delta):
        inputs = (self.theta, self.enemy.theta,
                  self.enemy.x - self.x, self.enemy.y - self.y, )
        (fire_output, turn_left, turn_right, move_forward,
         move_backward) = self.net.activate(inputs)

        if fire_output > 0.5:
            self.fire()

        if turn_left > 0.5:
            self.omega = 90
        if turn_right > 0.5:
            self.omega = -90
        if move_forward > 0.5:
            self.v = 200
        if move_backward > 0.5:
            self.v = -200

        if self.time_to_recharge > 0:
            self.time_to_recharge -= delta

        if self.time_to_recharge <= 0 and self.bullet_stock < MAX_STOCK:
            self.time_to_recharge = RECHARGE_TIME
            self.bullet_stock += 1

        self.theta += self.omega * delta
        self.x = self.x + self.v * np.cos(self.theta * pi / 180) * delta
        self.y = self.y - self.v * np.sin(self.theta * pi / 180) * delta

    def fire(self):
        if self.bullet_stock > 0:
            bullets.append(
                Bullet(self.x, self.y, self.theta, self.color, self))
            self.bullet_stock -= 1
            self.time_to_recharge = RECHARGE_TIME

    def render(self, screen, center_x, center_y):
        theta = 90 + self.theta

        rotated_image = pygame.transform.rotate(ship_image, theta)
        screen.blit(rotated_image, (self.x - center_x - rotated_image.get_width() /
                                    2, self.y - center_y - rotated_image.get_height() / 2), )


class Bullet:
    def __init__(self, x, y, theta, color, owner, v=1000):
        self.x = x
        self.y = y
        self.theta = theta
        self.color = color
        self.owner = owner
        self.v = v
        self.damage = BULLET_DAMAGE
        self.lifespan = 2

    def step(self, delta):
        self.lifespan -= delta
        self.x = self.x + self.v * np.cos(self.theta * pi / 180) * delta
        self.y = self.y - self.v * np.sin(self.theta * pi / 180) * delta

    def render(self, screen, center_x, center_y):
        theta = self.theta - 90

        bullet_image = red_bullet_image if self.color == "red" else blue_bullet_image
        rotated_image = pygame.transform.rotate(bullet_image, theta)
        screen.blit(rotated_image, (self.x - center_x - rotated_image.get_width() /
                                    2, self.y - center_y - rotated_image.get_height() / 2), )


def simulation(genome1, genome2, config,  render=False):
    if render:
        pygame.init()
        pygame.display.set_caption("simulation")
        screen = pygame.display.set_mode((1080, 720))

    ship1 = Ship(np.random.randint(100, 980), np.random.randint(
        100, 620), "red", genome1, config)
    ship2 = Ship(np.random.randint(100, 980), np.random.randint(
        100, 620), "blue", genome2, config)

    ship1.set_enemy(ship2)
    ship2.set_enemy(ship1)
    ships = [ship1, ship2]

    running = True

    old_time = time()
    cumulative_time = 0

    while running:
        if render:
            delta = (time() - old_time) * DELTA_MULTIPLIER
            old_time = time()
        else:
            delta = 0.05

        cumulative_time += delta

        if cumulative_time >= 30:
            running = False

        for i, ship in enumerate(ships):
            for j, bullet in enumerate(bullets):
                if distance(bullet, ship) <= 30 and bullet.owner != ship:
                    bullet.owner.genome.fitness += 1
                    ship.genome.fitness -= 1
                    ship.health -= bullet.damage
                    if ship.health <= 0:
                        ship.die()
                        del ships[i]
                        running = False

                    del bullets[j]

        for ship in ships:
            ship.step(delta)

        for i, bullet in enumerate(bullets):
            bullet.step(delta)
            if bullet.lifespan <= 0:
                del bullets[i]

        if render:
            (center_x, center_y) = center(ships, screen)
            screen.blit(background_image, (0, 0))
            for ship in ships:
                ship.render(screen, center_x, center_y)

            for bullet in bullets:
                bullet.render(screen, center_x, center_y)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == 32:
                        ships[0].fire()
                    if event.key == 273:
                        ships[0].v = 200
                    elif event.key == 274:
                        ships[0].v = -200

                    if event.key == 276:
                        ships[0].omega = 90
                    elif event.key == 275:
                        ships[0].omega = -90

                if event.type == pygame.KEYUP:
                    if event.key == 273 or event.key == 274:
                        ships[0].v = 0

                    if event.key == 276 or event.key == 275:
                        ships[0].omega = 0

                elif event.type == pygame.QUIT:
                    running = False
