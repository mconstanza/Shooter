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


screen_width, screen_height = 1000, 750
# Defining colors

black = [0, 0, 0]
blue = [15, 7, 166]
white = [255, 255, 255]
red = [89, 0 ,1]
explosion =  pyganim.PygAnimation([('explosion1.png', .1),
                                           ('explosion2.png', .1),
                                            ('explosion3.png', .1),
                                            ('explosion4.png', .1),
                                            ('explosion5.png', .1),
                                            ('explosion6.png', .1),
                                            ('explosion7.png', .1)])

class Ship(pygame.sprite.Sprite):
    '''
    Sprite for the player's ship.
    '''

    lives = 3

    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('playership.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.shiphit = pygame.mixer.Sound('boom7.wav')

        # set position
        self.rect.centerx, self.rect.centery = xy

        # ship movement speed
        self.movementspeed = 7

        # current ship velocity
        self.xvelocity = 0
        self.yvelocity = 0

        # current state, alive or dead
        self.state = "alive"

        # last time collided with ememy
        self.lastcollision = 0

    def left(self):
        '''Increases velocity'''
        if self.xvelocity > -5:
            self.xvelocity -= self.movementspeed


    def right(self):
        '''Decreases velocity'''
        self.xvelocity += self.movementspeed

    def up(self):
        '''Increases velocity'''
        self.yvelocity -= self.movementspeed

    def down(self):
        '''Decreases velocity'''
        self.yvelocity += self.movementspeed


    def move(self, xvelocity, yvelocity):
        '''Move the ship without going past sides'''
        if xvelocity != 0 or yvelocity != 0:
            if self.rect.right + xvelocity > 950:
                self.rect.right = 950
            elif self.rect.left + xvelocity < -50:
                self.rect.left = -50
            elif self.rect.top + yvelocity < 0:
                self.rect.top = 0
            elif self.rect.bottom + yvelocity > 800:
                self.rect.bottom = 800
            else:
                self.rect.x += xvelocity
                self.rect.y += yvelocity

    def shotCollision(self, playerspritegroup, enemyshots, healthbar):
        for self in pygame.sprite.groupcollide(playerspritegroup, enemyshots, False, False):
            for shot in pygame.sprite.groupcollide(enemyshots, playerspritegroup, True, False):
                healthbar.decrease_health(shot.damage)
                self.shiphit.play()

    def enemyCollision(self, playerspritegroup, enemies, healthbar, ticks):

        for self in pygame.sprite.groupcollide(playerspritegroup, enemies, False, False):
            if ticks - self.lastcollision > 500:
                self.lastcollision = ticks
                healthbar.decrease_health(20)
                self.shiphit.play()
            else:
                pass

    def update(self, sprites, enemies, enemyshots, healthbar, ticks):
        self.move(self.xvelocity, self.yvelocity)
        self.shotCollision(sprites, enemyshots, healthbar)
        self.enemyCollision(sprites, enemies, healthbar, ticks)

    def reset(self, xy):
        self.rect.centerx, self.rect.centery = xy

class HealthBar(object):
    def __init__(self, screen, location):
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
        self.health = self.width

    def increase_health(self, amount):
        self.health += amount
        if self.health > self.maxhealth:
            self.health = self.maxhealth

    def decrease_health(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def is_dead(self):
        return self.health == 0

    def display(self, screen):
       # load bar background
        screen.blit(self.image, (self.location[0], self.location[1]))
    # build bar rectangle
        self.bar = pygame.Rect(self.topleft[0],\
                               self.topleft[1],\
                                self.health,\
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
        print "enemieskilled + amount " + str(self.enemieskilled)
        if self.enemieskilled * 2.8 > self.maxkill:
            self.enemieskilled = self.maxkill / 2.8

    def decrease_kill_bar(self, amount):
        self.enemieskilled -= amount
        if self.enemieskilled < 0:
            self.enemieskilled = 0

    def convert_enemies_killed(self, enemieskilled):
        return float(enemieskilled * 2.8)

    def display(self, screen):
       # load bar background
        screen.blit(self.image, (self.location[0], self.location[1]))
    # build bar rectangle
        self.bar = pygame.Rect(self.topleft[0],\
                               self.topleft[1],\
                                self.enemieskilled * 2.8,\
                                30)
    # draw bar rectangle
        pygame.draw.rect(screen, self.color, self.bar, 0)

class Shot(pygame.sprite.Sprite):
    '''
    Sprite for rays the ship shoots.
    '''
    maxlifetime = 5 # seconds
    damage = 5

    def __init__(self, xy, movementspeed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('beamblue.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.maxspeed = 10
        self.yvelocity = 0
        self.lifetime = 0.0 # seconds

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

    def update(self, seconds = 0.0):
        '''
        Called to update the sprite. Do this every frame. Handles
        moving the sprite by its velocity.
        '''
        #---kill if too old---
        self.lifetime += seconds
        if self.lifetime > Shot.maxlifetime:
            self.kill()

        #---movement---
        self.move(self.yvelocity)

class BasicEnemyShot(Shot):
    def __init__(self, xy, movementspeed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('beamred.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.maxspeed = 10
        self.yvelocity = 0
        self.lifetime = 0.0 # seconds

         # set position
        self.rect.centerx, self.rect.centery = xy

        # shot movement speed
        self.movementspeed = movementspeed
        self.yvelocity += self.movementspeed

        def update(self, seconds = 0.0):
            '''
            Called to update the sprite. Do this every frame. Handles
            moving the sprite by its velocity.
            '''
        #---kill if too old---
            self.lifetime += seconds
            if self.lifetime > Shot.maxlifetime:
                self.kill()

        #---movement---
        self.move(self.yvelocity)

class EnemyShip(pygame.sprite.Sprite):
    '''
    Class to create basic enemy ships.
    '''
    health = 1

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

    def explosion(self, xy, window):

        self.explosionsound.play()
        self.kill()

    def update(self, xy, enemyhitlist, screen, enemies, shots, ticks, enemyshots, enemieskilled, killbar):
        #---explode if hit by shot---
        for self in pygame.sprite.groupcollide(enemies, shots, False, True):
            self.explosion((self.rect.left, self.rect.top), screen)
            killbar.enemieskilled += 1
            killbar.increase_kill_bar(killbar.enemieskilled)
            print killbar.enemieskilled


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

            self.enemyshot = BasicEnemyShot((self.rect.centerx, self.rect.bottom), 7)
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

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

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

    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self, screen):
        raise NotImplementedError

    def handle_events(self):
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
                    manager.go_to(LevelOne(1, screen))


    def update(self, screen):
        pass


class SceneManager(object):
    '''
    Manages loading all the data unique to each level
    '''
    def __init__(self, screen):
        self.go_to(StartScreen(0, screen))

    def go_to(self, scene):
        self.scene = scene
        self.scene.manager = self

class Game(object):
    '''Handles initialization of PyGame and sets up game'''

    def __init__(self):
        '''Called during initialization'''

        # load and set up pygame
        pygame.init()

        # initialize sound
        pygame.mixer.pre_init(44100, -16, 2, 2048)


    def spawnBasicEnemy(self):
        self.enemyship = self.enemyspawner.getEnemyShip(random.randrange(1, 4, 1))
        self.enemies.add(self.enemyship)

    def run(self):
        '''Runs the game. Contains the game loop.'''

        global screen, screen_width, screen_height, manager
        print "Starting Event Loop"

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

                # check if dead
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
                    self.restart()
                    self.run()

                elif event.key == pygame.K_n:
                    pygame.quit()

    def restart(self):

        pygame.mixer.pre_init(44100, -16, 2, 2048)
        # load and set up pygame
        pygame.init()

        #create window
        self.window = pygame.display.set_mode((1000, 750))
        screen_width, screen_height = 1000, 750

        # game over variable
        self.gameover = False

        # create enemy spawner
        self.enemyspawner = EnemySpawner()
        # timer for keeping track of enemy spawns
        self.lastEnemySpawned = 0
        # keeping track of enemy shots
        self.lastEnemyShot = 0


        #clock for ticking
        self.clock = pygame.time.Clock()

        #window title
        pygame.display.set_caption("Shooter")

        # tell pygame to pay attention to certain events like closing the window


        # make background
        self.background = pygame.image.load('Background-4vertical.png').convert_alpha()
        self.background2 = pygame.image.load('Background-4vertical2.png').convert_alpha()
        self.backgroundrect = self.background.get_rect()
        self.window.blit(self.background, (0, 0))
        self.backgroundspeed = 1
        self.bgOney = 0
        self.bgTwoy = self.background.get_height() * -1

        # draw health bar
        self.healthbar = HealthBar(self.window, ((screen_width/2) - 150, 700))
        self.healthbar.display()

        # a sprite rendering group for our ship
        self.sprites = pygame.sprite.RenderUpdates()
        self.ship = Ship((screen_width/2, screen_height - 100))
        self.sprites.add(self.ship)

        # a sprite rendering group for player's shots
        self.shots = pygame.sprite.RenderUpdates()

        # a sprite group for enemies

        self.enemies = pygame.sprite.RenderUpdates()
        self.enemyship = EnemyShip((screen_width/2, 50))
        self.enemies.add(self.enemyship)
        self.enemyhitlist = []

        # keep track of # of enemies killed
        self.enemieskilled = 0

         # a sprite rendering group for enemies' shots
        self.enemyshots = pygame.sprite.RenderUpdates()

        pygame.display.flip()

# Run the game

if __name__ == '__main__':
    game = Game()
    game.run()