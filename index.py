import pygame
from time import sleep, time, time_ns
from math import atan2, pi, cos, sin, sqrt

ship_image = pygame.transform.scale(pygame.image.load(
    "./PNG/Sprites/Ships/spaceShips_001.png"), (50, 50))
red_bullet_image = pygame.transform.scale(pygame.image.load(
    "./PNG/Sprites/Missiles/spaceMissiles_015.png"), (8, 19))
blue_bullet_image = pygame.transform.scale(pygame.image.load(
    "./PNG/Sprites/Missiles/spaceMissiles_016.png"), (8, 19))
background_image = pygame.image.load("./PNG/Sprites/background.png")

ships = []
bullets = []

MAX_STOCK = 3
RECHARGE_TIME = 1
RENDER = True
BASE_HEALTH = 100
BULLET_DAMAGE = 35


def distance(a, b):
    return sqrt((a.x - b.x)**2 + (a.y-b.y)**2)


class Ship:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.v = 0
        self.color = color
        self.health = BASE_HEALTH

        self.theta = 0
        self.omega = 0

        self.bullet_stock = MAX_STOCK
        self.time_to_recharge = 0

    def die(self):
        print("Dead")

    def step(self, delta):
        if self.time_to_recharge > 0:
            self.time_to_recharge -= delta

        if self.time_to_recharge <= 0 and self.bullet_stock < MAX_STOCK:
            self.time_to_recharge = RECHARGE_TIME
            self.bullet_stock += 1

        self.theta += self.omega * delta
        self.x = self.x + self.v * cos(self.theta * pi / 180) * delta
        self.y = self.y - self.v * sin(self.theta * pi / 180) * delta

    def fire(self):
        if self.bullet_stock > 0:
            bullets.append(
                Bullet(self.x, self.y, self.theta, self.color, self))
            self.bullet_stock -= 1
            self.time_to_recharge = RECHARGE_TIME

    def render(self, screen):
        theta = 90 + self.theta

        rotated_image = pygame.transform.rotate(ship_image, theta)
        screen.blit(rotated_image, (self.x - rotated_image.get_width() /
                                    2, self.y - rotated_image.get_height() / 2), )


class Bullet:
    def __init__(self, x, y, theta, color, owner, v=1000):
        self.x = x
        self.y = y
        self.theta = theta
        self.color = color
        self.owner = owner
        self.v = v
        self.damage = BULLET_DAMAGE

    def step(self, delta):
        self.x = self.x + self.v * cos(self.theta * pi / 180) * delta
        self.y = self.y - self.v * sin(self.theta * pi / 180) * delta

    def render(self, screen):
        theta = self.theta - 90

        bullet_image = red_bullet_image if self.color == "red" else blue_bullet_image
        rotated_image = pygame.transform.rotate(bullet_image, theta)
        screen.blit(rotated_image, (self.x - rotated_image.get_width() /
                                    2, self.y - rotated_image.get_height() / 2), )


def main():
    if RENDER:
        pygame.init()
        pygame.display.set_caption("simulation")
        screen = pygame.display.set_mode((540, 360))

    ships.append(Ship(270, 180, "red"))
    ships.append(Ship(100, 100, "blue"))

    running = True

    old_time = time()

    while running:
        if RENDER:
            delta = (time() - old_time)
            old_time = time()
        else:
            delta = 0.01

        for i, ship in enumerate(ships):
            for j, bullet in enumerate(bullets):
                if distance(bullet, ship) < 30 and bullet.owner != ship:
                    ship.health -= bullet.damage
                    if ship.health <= 0:
                        ship.die()
                        del ships[i]

                    del bullets[j]

        for ship in ships:
            ship.step(delta)

        for bullet in bullets:
            bullet.step(delta)

        if RENDER:
            screen.blit(background_image, (0, 0))
            for ship in ships:
                ship.render(screen)

            for bullet in bullets:
                bullet.render(screen)

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


if __name__ == "__main__":
    main()
