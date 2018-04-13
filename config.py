import pygame
from pygame.locals import *  # noqa

# run headless - for servers
global HEADLESS
HEADLESS = False

global CANVAS_HEIGHT
CANVAS_HEIGHT = 708

global CANVAS_WIDTH
CANVAS_WIDTH = 400

global IMG_SCALE_FACTOR
IMG_SCALE_FACTOR = 0.2

global SAVING
SAVING = False

# where to start counting for game numbers - so we don't overwrite data
global STARTING_NUM
STARTING_NUM = 0

# directory to hold numpy arrays
global DATA_DIR
DATA_DIR = './data'

# directory to hold TensorFlow models
global MODEL_DIR
MODEL_DIR = './models'

# directory to hold training screenshot data
global TRAIN_SCREEN_DIR
TRAIN_SCREEN_DIR = './screenshots'

# directory to hold testing screenshot data
global TEST_SCREEN_DIR
TEST_SCREEN_DIR = './screenshots_test'