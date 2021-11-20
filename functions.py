# from imports import *


class SliceDiscardedException(Exception):
    def __init__(self, _message):
        self.message = _message

###############################################################################

# showing
def show_array(arr, filename="tramwaje", dpi=30, cols = None):
    "Show a mosaic of images list and save it to jpg"
    if(len(arr)==0):
        print("Show_array: Nothing to show")
        return
    if cols == None:
        cols = int(np.sqrt(len(arr)))
    rows = ceil(len(arr)/cols)
    plt.figure(figsize=(cols*30,rows*20))

    for i,img in enumerate(arr):
        ax = plt.subplot(rows, cols, i+1)
        ax.set_xticks([])
        ax.set_yticks([])
        imshow(img, cmap='gray')
    plt.savefig("output/"+filename, dpi=dpi)
    # plt.show()

def show(*args, filename = None):
    """Show multiple images in a row"""
    plt.figure(figsize=(20,12))
    for i,img in enumerate(args):
        plt.subplot(1, len(args), i+1)
        imshow(img, cmap='gray')
    if filename != None:
        print("Saved to output/"+filename)
        plt.savefig("output/"+filename)
    plt.show()


def show_text(texts: list):
    """Create an image from text"""
    img = np.zeros((MINI_IMG_H, MINI_IMG_W,3), np.uint8)

    for i, text in enumerate(texts):
        cv2.putText(img, text, (10, 30*(i+1)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, 2)

    return img


def results_comparision(img_norm, img_cont, digits: set, filename: str):
    number_str = ''.join(digits)
    # img_norm_mini = cv2.resize(img_norm, (MINI_IMG_W, MINI_IMG_H))
    img_cont_mini = cv2.resize(img_cont, (MINI_IMG_W, MINI_IMG_H))

    text = ["img: "+ filename, "Recognized text: "+number_str]
    res = np.hstack((img_cont_mini, show_text(text))) #img_norm_mini

    return res


def print_stats(imgs: int, true_positive: list, false_positive: list, false_negative: list, long=True):
    tp = len(true_positive)
    fp = len(false_positive)
    fn = len(false_negative)
    all = tp + fp + fn
    if long:
        print("PARAMETRY\n------------------------")
        print(f"RED_TRESH {RED_TRESH}\nBLUE_TRESH {BLUE_TRESH}\nSMALL_TRESH {SMALL_TRESH}\nBIG_TRESH {BIG_TRESH}")
        print(f"BOUNDING_BOX_FACTOR_X {BOUNDING_BOX_FACTOR_X}\nBOUNDING_BOX_FACTOR_Y {BOUNDING_BOX_FACTOR_Y}\nBB_MIN_WIDHT {BB_MIN_WIDHT}\nBB_MIN_HEIGHT {BB_MIN_HEIGHT}\nGREY_BCKG_LVL {GREY_BCKG_LVL}")
        print("")
        print("STATYSTYKI\n------------------------")
        print(f"Liczba zdjęć: {imgs}")
        print(f"Wszystkich cyfr: {all}")
        print("")
        print(f"Poprawnie rozpoznanych cyfr (TP): {tp} czyli {tp*100/all:.2f}%")
        print(f"Inne obiekty uznane za cyfry (FP): {fp} czyli {fp*100/all:.2f}%")
        print(f"Nierozpoznanych cyfr (FN): {fn} czyli {fn*100/all:.2f}%")
        print("")
        print(f"Cyfra najczęściej poprawnie rozpoznawana (TP): {mode(true_positive)[0]}")
        print(f"Cyfra najczęściej rozpoznawana tam gdzie jej nie ma (FP): {mode(false_positive)[0]}")
        print(f"Cyfra najczęściej nierozpoznawana (FN): {mode(false_negative)[0]}")
    else:
        print(f"{RED_TRESH};{BLUE_TRESH};{SMALL_TRESH};{BIG_TRESH};{BOUNDING_BOX_FACTOR_X};{BOUNDING_BOX_FACTOR_Y};{BB_MIN_WIDHT};{BB_MIN_HEIGHT};{GREY_BCKG_LVL};{tp*100/all:.2f};{fp*100/all:.2f};{fn*100/all:.2f};{mode(true_positive)[0]};{mode(false_positive)[0]};{mode(false_negative)[0]}")



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
    img_chann_bw[img_chann > treshold] = 255

    return img_chann_bw

def apply_masks(img_src, img_to_mask, red_tresh, blue_tresh):
    """eliminate not red enough or too blue segments"""
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

def check_surroundings(slice, img_cont, img_src, img_clean):
    """Check if background is gray enough"""
    x,y,w,h = slice

    # extend bounding box
    dx = int((w*BOUNDING_BOX_FACTOR_X - w)/2)
    dy = int((h*BOUNDING_BOX_FACTOR_Y - h)/2)
    begin_x = np.clip(x-dx, 0, IMG_W)
    end_x = np.clip(x+w+dx, 0, IMG_W)
    begin_y = np.clip(y-dy, 0, IMG_H)
    end_y = np.clip(y+h+dy, 0, IMG_H)

    cv2.rectangle(img_cont, (begin_x,begin_y), (end_x, end_y), (0,0,255), 2)

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

    if median > GREY_BCKG_LVL: raise SliceDiscardedException(f'Background not gray (median = {median:.2f})')


def process_slice(cnt, img_cont, img_src, img_clean):
    """determine wheter slice can be a number"""
    # draw bounding box
    x, y, w, h = cv2.boundingRect(cnt)
    if (w < BB_MIN_WIDHT or h < BB_MIN_HEIGHT): raise SliceDiscardedException("Too thin")
    if (w > h-2): raise SliceDiscardedException("Horizontal")

    slice = check_surroundings((x,y,w,h), img_cont, img_src, img_clean)
    cv2.rectangle(img_cont,  (x,y), (x+w, y+h), (0,255,0), 2)

    slice_bw = img_clean[y-2:y+h+2, x-2:x+w+2]
    slice_bw = np.where(slice_bw == 1, 255, slice_bw) #change from [0;1] to [0;255]
    slice_bw = cv2.bitwise_not(slice_bw)

    return slice_bw

################################################################################
# tekst processing
def digits_processing(img):
    custom_config = r'--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789X' #single char, default ocr engine,  outputbase digits
    digit = pytesseract.image_to_string(img,config=custom_config)
    digit = digit.replace('\n', '')
    digit = digit.strip()
    return digit

def analyze_results(digits: set, filename: str):
    digits.discard('')
    for digit in digits:
        if len(digit) != 1: print (f"!!!!{digit}")

    true_digits = set(filename.split("_")[0])

    true_positive = true_digits & digits
    false_positive = digits - true_digits
    false_negative = true_digits - digits

    return (true_positive, false_positive, false_negative)
