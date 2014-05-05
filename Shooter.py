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
                game.shiphit.play()

    def enemyCollision(self, playerspritegroup, enemies, healthbar):

        for self in pygame.sprite.groupcollide(playerspritegroup, enemies, False, False):
            if game.ticks - self.lastcollision > 500:
                self.lastcollision = game.ticks
                healthbar.decrease_health(20)
                game.shiphit.play()
            else:
                pass



    def update(self):
        self.move(self.xvelocity, self.yvelocity)
        self.shotCollision(game.sprites, game.enemyshots, game.healthbar)
        self.enemyCollision(game.sprites, game.enemies, game.healthbar)

    def reset(self, xy):
        self.rect.centerx, self.rect.centery = xy

class HealthBar(object):
    def __init__(self, window, location):
        self.window = window
        self.image = pygame.image.load('healthbar.png').convert()
        self.location = location
        self.healthrect = pygame.draw.rect(self.window, blue,(self.location[0], self.location[1], 200, 50), 0)
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

    def display(self):
       # load bar background
        self.window.blit(self.image, (self.location[0], self.location[1]))
    # build bar rectangle
        self.bar = pygame.Rect(self.topleft[0],\
                               self.topleft[1],\
                                self.health,\
                                self.height)
    # draw bar rectangle
        pygame.draw.rect(self.window, self.color, self.bar, 0)

class KillBar(object):
    def __init__(self, window, location):
        self.window = window
        self.image = pygame.image.load('healthbar.png').convert()
        self.location = location
        self.killrect = pygame.draw.rect(self.window, blue,(self.location[0], self.location[1], 200, 50), 0)
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

    def display(self):
       # load bar background
        self.window.blit(self.image, (self.location[0], self.location[1]))
    # build bar rectangle
        self.bar = pygame.Rect(self.topleft[0],\
                               self.topleft[1],\
                                self.enemieskilled * 2.8,\
                                30)
    # draw bar rectangle
        pygame.draw.rect(self.window, self.color, self.bar, 0)

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
        print "spawn point: " + str(self.spawnpoint)
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
        print "exploding!"
        explosion.play()
        game.explosionsound.play()
        self.kill()

    def update(self, xy, enemyhitlist, window):
        #---explode if hit by shot---
        for self in pygame.sprite.groupcollide(game.enemies, game.shots, False, True):
            self.explosion((self.rect.left, self.rect.top), game.window)
            game.enemieskilled += 1
            game.killbar.increase_kill_bar(game.enemieskilled)
            print game.enemieskilled


        self.offscreen()
        self.move()
        self.enemyshoot()

    def offscreen(self):
        if self.rect.x < 0 or self.rect.x > screen_width:
            self.kill()
        elif self.rect.y > screen_height:
            self.kill()

    def enemyshoot(self):
        if game.ticks - self.lastshot > 800:
            self.lastshot = game.ticks

            self.enemyshot = BasicEnemyShot((self.rect.centerx, self.rect.bottom), 7)
            game.enemyshots.add(self.enemyshot)

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

class StartScreen(object):
    '''
    The Title screen for the game
    '''
    def __init__(self):
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
            self.window.fill(black)
            self.startScreenSurf = pygame.transform.rotate(self.startScreenSurf, self.degrees1)
            placement_rect1 = self.startScreenSurf.get_rect()
            placement_rect1.center = (screen_width / 2, screen_height / 2)

            self.placement_presstoPlay = pygame.transform.rotate(self.presstoPlaySurf, self.degrees1)
            placement_presstoPlayRect = self.placement_presstoPlay.get_rect()
            placement_presstoPlayRect.center = (screen_width / 2, (screen_height / 2) + (screen_height / 4))

            # Draw them to the screen
            screen.blit(self.placement_presstoPlay, placement_presstoPlayRect)
            screen.blit(self.startScreenSurf, placement_rect1)


        def handle_events(self):

            while start == False:
             # poll for events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()

                # handle user input
                    elif event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()

                        elif event.key == pygame.K_SPACE:
                            pygame.mixer.music.stop()
                            start = True

class LevelLoader(object):
    '''
    Manages loading all the data unique to each level
    '''
    def __init__(self):
        self.go_to(StartScreen())

class Game(object):
    '''Handles initialization of PyGame and sets up game'''
    global screen_width, screen_height
    def __init__(self):
        '''Called during initialization'''

        pygame.mixer.pre_init(44100, -16, 2, 2048)
        # load and set up pygame
        pygame.init()

        #create window
        self.window = pygame.display.set_mode((1000, 750))
        screen_width, screen_height = 1000, 750


        # start screen
        self.startScreen()

        # game over variable
        self.gameover = False

        # create enemy spawner
        self.enemyspawner = EnemySpawner()
        # timer for keeping track of enemy spawns
        self.lastEnemySpawned = 0
        # keeping track of enemy shots
        self.lastEnemyShot = 0

        # set up sounds
        self.lasersound = pygame.mixer.Sound('laser1.wav')
        self.shiphit = pygame.mixer.Sound('boom7.wav')
        self.music = pygame.mixer.music.load('Donkey Kong Country 2 - Stickerbrush Symphony Acapella.mp3')
        self.explosionsound = pygame.mixer.Sound('boom9.wav')
        pygame.mixer.music.play(-1, 0.0)

        #clock for ticking
        self.clock = pygame.time.Clock()

        #window title
        pygame.display.set_caption("Shooter")

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

        # draw kill bar
        self.killbar = KillBar(self.window, ((screen_width / 2) - 150, 0))
        self.killbar.display()

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

    def spawnBasicEnemy(self):
        self.enemyship = self.enemyspawner.getEnemyShip(random.randrange(1, 4, 1))
        self.enemies.add(self.enemyship)

    def draw(self, window):
                        # update background
            self.window.blit(self.background, (0, self.bgOney))
            self.window.blit(self.background2, (0, self.bgTwoy))

                    #update our sprites
            for sprite in self.sprites:
                sprite.update()
            for sprite in self.shots:
                sprite.update()
            for sprite in self.enemies:
                sprite.update((sprite.rect.centerx, sprite.rect.centery), self.enemyhitlist, self.window)
            for sprite in self.enemyshots:
                sprite.update()

            #render our sprites
            self.sprites.clear(self.window, self.background) # clears the window where sprites are
            dirty = self.sprites.draw(self.window)  #calculates the 'dirty' rectangles that need to be redrawn

            # render shots
            self.shots.clear(self.window, self.background)
            dirty += self.shots.draw(self.window)

            # render enemies
            self.enemies.clear(self.window, self.background)
            dirty += self.enemies.draw(self.window)

            # render enemy shots
            self.enemyshots.clear(self.window, self.background)
            dirty += self.enemyshots.draw(self.window)

            # render health bar
            self.healthbar.display()

            # render kill bar
            self.killbar.display()

            # blit the dirty areas of the screen
            pygame.display.update(dirty)

            pygame.display.flip()



    def run(self):
        '''Runs the game. Contains the game loop.'''

        print "Starting Event Loop"

        running = True
        # run until something tells us to stop
        while running:

            #tick pygame clock
            #limit fps
            self.clock.tick(60)

            # if game is not over
            if self.gameover == False:

                #handle pygame events
                running = self.handleEvents()

                # update title bar with fps
                pygame.display.set_caption('Shooter  %d fps' % self.clock.get_fps())

            # spawn enemy ships
                self.ticks = pygame.time.get_ticks() # get millisecond 'ticks' since starting game
                if len(self.enemies) < 30 and self.ticks - self.lastEnemySpawned > 800:  # if there are less than 20
                                                                                    # onscreen enemies and it's been at
                                                                                    # least one second since the last
                                                                                    # was spawned.
                    self.lastEnemySpawned = self.ticks # the last spawn is now
                    self.enemyship = self.enemyspawner.getEnemyShip(random.randrange(1, 4, 1)) # spawn enemy ship
                    self.enemies.add(self.enemyship) # add the enemy ship to enemy sprite group

                else:
                    pass

                # check if dead
                if self.healthbar.health == 0:
                    self.gameover = True

                # scrolling background
                self.bgOney += 2
                self.bgTwoy += 2

                if self.bgOney >= 750:
                    self.bgOney = (self.bgTwoy + self.background2.get_height() * -1)

                if self.bgTwoy >= 750:
                    self.bgTwoy = (self.bgOney + self.background.get_height() * -1)


                self.draw(self.window)

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

                # ship control
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.ship.left()
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.ship.right()
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.ship.up()
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.ship.down()

                # Make the ship shoot
                if event.key == pygame.K_SPACE:
                    self.shot = Shot((self.ship.rect.right - 18.5, self.ship.rect.top), -10)
                    self.shots.add(self.shot)
                    self.lasersound.play()


            elif event.type == pygame.KEYUP:
                # ship control
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.ship.right()
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.ship.left()
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.ship.down()
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.ship.up()
        return True

    def startScreen(self):

        # Start Screen Music
        pygame.mixer.pre_init(44100, -16, 2, 2048)

        self.music = pygame.mixer.music.load('02 Chemical Reaction.mp3')
        pygame.mixer.music.play()

        # Create Title text
        self.startScreenFont = pygame.font.Font('freesansbold.ttf', 44)
        self.startScreenSurf = self.startScreenFont.render('GENERIC SHOOTER', True, white)
        self.degrees1 = 0

        # Create 'Press Space to Play' text

        self.presstoPlayFont = pygame.font.Font('freesansbold.ttf', 20)
        self.presstoPlaySurf = self.presstoPlayFont.render('Press Space to Play!', True, white)

        # Render surfaces
        self.window.fill(black)
        self.startScreenSurf = pygame.transform.rotate(self.startScreenSurf, self.degrees1)
        placement_rect1 = self.startScreenSurf.get_rect()
        placement_rect1.center = (screen_width / 2, screen_height / 2)

        self.placement_presstoPlay = pygame.transform.rotate(self.presstoPlaySurf, self.degrees1)
        placement_presstoPlayRect = self.placement_presstoPlay.get_rect()
        placement_presstoPlayRect.center = (screen_width / 2, (screen_height / 2) + (screen_height / 4))

        # Draw them to the screen
        self.window.blit(self.placement_presstoPlay, placement_presstoPlayRect)
        self.window.blit(self.startScreenSurf, placement_rect1)
        pygame.display.flip()

        start = False
        while start == False:
         # poll for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            # handle user input
                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()

                    elif event.key == pygame.K_SPACE:
                        pygame.mixer.music.stop()
                        start = True

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

        # set up sounds
        self.lasersound = pygame.mixer.Sound('laser1.wav')
        self.shiphit = pygame.mixer.Sound('boom7.wav')
        self.music = pygame.mixer.music.load('Donkey Kong Country 2 - Stickerbrush Symphony Acapella.mp3')
        self.explosionsound = pygame.mixer.Sound('boom9.wav')
        pygame.mixer.music.play(-1, 0.0)

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