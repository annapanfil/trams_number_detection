from imports import *
from main import recognize_tram_number
import time


# RED_TRESH = 140   # discards all pixels with lower red
# BLUE_TRESH = 130  # discards pixels with higher blue than this
# SMALL_TRESH = 20  # discards smaller
# BIG_TRESH = 300  # discards bigger
# BOUNDING_BOX_FACTOR_X = 1.5
BB_FACTOR_Y = 1.2
# GREY_BCKG_LVL = 0.4
#
# BB_MIN_WIDHT = 5
# BB_MIN_HEIGHT = 7
# GREY_BCKG_LVL = 0.3


start = time.time()
for RED_TRESH in range(100, 180, 10):       # 8
    for BLUE_TRESH in range(90, 160, 10):   # 7
        for SMALL_TRESH in range(20,30, 2): # 9
            for BIG_TRESH in range (100, 500, 100): #4
                for BB_FACTOR_X in np.arange(1.3, 1.8, 0.2):    #3
                        for BB_MIN_WIDHT in range(5, 10, 2):    # 3
                            for BB_MIN_HEIGHT in range(6, 11, 2):   # 3
                                for GREY_BCKG_LVL in (0.1, 0.2, 0.3): #4
                                    consts = {"RED_TRESH": RED_TRESH, "BLUE_TRESH": BLUE_TRESH, "SMALL_TRESH": SMALL_TRESH, "BIG_TRESH": BIG_TRESH, "BB_FACTOR_X": BB_FACTOR_X, "BB_FACTOR_Y": BB_FACTOR_Y, "BB_MIN_WIDHT": BB_MIN_WIDHT, "BB_MIN_HEIGHT": BB_MIN_HEIGHT, "GREY_BCKG_LVL": GREY_BCKG_LVL}

                                    recognize_tram_number(consts)

end = time.time()
print(end - start)
