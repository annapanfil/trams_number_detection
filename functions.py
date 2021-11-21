from imports import *


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
    plt.figure(figsize=(cols*30,rows*10), tight_layout=True)

    for i,img in enumerate(arr):
        ax = plt.subplot(rows, cols, i+1)
        ax.set_xticks([])
        ax.set_yticks([])
        imshow(img, cmap='gray')
    plt.savefig("graphics/"+filename, dpi=dpi)
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


def results_comparision(img_norm, img_cont, number: str, filename: str):
    """Produce an image to visually compare original image and result"""
    # img_norm_mini = cv2.resize(img_norm, (MINI_IMG_W, MINI_IMG_H))
    img_cont_mini = cv2.resize(img_cont, (MINI_IMG_W, MINI_IMG_H))

    text = ["img: "+ filename, "Recognized text: "+number]
    res = np.hstack((img_cont_mini, show_text(text))) #img_norm_mini

    return res


def print_stats(c: dict, imgs: int, true_positive: list, false_positive: list, false_negative: list, correct: list, long=True):
    """Print statistics for program"""
    tp = len(true_positive)
    fp = len(false_positive)
    fn = len(false_negative)
    corr = len(correct)
    all = tp + fn

    if long:
        print("PARAMETRY\n------------------------")
        print(f'RED_TRESH {c["RED_TRESH"]}\nBLUE_TRESH {c["BLUE_TRESH"]}\nSMALL_TRESH {c["SMALL_TRESH"]}\nBIG_TRESH {c["BIG_TRESH"]}')
        print(f'BB_FACTOR_X {c["BB_FACTOR_X"]}\nBB_FACTOR_Y {c["BB_FACTOR_Y"]}\nBB_MIN_WIDTH {c["BB_MIN_WIDTH"]}\nBB_MIN_HEIGHT {c["BB_MIN_HEIGHT"]}\nGREY_BCKG_LVL {c["GREY_BCKG_LVL"]}\nWS_LOW {c["WS_LOW"]}\nWS_HIGH {c["WS_HIGH"]}')
        print("")
        print("STATYSTYKI\n------------------------")
        print(f"Liczba zdjęć: {imgs}")
        print(f"Wszystkich cyfr: {all}")
        print("")
        print(f"Poprawnie rozpoznanych cyfr (TP): {tp} czyli {tp*100/all:.2f}%")
        print(f"Inne obiekty uznane za cyfry (FP): {fp}")
        print(f"Nierozpoznanych cyfr (FN): {fn}%")
        print("")
        # print(f"Cyfra najczęściej poprawnie rozpoznawana (TP): {mode(true_positive)[0]}")
        # print(f"Cyfra najczęściej rozpoznawana tam gdzie jej nie ma (FP): {mode(false_positive)[0]}")
        # print(f"Cyfra najczęściej nierozpoznawana (FN): {mode(false_negative)[0]}")
        # print("")
        print(f"Precyzja algorytmu rozpoznawania cyfr: {tp*100/(tp+fp):.2f}%")
        print(f"Pełność algorytmu rozpoznawania cyfr: {tp*100/(tp+fn):.2f}%")

        print("")
        print(f"Poprawnie rozpoznanych numerów: {corr} czyli {corr*100/imgs:.2f}%")
        print(f"Najczęściej poprawnie rozpoznawany numer: {mode(correct)[0]}")

    else:
        print(f'{c["RED_TRESH"]};{c["BLUE_TRESH"]};{c["SMALL_TRESH"]};{c["BIG_TRESH"]};{c["BB_FACTOR_X"]};{c["BB_FACTOR_Y"]};{c["BB_MIN_WIDTH"]};{c["BB_MIN_HEIGHT"]};{c["GREY_BCKG_LVL"]};{c["WS_LOW"]};{c["WS_HIGH"]};{tp*100/all:.2f};{fp*100/all:.2f};{fn*100/all:.2f};{mode(true_positive)[0]};{mode(false_positive)[0]};{mode(false_negative)[0]}; {corr*100/imgs:.2f}; {mode(correct)[0]}')



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
    """cf. [1],[2]"""
    elevation_map = sobel(img)

    markers = np.zeros_like(img)
    markers[img < bg_tresh] = 1
    markers[img > obj_tresh] = 2

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
    """determine wheter slice can be a number"""
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
    # print(slice_bw)
    slice_bw = np.where(slice_bw == 1, 255, slice_bw)
    # print(len(slice_bw)) #change from [0;1] to [0;255]
    # print(min(slice_bw.flatten()),
     # max(slice_bw.flatten()))
    # print(slice_bw)
    slice_bw = cv2.bitwise_not(slice_bw)
    # print(slice_bw.dtype)

    return slice_bw

################################################################################
# tekst processing
def digits_processing(img):
    """Digit from image"""
    custom_config = r'--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789X' # single char, default ocr engine
    # digit = pytesseract.image_to_string(img,config=custom_config)

    digit_dict = pytesseract.image_to_data(img, config=custom_config, output_type=pytesseract.Output.DICT)
    digit = digit_dict["text"][-1]
    conf = digit_dict["conf"][-1]

    digit = digit.replace('\n', '')
    digit = digit.strip()

    return (digit, conf)


def number_from_digits(digits_tupl: list):
    """Return a number from digits. Normal numbers in Poznań are less than 18 (substitutive lines can have higher numbers, but not greater than 99)"""
    digits_tupl = [d for d in digits_tupl if d[0] != '']
    digits = [d[0] for d in digits_tupl]

    if len(digits) == 0:
        return ("", digits)
    if len(digits) == 1:
        return (digits[0][0], digits)

    digits_tupl = [d for d in digits_tupl if d[0] != 'X'] # remove 'X', since it can't occur in 2-digit number
    digits = [d[0] for d in digits_tupl]
    if len(digits) == 1:
        return (digits[0][0], digits)

    if len(digits) > 2:
        # choose two with the highest confidence
        digits_tupl = sorted(digits_tupl, key=lambda x: x[1], reverse=True)
        digits_tupl = digits_tupl[0:2]
        digits = [d[0] for d in digits_tupl]

    if len(digits) == 2:
        first = int(digits[0])
        second = int(digits[1])
        if first > second:
            number = 10*second + first
        else:
            number = 10*first + second

    # if int(number) > 18:
        # print("Probably wrong number: ", number)

    return (str(number), digits)


def analyze_results(digits: set, number:str, filename: str):
    """return stats for result"""
    true_number = filename.split("_")[0]

    true_positive = [x for x in digits if x in true_number] #true_number & digits
    false_positive = [x for x in digits if x not in true_number] #digits - true_number
    false_negative = [x for x in true_number if x not in digits] # true_number - digits

    correct_number = number == true_number

    return (true_positive, false_positive, false_negative, correct_number)
