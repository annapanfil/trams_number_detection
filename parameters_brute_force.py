from imports import *
from main import recognize_tram_number
import time

SMALL_TRESH = 30  # discards smaller
BIG_TRESH = 800   # discards bigger
RED_TRESH = 150   # discards all pixels with lower red
BLUE_TRESH = 140 # discards pixels with higher blue than this
BB_FACTOR_X = 1.5
BB_FACTOR_Y = 1.2
BB_MIN_HEIGHT = 13
BB_MIN_WIDTH = 4
GREY_BCKG_LVL = 0.4



start = time.time()
consts = {"RED_TRESH": RED_TRESH, "BLUE_TRESH": BLUE_TRESH, "SMALL_TRESH": SMALL_TRESH, "BIG_TRESH": BIG_TRESH, "BB_FACTOR_X": BB_FACTOR_X, "BB_FACTOR_Y": BB_FACTOR_Y, "BB_MIN_WIDTH": BB_MIN_WIDTH, "BB_MIN_HEIGHT": BB_MIN_HEIGHT, "GREY_BCKG_LVL": GREY_BCKG_LVL}

recognize_tram_number(consts)

end = time.time()
print(end - start)
