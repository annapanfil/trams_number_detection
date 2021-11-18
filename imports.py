import numpy as np
from numpy import array

from math import ceil

from matplotlib import pylab as plt
from matplotlib.pyplot import imshow

from pylab import imread

import skimage
from skimage import morphology, measure, draw, feature, exposure
from skimage.color import rgb2hsv, rgb2gray
from skimage.morphology import square
from skimage.feature import canny
from skimage.filters import sobel
from skimage.segmentation import watershed

import cv2

from scipy import ndimage as ndi


# tram_names = ["10_01", "10_02", "1_01", "1_02", "1_03", "1_04", "1_05", "1_06", "1_07", "11_01", "11_02", "11_03", "11_04", "11_05", "11_06", "12_01", "12_02", "12_03", "12_04", "12_05", "13_01", "13_02", "13_03", "14_01", "14_02", "14_03", "14_04", "14_05", "15_01", "15_02", "15_03", "16_01", "16_02", "16_03", "16_04", "16_05", "16_06", "16_07", "16_08", "16_09", "16_10", "16_11", "16_12", "16_13", "16_14", "16_15", "16_16", "16_17", "16_18", "16_19", "16_20", "16_21", "16_22", "17_01", "17_02", "17_03", "17_04", "17_05", "17_06", "18_01", "18_02", "19_01", "2_01", "21_01", "3_01", "3_02", "3_10", "4_01", "4_02", "4_03", "4_04", "5_01", "5_02", "5_03", "5_04", "5_05", "5_06", "5_07", "5_08", "5_09", "5_10", "5_11", "5_12", "5_13", "5_14", "6_01", "6_02", "6_03", "6_04", "6_05", "6_06", "6_07", "6_08", "7_01", "7_02", "8_01", "8_02", "9_01", "9_02", "9_03", "wiele_5_16_01", "X_01"]
tram_names = ["1_02", "1_06", "2_01" ,"5_07","5_12","5_14", "4_04" ,"6_02", "12_02"] #
# tram_names = ["4_04"]
