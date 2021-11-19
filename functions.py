from imports import *


class SliceDiscardedException(Exception):
    def __init__(self, _message):
        self.message = _message

###############################################################################

# showing
def show_array(arr, filename="tramwaje", dpi=30):
    "Show a mosaic of images list and save it to jpg"
    if(len(arr)==0):
        print("Show_array: Nothing to show")
        return

    cols = int(np.sqrt(len(arr)))
    rows = ceil(len(arr)/cols)
    plt.figure(figsize=(cols*30,rows*20))

    for i,img in enumerate(arr):
        ax = plt.subplot(rows, cols, i+1)
        ax.set_xticks([])
        ax.set_yticks([])
        imshow(img, cmap='gray')
    plt.savefig(filename, dpi=dpi)
    plt.show()

def show(*args):
    """Show multiple images in a row"""
    plt.figure(figsize=(20,12))
    for i,img in enumerate(args):
        plt.subplot(1, len(args), i+1)
        imshow(img, cmap='gray')

################################################################################
# preprocessing
def normalize_size(img):
    """change proportions to 3:2 and resize it to 900x600"""
    #todo: vertical images!!!
    h, w, _ = img.shape
    img_cropped = img
    print(w/h)
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
    img_cropped = cv2.resize(img_cropped, (900,600))

    return img_cropped


################################################################################
# processing

def segmentate_watershed(img):
    """Apply watershed segmentation to gray image"""
    """cf. [1],[2]"""
    elevation_map = sobel(img)

    markers = np.zeros_like(img)
    markers[img < 0.4] = 1
    markers[img > 0.95] = 2

    segmentation = watershed(elevation_map, markers)
    segmentation = ndi.binary_fill_holes(segmentation - 1)

    return segmentation


def discard_small_and_big(segmentated_img, min_size_tresh, max_size_tresh):
    """discard small object - noise and big - tram or buildings"""
    label_objects, nb_labels = ndi.label(segmentated_img)

    sizes = np.bincount(label_objects.ravel())  #ilość wystąpień każdej cyfry w sprasowanej tabeli

    mask_sizes = np.logical_and(sizes<max_size_tresh, sizes>min_size_tresh)
    cleaned = mask_sizes[label_objects]

    return cleaned


def mask_from_channel(img, x:int, treshold:int ):
    """Return mask from rgb channel on desired treshold"""
    img_chann = img[:,:,x]

    img_chann_bw = np.zeros_like(img_chann)
    img_chann_bw[img_chann > treshold] = 1

    return img_chann_bw

def apply_masks(img_src, img_to_mask, red_tresh, blue_tresh):
    """eliminate not enough red or too blue segments"""
    # eliminate not red
    red_mask = mask_from_channel(img_src, 0, red_tresh)
    masked = cv2.bitwise_and(img_to_mask, img_to_mask, mask = red_mask)

    # eliminate white (or blue)
    blue_mask = mask_from_channel(img_src, 2, blue_tresh)
    blue_mask = cv2.bitwise_not(blue_mask)
    masked = cv2.bitwise_and(masked, masked, mask = blue_mask)

    return masked

def check_surroundings(slice, img_cont, img_src, img_clean):
    x,y,w,h = slice

    # extend bounding box
    dx = int((w*BOUNDING_BOX_FACTOR_X - w)/2)
    dy = int((h*BOUNDING_BOX_FACTOR_Y - h)/2)
    cv2.rectangle(img_cont, (x-dx,y-dy), (w+x+2*dx, y+h+2*dy), (0,0,255), 1)

    # check background color
    slice = img_src[y-dy:y+h+2*dy, x-dx:x+w+2*dx]
    mask_slice = img_clean[y-dy:y+h+2*dy, x-dx:x+w+2*dx]
    mask_slice = cv2.bitwise_not(mask_slice)
    slice_v = rgb2hsv(slice)[:,:,2]
    slice_backgnd = cv2.bitwise_and(slice_v, slice_v, mask = mask_slice)
    np.where(slice_backgnd == 100, np.nan, slice_backgnd)

    if np.median(slice_backgnd > 30): raise SliceDiscardedException("Background not gray")
    return slice

def process_slice(cnt, img_cont, img_src, img_clean):
    """determine wheter slice can be a number"""
    # draw bounding box
    x, y, w, h = cv2.boundingRect(cnt)
    if (w < 5 or h < 5): raise SliceDiscardedException("Too thin")
    if (w > h-2): raise SliceDiscardedException("Horizontal")
    cv2.rectangle(img_cont,  (x,y), (x+w, y+h), (0,255,0), 1)

    slice = check_surroundings((x,y,w,h), img_cont, img_src, img_clean)

    return slice

################################################################################
# old

def draw_circles(img):
    """ Detect circles in the image and draw them """
    """ cf. [6]"""

    output = img.copy()
    circles = cv2.HoughCircles(edged, cv2.HOUGH_GRADIENT, 1.2, 100) #maxRadius=100

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int") # (x, y) coordinates and radius to int
        for (x, y, r) in circles:
            # draw circle and center on the output image
            cv2.circle(output, (x, y), r, (0, 255, 0), 3)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1) # center

    return output
