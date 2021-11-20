from functions import *

# imgs = []
imgs_obr = []

for tram in tram_names:
    print(tram)
    # read image and convert to gray based on saturation
    img = imread("dane/"+tram+".jpg")
    img_norm = normalize_size(img)
    # imgs.append(img_norm)
    img_sat = rgb2hsv(img_norm)[:,:,1]

    # recognize segments
    segmentated = segmentate_watershed(img_sat)
    segmentated = segmentated.astype(np.uint8)

    masked = apply_masks(img_norm, segmentated, RED_TRESH, BLUE_TRESH)

    cleaned = discard_small_and_big(masked, SMALL_TRESH, BIG_TRESH)
    cleaned = cleaned.astype(np.uint8)

    # del masked

    # recognize edges
    contours, hierarchy = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_cont = img_norm.copy()
    cv2.drawContours(img_cont, contours, -1, (255,0,0), 2)

    digits = []
    for cnt in contours:
        try:
            slice = process_slice(cnt, img_cont, img_norm, cleaned)
            digit = digits_processing(slice)
            digits.append(digit)
        except SliceDiscardedException as e:
            # if e.message == "Background not gray":
                # print(e.message)
            pass

    res = results_comparision(img_norm, img_cont, digits, tram)
    # show(res)
    imgs_obr.append(res)

# show_array(imgs, "oryginały")
res = np.vstack(imgs_obr)
# show_array(imgs_obr, filename = "result")
show(res, filename = "results_vertical")
# show_array(imgs_obr, "results")
