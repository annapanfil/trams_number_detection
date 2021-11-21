from imports import *
from main import recognize_tram_number
import time

RED_TRESH = 150   # discards all pixels with lower red
BLUE_TRESH = 140 # discards pixels with higher blue than this
SMALL_TRESH = 30  # discards smaller
BIG_TRESH = 800   # discards bigger
BB_FACTOR_X = 1.5
BB_FACTOR_Y = 1.2
BB_MIN_WIDTH = 4
BB_MIN_HEIGHT = 13
GREY_BCKG_LVL = 0.4
WS_LOW = 0      # 0.1 zmniejsza FP
WS_HIGH = 0.9

start = time.time()
for WS_HIGH in [1]:
    consts = {"RED_TRESH": RED_TRESH, "BLUE_TRESH": BLUE_TRESH, "SMALL_TRESH": SMALL_TRESH, "BIG_TRESH": BIG_TRESH, "BB_FACTOR_X": BB_FACTOR_X, "BB_FACTOR_Y": BB_FACTOR_Y, "BB_MIN_WIDTH": BB_MIN_WIDTH, "BB_MIN_HEIGHT": BB_MIN_HEIGHT, "GREY_BCKG_LVL": GREY_BCKG_LVL, "WS_LOW": WS_LOW, "WS_HIGH": WS_HIGH}

    recognize_tram_number(consts)

end = time.time()
print(end - start)
