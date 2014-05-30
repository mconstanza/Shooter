__author__ = 'Mike'

import pygame
import random
import imp
import sys
import os
import math
import pyganim
import time
from pygame.locals import Color
from ShooterLevelOne import*

global game

screen_width, screen_height = 1000, 750
# Defining colors

black = [0, 0, 0]
blue = [15, 7, 166]
white = [255, 255, 255]
red = [89, 0 ,1]


def load_image(name):
    image = pygame.image.load(name).convert_alpha()
    return image


#----Player Class----
class Ship(pygame.sprite.Sprite):
    '''
    Sprite for the player's ship.
    '''

    def __init__(self, xy):
        super(Ship, self).__init__()
        self.images = []
        # indexes: 0 = still, 1 = forward, 2 = left, 3 = left/forward, 4 = right, 5 = right/forward
        self.images.append(load_image('playership.png'))
        self.images.append(load_image('playershipforward.png'))
        self.images.append(load_image('playershipleft.png'))
        self.images.append(load_image('playershipleftforward.png'))
        self.images.append(load_image('playershipright.png'))
        self.images.append(load_image('playershiprightforward.png'))

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.shiphit = pygame.mixer.Sound('boom7.wav')

        # set position
        self.rect.centerx, self.rect.centery = xy

        # ship movement speed
        self.movementspeed = 7

        # health
        self.health = 100

        # current ship velocity
        self.xvelocity = 0
        self.yvelocity = 0

        # beam type
        self.beam = "default"

        # current state, alive, dead, or invulnerable
        self.state = "alive"

        # sounds
        self.lasersound = pygame.mixer.Sound('laser1.wav')

        # last time collided with ememy
        self.lastcollision = 0

# movement
    def left(self):
        '''Increases velocity'''
        if self.xvelocity > -5:
            self.xvelocity -= self.movementspeed
        self.index = 2
        self.image = self.images[self.index]

    def leftkeyup(self):
        '''Decreases velocity'''
        if self.xvelocity < 5:
            self.xvelocity += self.movementspeed
        self.index = 0
        self.image = self.images[self.index]

    def right(self):
        '''Decreases velocity'''
        if self.xvelocity < 5:
            self.xvelocity += self.movementspeed
        self.index = 4
        self.image = self.images[self.index]

    def rightkeyup(self):
        '''Increases velocity'''
        if self.xvelocity > -5:
            self.xvelocity -= self.movementspeed
        self.index = 0
        self.image = self.images[self.index]

    def up(self):
        '''Increases velocity'''

        self.yvelocity -= self.movementspeed
        self.index = 1
        self.image = self.images[self.index]

    def down(self):
        '''Decreases velocity'''
        self.yvelocity += self.movementspeed
        self.index = 0
        self.image = self.images[self.index]

    def downkeyup(self):
        self.yvelocity += self.movementspeed
        self.index = 0
        self.image = self.images[self.index]

    def zero_xvelocity(self):
        '''not moving horizontally'''
        self.xvelocity = 0
        self.index = 0
        self.image = self.images[self.index]

    def zero_yvelocity(self):
        '''not moving vertically'''
        self.yvelocity = 0
        self.index = 0
        self.image = self.images[self.index]

    def upleft(self):
        '''moving up and left'''
        self.index = 3
        self.image = self.images[self.index]

    def upright(self):
        '''moving up and right'''
        self.index = 5
        self.image = self.images[self.index]

    def move(self, xvelocity, yvelocity):
        '''Move the ship without going past sides'''
        if xvelocity != 0 or yvelocity != 0:
            if self.rect.right + xvelocity > 975:
                self.rect.right = 975
            elif self.rect.left + xvelocity < 25:
                self.rect.left = 25
            elif self.rect.top + yvelocity < 0:
                self.rect.top = 0
            elif self.rect.bottom + yvelocity > 800:
                self.rect.bottom = 800
            else:
                self.rect.x += xvelocity
                self.rect.y += yvelocity


    # Collision Check
    def shotCollision(self, playerspritegroup, enemyshots, healthbar):
        for self in pygame.sprite.groupcollide(playerspritegroup, enemyshots, False, False):
            for shot in pygame.sprite.groupcollide(enemyshots, playerspritegroup, True, False):
                healthbar.decrease_health(shot.damage, self)
                self.shiphit.play()

    def enemyCollision(self, playerspritegroup, enemies, healthbar, ticks):

        for self in pygame.sprite.groupcollide(playerspritegroup, enemies, False, False):
            if ticks - self.lastcollision > 500:
                self.lastcollision = ticks
                healthbar.decrease_health(20, self)
                self.shiphit.play()
            else:
                pass

    def powerupCollision(self, healthbar, playerspritegroup, powerupgroup):
        for self in pygame.sprite.groupcollide(playerspritegroup, powerupgroup, False, False):
            for powerup in pygame.sprite.groupcollide(powerupgroup, playerspritegroup, True, False):
                if powerup.type == 'tribeam':
                    self.beam = powerup.type
                elif powerup.type == 'health':
                    healthbar.increase_health(self, powerup.amount)

    def asteroidCollision(self, playerspritegroup, asteroidgroup, healthbar, ticks):
        for self in pygame.sprite.groupcollide(playerspritegroup, asteroidgroup, False, False):
           for asteroid in pygame.sprite.groupcollide(asteroidgroup, playerspritegroup, False, False):
                if ticks - self.lastcollision > 500:
                    self.lastcollision = ticks
                    healthbar.decrease_health(asteroid.damage, self)
                    self.shiphit.play()
                else:
                    pass

    def collision(self, ticks, playerspritegroup, enemies, enemyshots, healthbar, powerupgroup, asteroidgroup):
        self.asteroidCollision(playerspritegroup, asteroidgroup, healthbar, ticks)
        self.powerupCollision(healthbar, playerspritegroup, powerupgroup)
        self.enemyCollision(playerspritegroup, enemies, healthbar, ticks)
        self.shotCollision(playerspritegroup, enemyshots, healthbar)


# Update
    def update(self, sprites, enemies, enemyshots, healthbar, powerupgroup, asteroidgroup, ticks):
        self.move(self.xvelocity, self.yvelocity)
        if self.state == "alive":
            self.collision(ticks, sprites, enemies, enemyshots, healthbar, powerupgroup, asteroidgroup)
        else:
            pass
        if self.health > 100:
            self.health = 100

    def reset(self, xy):
        self.rect.centerx, self.rect.centery = xy

    def firecurrentshot(self, shotsgroup, ticks):
        if self.beam == "default":
            self.shot = Shot((self.rect.right - 18.5, self.rect.top), -10, ticks)
            shotsgroup.add(self.shot)
            self.lasersound.play()
        elif self.beam == "tribeam":
            self.shot = TriBeam(shotsgroup, self, ticks)
            self.lasersound.play()

    def invulnerability(self, time):
        self.state = "invulnerable"

    def explode(self, screen, xy):
        self.explosion.blit(screen, xy)

# ----Bars----
class HealthBar(object):
    def __init__(self, screen, ship, location):
        screen = screen
        self.image = pygame.image.load('healthbar.png').convert()
        self.location = location
        self.healthrect = pygame.draw.rect(screen, blue,(self.location[0], self.location[1], 200, 50), 0)
        self.rect = self.image.get_rect()

        # boundaries for bar fill
        self.topleft = (360, 710)
        self.topright = (640, 710)
        self.bottomleft = (360, 740)
        self.bottomright = (640, 740)
        self.height = abs(self.topleft[1] - self.bottomleft[1])
        self.width = abs(self.topleft[0] - self.topright[0])
        self.color = blue

        # health
        self.maxhealth = self.width
        self.health = ship.health

    def increase_health(self, ship, amount):
        ship.health += amount
        self.health += amount
        if self.health * 2.8 > self.maxhealth:
            self.health = self.maxhealth / 2.8
        if ship.health * 2.8 > self.maxhealth:
            ship.health = self.maxhealth / 2.8

    def decrease_health(self, amount, ship):
        self.health -= amount
        ship.health -= amount
        if self.health < 0:
            self.health = 0
            ship.health = 0

    def is_dead(self):
        return self.health == 0

    def display(self, screen):
       # load bar background
        screen.blit(self.image, (self.location[0], self.location[1]))
    # build bar rectangle
        self.bar = pygame.Rect(self.topleft[0],\
                               self.topleft[1],\
                                self.health * 2.8,\
                                self.height)
    # draw bar rectangle
        pygame.draw.rect(screen, self.color, self.bar, 0)

class KillBar(object):
    def __init__(self, screen, location):

        self.image = pygame.image.load('healthbar.png').convert()
        self.location = location
        self.killrect = pygame.draw.rect(screen, blue,(self.location[0], self.location[1], 200, 50), 0)
        self.rect = self.image.get_rect()

        # boundaries for bar fill
        self.topleft = (360, 10)
        self.topright = (640, 10)
        self.bottomleft = (360, 50)
        self.bottomright = (640, 50)
        self.height = abs(self.topleft[1] - self.bottomleft[1])
        self.width = abs(self.topleft[0] - self.topright[0])
        self.color = red

        # kills
        self.minkill = 0
        self.maxkill = self.width
        self.enemieskilled = 0

    def increase_kill_bar(self, enemieskilled):

        self.enemieskilled = enemieskilled
        if self.enemieskilled * 2.8 > self.maxkill:
            self.enemieskilled = self.maxkill / 2.8

    def decrease_kill_bar(self, amount):
        self.enemieskilled -= amount
        if self.enemieskilled < 0:
            self.enemieskilled = 0

    def display(self, screen):
       # load bar background
        screen.blit(self.image, (self.location[0], self.location[1]))
    # build bar rectangle
        self.bar = pygame.Rect(self.topleft[0],\
                               self.topleft[1],\
                               ((self.enemieskilled * 280) / 100),\
                                30)
    # draw bar rectangle
        pygame.draw.rect(screen, self.color, self.bar, 0)

class BossBar(HealthBar):

    def __init__(self, screen, location, bosshealth):

        self.image = pygame.image.load('healthbar.png').convert()
        self.location = location
        self.barrect = pygame.draw.rect(screen, red,(self.location[0], self.location[1], 200, 50), 0)
        self.rect = self.image.get_rect()

        # boundaries for bar fill
        self.topleft = (360, 10)
        self.topright = (640, 10)
        self.bottomleft = (360, 50)
        self.bottomright = (640, 50)
        self.height = abs(self.topleft[1] - self.bottomleft[1])
        self.width = abs(self.topleft[0] - self.topright[0])
        self.color = red
        self.health = bosshealth

    def increase_health(self, amount):
        self.health += amount
        if self.health > self.maxhealth:
            self.health = self.maxhealth

    def decrease_health(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def convert_health(self, bosshealth, maxbosshealth):
        '''
        convert boss health to a percentage of 280, the pixel-width of the bossbar
        '''
        if bosshealth <= 0:
            return 0
        else:
            return (bosshealth * 280)/maxbosshealth

    def is_dead(self):
        return self.health == 0

    def display(self, screen, bosshealth, maxbosshealth):
       # load bar background
        screen.blit(self.image, (self.location[0], self.location[1]))
    # build bar rectangle
        self.bar = pygame.Rect(self.topleft[0],\
                               self.topleft[1] + 10,\
                               self.convert_health(bosshealth, maxbosshealth),\
                                30)
    # draw bar rectangle
        pygame.draw.rect(screen, self.color, self.bar, 0)

class LivesBar(object):
    def __init__(self, ship):
        self.image = pygame.image.load('ship.png').convert_alpha()
        self.rect = self.image.get_rect()

#----Shots----
class Shot(pygame.sprite.Sprite):
    '''
    Sprite for rays the ship shoots.
    '''
    maxlifetime = 3000 # seconds
    damage = 5

    def __init__(self, xy, movementspeed, ticks):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('beamblue.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.maxspeed = 10
        self.yvelocity = 0
        self.lifetime = ticks # seconds
        self.maxlifetime = 3000 # milliseconds

         # set position
        self.rect.centerx, self.rect.centery = xy

        # shot movement speed
        self.movementspeed = movementspeed
        self.yvelocity += self.movementspeed


    def move(self, yvelocity):
        '''
        Make the shot move up the y axis automatically.
        '''
        self.rect.y += self.yvelocity

    def update(self, ticks):
        '''
        Called to update the sprite. Do this every frame. Handles
        moving the sprite by its velocity.
        '''
        #---kill if too old---

        if ticks - self.lifetime > self.maxlifetime:
            self.kill()

        else:
            self.lifetime = ticks

        # kill if off screen
        if self.rect.bottom < 0:
            self.kill()

        #---movement---
        self.move(self.yvelocity)

class TriBeam(object):

    def __init__(self, shotsgroup, ship, ticks):
        self.yvelocity = -7
        self.leftshot = Shot((ship.rect.centerx, ship.rect.top),-7, ticks )
        shotsgroup.add(self.leftshot)
        self.rightshot = Shot((ship.rect.left - 10, ship.rect.top), -7, ticks)
        shotsgroup.add(self.rightshot)
        self.centershot = Shot((ship.rect.right + 10, ship.rect.top), -7, ticks)
        shotsgroup.add(self.centershot)

class BasicEnemyShot(Shot):
    def __init__(self, xy, movementspeed, ticks):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('beamred.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.maxspeed = 10
        self.yvelocity = 0
        self.lifetime = ticks # seconds

         # set position
        self.rect.centerx, self.rect.centery = xy

        # shot movement speed
        self.movementspeed = movementspeed
        self.yvelocity += self.movementspeed

    def update(self, ticks):
        '''
        Called to update the sprite. Do this every frame. Handles
         moving the sprite by its velocity.
        '''

        #---kill if too old---

        if ticks - self.lifetime > Shot.maxlifetime:
            self.kill()

        else:
            self.lifetime = ticks

        # kill if off screen
        if self.rect.bottom > screen_height or self.rect.top < 0:
            self.kill()

        #---movement---
        self.move(self.yvelocity)

class Hadouken(BasicEnemyShot):

    damage = 25

    def __init__(self, xy, movementspeed, ticks):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('hadouken.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.maxspeed = 15
        self.yvelocity = 0
        self.lifetime = ticks # seconds
        self.maxlifetime = 3000
         # set position
        self.rect.centerx, self.rect.centery = xy

        # shot movement speed
        self.movementspeed = movementspeed
        self.yvelocity += self.movementspeed

        def update(self, ticks):
            '''
            Called to update the sprite. Do this every frame. Handles
            moving the sprite by its velocity.
            '''
        #---kill if too old---

            if ticks - self.lifetime > Shot.maxlifetime:
                self.kill()

            else:
                self.lifetime = ticks

            # kill if off screen
            if self.rect.top > screen_height:
                self.kill()

        #---movement---
            self.move(self.yvelocity)


#----Powerups----
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    def update(self):
        raise NotImplementedError
    def move(self):
        raise NotImplementedError

class TriBeamPowerup(PowerUp):
    def __init__(self, ticks):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('TriBeamPowerUp.png').convert_alpha()
        self.rect = self.image.get_rect()

        # type
        self.type = "tribeam"
        # speed and velocity
        self.yvelocity = 5

        # lifetime
        self.maxlifetime = 3000 # milliseconds
        self.lifetime = ticks # milliseconds

        # set position
        self.rect.centerx, self.rect.centery = random.randrange(100, 700, 50), 100

    def move(self, yvelocity):
        self.rect.centery += yvelocity

    def update(self, ticks):
        # kill if too old
        if ticks - self.lifetime > self.maxlifetime:
            self.kill()

        self.move(self.yvelocity)

class HealthPowerup(PowerUp):
    def __init__(self, ticks):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('HealthPowerup.png').convert_alpha()
        self.rect = self.image.get_rect()

        # type
        self.type = "health"

        # amount
        self.amount = 20

        # speed and velocity
        self.yvelocity = 5

        # lifetime
        self.maxlifetime = 3000 # milliseconds
        self.lifetime = ticks # milliseconds

        # set position
        self.rect.centerx, self.rect.centery = random.randrange(100, 700, 50), 100

    def move(self, yvelocity):
        self.rect.centery += yvelocity

    def update(self, ticks):
        # kill if too old
        if ticks - self.lifetime > self.maxlifetime:
            self.kill()

        self.move(self.yvelocity)


#----Asteroids and other Flotsam----

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, yvelocity):
        '''
        Asteroid type is a random integer 1-24 that chooses which asteroid is summoned
        '''
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('asteroid1.png').convert_alpha()
        self.rect = self.image.get_rect()

        # set position
        self.rect.centerx = random.randrange(0 + 100, screen_width - 100, 50)
        self.rect.centery = random.randrange(-50, 100, 10)

        # velocity
        self.yvelocity = yvelocity

        # damage
        self.damage = 20

    def render(self):
        pass

    def update(self, asteroidgroup, shotsgroup):
        self.move(self.yvelocity)
        if self.rect.top > screen_height:
            self.kill()
        for asteroid in pygame.sprite.groupcollide(asteroidgroup, shotsgroup, False, True):
            pass

    def move(self, yvelocity):
        self.rect.y += yvelocity


#----Enemies----
class EnemyShip(pygame.sprite.Sprite):
    '''
    Class to create basic enemy ships.
    '''

    def __init__(self, spawnpoint):
        '''
        spawnpoint is a random number between 1 and 3
        that determines the starting point and path
        of the enemy.
        '''
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('basicenemyship.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.spawnpoint = spawnpoint

        self.explosionsound = pygame.mixer.Sound('boom9.wav')

        # set position
        if self.spawnpoint == 1:
            self.rect.left, self.rect.top = (random.randrange(-10, 250, 10), random.randrange\
                                                                            (-10, 0, 1))
        elif self.spawnpoint == 2:
            self.rect.left, self.rect.top = (random.randrange(260, 600, 10), random.randrange\
                                                                                  (-10, 0, 1))
        elif self.spawnpoint == 3:
            self.rect.left, self.rect.top = (random.randrange(650, 760, 10), random.randrange\
                                                                            (-10, 0, 1))

        # ship movement speed
        self.movementspeed = 4

        # current ship velocity
        self.xvelocity = 0
        self.yvelocity = 0
        if self.spawnpoint == 2:
            self.xvelocity = random.choice([-5, 5])

        # counter for horizontal movement
        self.xvelocitycounter = 0

        # variable for when the enemy last fired a shot
        self.lastshot = 0

    def move(self):
        # spawn point based movement patterns

        if self.spawnpoint == 1:
            self.xvelocity = random.randrange(1, 5, 1)
        elif self.spawnpoint == 2:
            if self.xvelocity == -5:
                self.xvelocitycounter -= 1
                if self.xvelocitycounter == -50:
                    self.xvelocity = 5
            elif self.xvelocity == 5:
                self.xvelocitycounter += 1
                if self.xvelocitycounter == 50:
                    self.xvelocity = -5
        elif self.spawnpoint == 3:
            self.xvelocity = random.randrange(-5, 2, 1)

        self.yvelocity = random.randrange(2, 5, 1)
        self.rect.x += self.xvelocity
        self.rect.y += self.yvelocity

    def explode(self, screen, xy, ticks):
        explosion = Explosion(xy, ticks, 700)
        return explosion


    def update(self, xy, screen, enemies, shots, ticks, enemyshots, enemieskilled, killbar, explosiongroup):

        #---explode if hit by shot---
        for self in pygame.sprite.groupcollide(enemies, shots, False, True):
            explosion = self.explode(screen, self.rect.topleft, ticks)
            explosiongroup.add(explosion)
            self.explosionsound.play()
            self.kill()
            killbar.enemieskilled += 1
            killbar.increase_kill_bar(killbar.enemieskilled)

        self.offscreen()
        self.move()
        self.enemyshoot(ticks, enemyshots)

    def offscreen(self):
        if self.rect.x < 0 or self.rect.x > screen_width:
            self.kill()
        elif self.rect.y > screen_height:
            self.kill()

    def enemyshoot(self, ticks, enemyshots):
        if ticks - self.lastshot > 800:
            self.lastshot = ticks
            self.enemyshot = BasicEnemyShot((self.rect.centerx, self.rect.bottom), 7, ticks)
            enemyshots.add(self.enemyshot)

class EnemySpawner(object):
    '''
    Using this class to spawn enemies with a copy of the sprites
    already loaded.
    '''
    def __init__(self):
        # load all of the enemy images
        self.images = {
            1: pygame.image.load('basicenemyship.png')
        }

    def getEnemyShip(self, xy):
        return EnemyShip(xy)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, xy, ticks, lifetime):
        super(Explosion, self).__init__()
        self.images = []
        self.images.append(load_image('explosion1.png'))
        self.images.append(load_image('explosion2.png'))
        self.images.append(load_image('explosion3.png'))
        self.images.append(load_image('explosion4.png'))
        self.images.append(load_image('explosion5.png'))
        self.images.append(load_image('explosion6.png'))
        self.images.append(load_image('explosion7.png'))

        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.topleft = xy

        self.maxlifetime = lifetime # milliseconds
        self.lifetime = ticks

        self.frameticks = ticks # this is to keep track of how long each frame of the animation lasts


    def update(self, ticks):
        '''
        This method iterates through the elements inside self.images and
        displays the next one each tick. For a slower animation, you may want to
        consider using a timer of some sort so it updates slower.
        '''

        if ticks - self.frameticks >= 100:  # each frame of animation should take 100 milliseconds
            self.index += 1
            self.frameticks = ticks

        if self.index >= len(self.images):
            self.index = 0

        self.image = self.images[self.index]

        #---kill if too old---
        if ticks - self.lifetime >= self.maxlifetime:
            self.kill()



#----Scenes----
class SceneManager(object):
    '''
    Manages loading all the data unique to each level
    '''
    def __init__(self, screen):
        self.go_to(StartScreen(0, screen))

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self

class Scene(object):

    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self, screen):
        raise NotImplementedError

    def handle_events(self):
        raise NotImplementedError

class Level(Scene):
    '''
    Define a 'bosstrigger' stating how many enemies must be killed
    before the boss appears.
    '''
    def __init__(self, lives):
        self.lives = lives

    def render(self, screen):
        raise NotImplementedError

    def update(self, screen):
        raise NotImplementedError

    def handle_events(self):
        raise NotImplementedError

    def boss_check(self, bosstrigger, enemieskilled, screen):

        if enemieskilled >= bosstrigger:
            return True
        else:
            return False

    def powerup_roll(self, percentchance):
        raise NotImplementedError
    def spawn_powerup(self):
        raise NotImplementedError

    def spawn_enemies(self, enemieslist, maxenemies, ticks, lastEnemySpawned, spawntime):
        raise NotImplementedError

class BossMode(Scene):
    def __init__(self, screen):
        pass

    def boss_beaten(self, bosshealth, bossmaxhealth):
        if bosshealth - bossmaxhealth <= -(bossmaxhealth):
            return True
        else:
            return False

    def boss_time(self):
        raise NotImplementedError

class StartScreen(Scene):
    '''
    The Title screen for the game
    '''
    def __init__(self, level, screen):

        level = level

        # Start Screen Music
        pygame.mixer.pre_init(44100, -16, 2, 2048)

        self.music = pygame.mixer.music.load('02 Chemical Reaction.mp3')
        pygame.mixer.music.play()


        start = False

    def render(self, screen):
        # Create Title text
        self.startScreenFont = pygame.font.Font('freesansbold.ttf', 44)
        self.startScreenSurf = self.startScreenFont.render('GENERIC SHOOTER', True, white)
        self.degrees1 = 0

    # Create 'Press Space to Play' text

        self.presstoPlayFont = pygame.font.Font('freesansbold.ttf', 20)
        self.presstoPlaySurf = self.presstoPlayFont.render('Press Space to Play!', True, white)

        # Render surfaces
        screen.fill(black)
        self.startScreenSurf = pygame.transform.rotate(self.startScreenSurf, self.degrees1)
        placement_rect1 = self.startScreenSurf.get_rect()
        placement_rect1.center = (screen_width / 2, screen_height / 2)

        self.placement_presstoPlay = pygame.transform.rotate(self.presstoPlaySurf, self.degrees1)
        placement_presstoPlayRect = self.placement_presstoPlay.get_rect()
        placement_presstoPlayRect.center = (screen_width / 2, (screen_height / 2) + (screen_height / 4))

        # Draw them to the screen
        screen.blit(self.placement_presstoPlay, placement_presstoPlayRect)
        screen.blit(self.startScreenSurf, placement_rect1)


    def handle_events(self, events):

        # poll for events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()

        # handle user input
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

                elif event.key == pygame.K_SPACE:
                    pygame.mixer.music.stop()
                    self.manager.go_to(LevelOne(1, screen, 3))


    def update(self, screen):
        pass

class WinScreen(Scene):
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)

        self.music = pygame.mixer.music.load('02 Chemical Reaction.mp3')
        pygame.mixer.music.play()

    def render(self, screen):
        # Create Title text
        self.winScreenFont = pygame.font.Font('freesansbold.ttf', 44)
        self.winScreenSurf = self.winScreenFont.render('You Win!', True, white)
        self.degrees1 = 0


        # Render surfaces
        screen.fill(black)
        self.winScreenSurf = pygame.transform.rotate(self.winScreenSurf, self.degrees1)
        placement_rect1 = self.winScreenSurf.get_rect()
        placement_rect1.center = (screen_width / 2, screen_height / 2)


        # Draw them to the screen
        screen.blit(self.winScreenSurf, placement_rect1)

    def update(self, screen):
        pass

    def handle_events(self, events):

        # poll for events
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()

        # handle user input
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

class GameOver(Scene):
     def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)

        self.music = pygame.mixer.music.load('02 Chemical Reaction.mp3')
        pygame.mixer.music.play()

     def render(self, screen):

        # Create 'Game Over' text
        self.gameOverFont = pygame.font.Font('freesansbold.ttf', 36)
        self.gameOverSurf1 = self.gameOverFont.render('Game Over!', True, white)
        self.degrees1 = 0

        # Create 'Play Again' text

        self.playagainfont = pygame.font.Font('freesansbold.ttf', 20)
        self.playagainsurf = self.playagainfont.render('Play Again? Y/N', True, white)

        # Render surfaces
        screen.fill(black)
        self.placement_gameOversurf1 = pygame.transform.rotate(self.gameOverSurf1, self.degrees1)
        placement_rect1 = self.placement_gameOversurf1.get_rect()
        placement_rect1.center = (screen_width / 2, screen_height / 2)

        self.placement_playagain = pygame.transform.rotate(self.playagainsurf, self.degrees1)
        placement_playagainrect = self.placement_playagain.get_rect()
        placement_playagainrect.center = (screen_width / 2, (screen_height / 2) + (screen_height / 4))

        # Draw them to the screen
        screen.blit(self.placement_gameOversurf1, placement_rect1)
        screen.blit(self.placement_playagain, placement_playagainrect)
        pygame.display.update()

     def update(self, screen):
        pass

     def handle_events(self, events):

         # poll for events
         for event in events:
             if event.type == pygame.QUIT:
                 pygame.quit()

         # handle user input
             elif event.type == pygame.KEYDOWN:

                 if event.key == pygame.K_ESCAPE:
                     pygame.quit()

#----Main Loop----
class Game(object):
    '''Handles initialization of PyGame and sets up game'''

    def __init__(self):
        '''Called during initialization'''

        # load and set up pygame
        pygame.init()

        # initialize sound
        pygame.mixer.pre_init(44100, -16, 2, 2048)

        self.lives = 3

    def spawnBasicEnemy(self):
        self.enemyship = self.enemyspawner.getEnemyShip(random.randrange(1, 4, 1))
        self.enemies.add(self.enemyship)

    def run(self):
        '''Runs the game. Contains the game loop.'''

        global screen, screen_width, screen_height, manager, lives

        pygame.init()

        # initialize sound
        pygame.mixer.pre_init(44100, -16, 2, 2048)

        #create window
        screen = pygame.display.set_mode((1000, 750))
        screen_width, screen_height = 1000, 750

        manager = SceneManager(screen)

        # initialize clock
        timer = pygame.time.Clock()

        # gameover variable
        gameover = False


        running = True

        # run until something tells us to stop

        while running:

            #tick pygame clock
            #limit fps
            timer.tick(60)

            # if game is not over
            if gameover == False:

                #handle pygame events

                # update title bar with fps
                pygame.display.set_caption('Shooter  %d fps' % timer.get_fps())

                # main loop
                manager.scene.handle_events(pygame.event.get())
                manager.scene.update(screen)
                manager.scene.render(screen)
                pygame.display.flip()

            else:
                self.gameOver()

        print 'Quitting. Thanks for playing.'

    def handleEvents(self):
        '''Poll PyGame for events and handle accordingly'''

        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # handle user input
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        return True

    def gameOver(self):

        # change the gameover variable so the main loop stops
        self.gameover = True

        # stop the music
        pygame.mixer.music.stop()

        # Create 'Game Over' text
        self.gameOverFont = pygame.font.Font('freesansbold.ttf', 36)
        self.gameOverSurf1 = self.gameOverFont.render('Game Over!', True, white)
        self.degrees1 = 0

        # Create 'Play Again' text

        self.playagainfont = pygame.font.Font('freesansbold.ttf', 20)
        self.playagainsurf = self.playagainfont.render('Play Again? Y/N', True, white)

        # Render surfaces
        self.window.fill(black)
        self.placement_gameOversurf1 = pygame.transform.rotate(self.gameOverSurf1, self.degrees1)
        placement_rect1 = self.placement_gameOversurf1.get_rect()
        placement_rect1.center = (screen_width / 2, screen_height / 2)

        self.placement_playagain = pygame.transform.rotate(self.playagainsurf, self.degrees1)
        placement_playagainrect = self.placement_playagain.get_rect()
        placement_playagainrect.center = (screen_width / 2, (screen_height / 2) + (screen_height / 4))

        # Draw them to the screen
        self.window.blit(self.placement_gameOversurf1, placement_rect1)
        self.window.blit(self.placement_playagain, placement_playagainrect)
        pygame.display.update()


         # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            # handle user input
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

                if event.key == pygame.K_y:
                    self.run()

                elif event.key == pygame.K_n:
                    pygame.quit()

# Run the game

if __name__ == '__main__':
    game = Game()
    game.run()