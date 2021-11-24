from imports import *


class SliceDiscardedException(Exception):
    def __init__(self, _message):
        self.message = _message

################################################################################
# preprocessing
def normalize_size(img):
    """change proportions to 3:2 and resize it to 900x600"""
    #todo: vertical images!!!
    h, w, _ = img.shape
    img_cropped = img
    if w/h > 3/2 + 0.1: # zbyt panoramiczne
        #cut both sides
        new_w = 3*h/2
        delta = int((w - new_w)/2)
        img_cropped = img[: , delta:w-delta, :]
    elif w/h < 3/2 - 0.1: # za wysokie
        #cut the top and the bottom
        new_h = int((2*w)/3)
        delta = int((h - new_h)/2)
        img_cropped = img[delta:h-delta , :, :]

    """change dpi"""
    img_cropped = cv2.resize(img_cropped, (IMG_W, IMG_H))

    return img_cropped


################################################################################
# processing

def segmentate_watershed(img, bg_tresh, obj_tresh):
    """Apply watershed segmentation to gray image"""
    elevation_map = sobel(img)

    markers = np.zeros_like(img)
    markers[img < bg_tresh] = 1
    markers[img > obj_tresh] = 2

    segmentation = watershed(elevation_map, markers)
    segmentation = ndi.binary_fill_holes(segmentation - 1)

    return segmentation


def discard_small_and_big(segmentated_img, min_size_tresh, max_size_tresh):
    """Discard small object - noise and big - tram or buildings"""
    label_objects, nb_labels = ndi.label(segmentated_img)

    sizes = np.bincount(label_objects.ravel())  #ilość wystąpień każdej cyfry w sprasowanej tabeli

    mask_sizes = np.logical_and(sizes<max_size_tresh, sizes>min_size_tresh)
    cleaned = mask_sizes[label_objects]

    return cleaned


def mask_from_channel(img, x:int, treshold:int ):
    """Return mask from rgb channel on desired treshold"""
    img_chann = img[:,:,x]

    img_chann_bw = np.zeros_like(img_chann)
    img_chann_bw[img_chann > treshold] = 255

    return img_chann_bw


def apply_masks(img_src, img_to_mask, red_tresh, blue_tresh):
    """Eliminate not red enough or too blue segments"""
    # eliminate not red
    red_mask = mask_from_channel(img_src, 0, red_tresh)
    masked = cv2.bitwise_and(img_to_mask, img_to_mask, mask = red_mask)

    # eliminate white (or blue)
    blue_mask = mask_from_channel(img_src, 2, blue_tresh)
    blue_mask = cv2.bitwise_not(blue_mask)
    masked = cv2.bitwise_and(masked, masked, mask = blue_mask)

    return masked

#######################################################
# slices

def check_surroundings(slice: tuple, img_cont, img_src, img_clean, consts: dict):
    """Check if background is gray enough"""
    x,y,w,h = slice

    # extend bounding box
    dx = int((w*consts["BB_FACTOR_X"] - w)/2)
    dy = int((h*consts["BB_FACTOR_Y"] - h)/2)
    begin_x = np.clip(x-dx, 0, IMG_W)
    end_x = np.clip(x+w+dx, 0, IMG_W)
    begin_y = np.clip(y-dy, 0, IMG_H)
    end_y = np.clip(y+h+dy, 0, IMG_H)

    # cv2.rectangle(img_cont, (begin_x,begin_y), (end_x, end_y), (0,0,255), 2)

    # get slices of: original image, values from hsv and cleaned image
    slice = img_src[begin_y:end_y, begin_x:end_x]
    slice_v = rgb2hsv(slice)[:,:,2]

    mask_slice = img_clean[begin_y:end_y, begin_x:end_x]
    mask_slice = np.where(mask_slice == 1, 255, mask_slice) #change from [0;1] to [0;255]
    mask_slice = cv2.bitwise_not(mask_slice)

    # get background color
    slice_backgnd = cv2.bitwise_and(slice_v, slice_v, mask = mask_slice)

    # count median without masked values
    slice_backgnd = np.where(slice_backgnd == 0, np.nan, slice_backgnd)
    median = np.nanmedian(slice_backgnd)

    if median > consts["GREY_BCKG_LVL"]: raise SliceDiscardedException(f'Background not gray (median = {median:.2f})')


def process_slice(cnt, img_cont, img_src, img_clean, consts: dict):
    """Determine wheter slice can be a number"""
    # draw bounding box
    x, y, w, h = cv2.boundingRect(cnt)
    if (w < consts["BB_MIN_WIDTH"] or h < consts["BB_MIN_HEIGHT"]): raise SliceDiscardedException("Too thin")
    if (w > h-2): raise SliceDiscardedException("Horizontal")

    slice = check_surroundings((x,y,w,h), img_cont, img_src, img_clean, consts)
    cv2.rectangle(img_cont,  (x,y), (x+w, y+h), (0,255,0), 2)

    begin_x = np.clip(x-2, 0, IMG_W)
    end_x = np.clip(x+w+2, 0, IMG_W)
    begin_y = np.clip(y-2, 0, IMG_H)
    end_y = np.clip(y+h+2, 0, IMG_H)

    slice_bw = img_clean[begin_y:end_y, begin_x:end_x]
    slice_bw = np.where(slice_bw == 1, 255, slice_bw)
    slice_bw = cv2.bitwise_not(slice_bw)

    return slice_bw
