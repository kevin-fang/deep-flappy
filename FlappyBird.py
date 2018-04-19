import pygame, sys, os, random
from pygame.locals import *  # noqa
import neural_jumper
from config import *
from global_vars import *
import numpy as np

def makeDirIfNotExist(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

class FlappyGame:
    def __init__(self):
        # set up the display
        if HEADLESS:
           # os.environ["SDL_VIDEODRIVER"] = "dummy"
            #self.real_screen = pygame.display.set_mode((1,1))
            self.real_screen = pygame.display.set_mode((1, 1))
            self.screen = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT)).convert()
        else:
            self.screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))

        self.bird = pygame.Rect(65, 50, 50, 50)
        self.background = pygame.image.load("assets/background.png").convert()
        self.birdSprites = [pygame.image.load("assets/1.png").convert(),
                            pygame.image.load("assets/2.png").convert()]
        # create pipes
        self.wallUp = pygame.image.load("assets/bottom.png").convert()
        self.wallDown = pygame.image.load("assets/top.png").convert()

        # set the gap between the pipes
        self.gap = 250

        self.wallx = 400
        self.birdY = 350
        self.jump = 0
        self.jumpSpeed = 10
        self.gravity = 8
        self.dead = False
        self.sprite = 0

        self.offset = random.randint(-110, 110)

        # point counter
        self.counter = 0

        # counts since last jump
        self.last_jump_counter = 0
        # frames since starting
        self.alive_frames = 0

        # counters for image storage
        self.image_counter = 0
        self.game_counter = 1

        self.saved_game_counter = 0

        # make the first screenshot folder
        makeDirIfNotExist(TRAIN_SCREEN_DIR)
        makeDirIfNotExist(os.path.join(TRAIN_SCREEN_DIR, "game{}".format(self.game_counter)))

    # move the walls to the left or teleport them to the end
    def updateWalls(self):
        self.wallx -= 2
        if self.wallx < -80:
            self.wallx = 400
            self.counter += 1
            self.offset = random.randint(-110, 110)

    def check_collision(self, temporary_update = False):
        # up and down pipes

        wallx = self.wallx if not temporary_update else self.wallx - 4

        upRect = pygame.Rect(wallx,
                             360 + self.gap - self.offset + 10,
                             self.wallUp.get_width() - 10,
                             self.wallUp.get_height())
        downRect = pygame.Rect(wallx,
                               0 - self.gap - self.offset - 10,
                               self.wallDown.get_width() - 10,
                               self.wallDown.get_height())
        return upRect.colliderect(self.bird) or downRect.colliderect(self.bird)

    def birdUpdate(self):
        # if jumping, account for acceleration and lower the bird
        if self.jump:
            self.jumpSpeed -= 1
            self.birdY -= self.jumpSpeed
            self.jump -= 1
        else:
            # move the bird down
            self.birdY += self.gravity
            self.gravity += 0.2

        self.bird[1] = self.birdY

        # if collide with pipe
        if self.check_collision():
            self.dead = True
            # make the game reset immediately
            self.bird[1] = -1

        # check if bird has fallen above/below the screen
        if not 10 < self.bird[1] < CANVAS_HEIGHT:
            return True

        return False

    def reset_game(self):
        self.alive_frames = 0
        self.bird[1] = 350
        self.birdY = 350
        self.dead = False
        self.counter = 0
        self.wallx = 400
        self.offset = random.randint(-110, 110)
        self.gravity = 5

    def get_score(self):
        #print("bird y: ", self.bird[1])
        if self.check_collision(temporary_update = True) or not 10 < self.birdY < CANVAS_HEIGHT or self.bird[1] == -1:
            return -1
        elif self.wallx - 2 < -80:
            return 1
        else:
            return .01

    def frameUpdate(self, jump):
        self.screen.fill((255, 255, 255))
        # keep this line commented out for training - less distracting background
        #self.screen.blit(self.background, (0, 0))

        self.screen.blit(self.wallUp,
                         (self.wallx, 360 + self.gap - self.offset))
        self.screen.blit(self.wallDown,
                         (self.wallx, 0 - self.gap - self.offset))
        self.screen.blit(self.font.render(str(self.counter),
                                    0,
                                    (0, 0, 0)),
                                    (200, 50))
        # change sprite 
        if self.jump:
            self.sprite = 1

        self.screen.blit(self.birdSprites[self.sprite], (70, self.birdY))
        if not self.dead:
            self.sprite = 0
        
        self.updateWalls()
        dead = self.birdUpdate()

        score = self.get_score()
        if score != 0.01: print(score)

        if score == -1:
            dead = True

        if dead:
            print("Game {} over; alive frames: {}".format(self.game_counter, self.alive_frames))
            if (self.game_counter == NUM_GAMES):
                print("{} games finished. Exiting...".format(NUM_GAMES))
                return True
            self.reset_game()

        screenshot_name = os.path.join(TRAIN_SCREEN_DIR, "game{}".format(self.game_counter), 
                                                    "{img_num}_{y}_{r}_{last_jump}_capture.jpg"
                                                        .format(y=1 if jump else 0, 
                                                                r=score, 
                                                                last_jump=self.last_jump_counter, 
                                                                img_num=self.image_counter))
        
        if SAVING:
            pygame.image.save(self.screen, screenshot_name)
            
        if dead:
            # reset the image counter and increment the game counter
            self.game_counter += 1
            self.image_counter = 0
            makeDirIfNotExist(os.path.join(TRAIN_SCREEN_DIR, "game{}".format(self.game_counter)))

        self.image_counter += 1

        pygame.display.update()

    def run(self, model = False):
        # initialize game and game counter font
        clock = pygame.time.Clock()
        pygame.font.init()
        font = pygame.font.SysFont("Arial", 50)
        self.font = font
        over = self.frameUpdate(jump = None)
        neural_jumper.initialize_network(model)

        if over: return

        while True:
            clock.tick()
            # get a jump from the neural network
            image = pygame.image.tostring(self.screen, "RGB")
            result = neural_jumper.get_jump(image, self.last_jump_counter)[0]
            # flip a biased coin
            #print("result: {}".format(result))
            # send events to jump or stay
            if result == 1:
                self.last_jump_counter = 0
                pygame.event.post(JUMP)
            elif result == 0:
                self.last_jump_counter += 1
                pygame.event.post(STAY)

            event = pygame.event.wait()
            #for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == JUMP_CONST and not self.dead:
                self.jump = 17
                self.gravity = 5
                self.jumpSpeed = 10
                self.alive_frames += 1
                over = self.frameUpdate(jump = True)
                if over: 
                    pygame.quit()
                    return
            elif event.type == STAY_CONST and not self.dead:
                #print(self.last_jump_counter)
                self.alive_frames += 1
                over = self.frameUpdate(jump = False)      
                if over: 
                    pygame.quit()
                    return