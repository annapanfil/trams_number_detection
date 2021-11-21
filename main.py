from functions import *

def recognize_tram_number(c: dict):
    imgs_obr = []

    true_positive = []
    false_positive = []
    false_negative = []

    for tram in tram_names:
        # read image and convert to gray based on saturation
        img = imread("dane/"+tram+".jpg")
        img_norm = normalize_size(img)
        img_sat = rgb2hsv(img_norm)[:,:,1]

        # recognize segments
        segmentated = segmentate_watershed(img_sat)
        segmentated = segmentated.astype(np.uint8)

        masked = apply_masks(img_norm, segmentated, c["RED_TRESH"], c["BLUE_TRESH"])

        cleaned = discard_small_and_big(masked, c["SMALL_TRESH"], c["BIG_TRESH"])
        cleaned = cleaned.astype(np.uint8)

        # recognize edges
        contours, hierarchy = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        img_cont = img_norm.copy()
        cv2.drawContours(img_cont, contours, -1, (255,0,0), 2)

        digits = set()
        for cnt in contours:
            try:
                slice = process_slice(cnt, img_cont, img_norm, cleaned, c)
                digit = digits_processing(slice)
                digits.add(digit)
            except SliceDiscardedException as e:
                # if e.message == "Background not gray":
                    # print(e.message)
                pass
        res = results_comparision(img_norm, img_cont, digits, tram)

        tp, fp, fn = analyze_results(digits, tram)
        true_positive += tp
        false_positive += fp
        false_negative += fn
        imgs_obr.append(res)

    show_array(imgs_obr, "16_08")

    print_stats(c, len(tram_names), true_positive, false_positive, false_negative, long=False)
    print_stats(c, len(tram_names), true_positive, false_positive, false_negative)

if __name__ == '__main__':
    SMALL_TRESH = 30  # discards smaller
    BIG_TRESH = 800   # discards bigger
    RED_TRESH = 150   # discards all pixels with lower red
    BLUE_TRESH = 140 # discards pixels with higher blue than this
    BB_FACTOR_X = 1.5
    BB_FACTOR_Y = 1.2
    BB_MIN_HEIGHT = 13
    BB_MIN_WIDTH = 4
    GREY_BCKG_LVL = 0.4

    consts = {"RED_TRESH": RED_TRESH, "BLUE_TRESH": BLUE_TRESH, "SMALL_TRESH": SMALL_TRESH, "BIG_TRESH": BIG_TRESH, "BB_FACTOR_X": BB_FACTOR_X, "BB_FACTOR_Y": BB_FACTOR_Y, "BB_MIN_WIDTH": BB_MIN_WIDTH, "BB_MIN_HEIGHT": BB_MIN_HEIGHT, "GREY_BCKG_LVL": GREY_BCKG_LVL}

    recognize_tram_number(consts)
