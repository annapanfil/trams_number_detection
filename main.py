from functions import *

"""podejście I - segmentacja na podstawie nasycenia"""
imgs = []
imgs_obr = []
imgs_both = []

# winname = "Test"
# cv2.namedWindow(winname)
# cv2.resizeWindow("winname", 500, 700)
# cv2.createTrackbar("trackbarName", "winname", val, 15, 1) # suwak
# x = cv2.getTrackbarPos("trackbarName", "winname")

for tram in tram_names:
    img = imread("dane/"+tram+".jpg")
    imgs.append(img)
    img_sat = rgb2hsv(img)[:,:,1]

    # recognize segments and choose the best
    segmentated = segmentate_watershed(img_sat)
    cleaned = discard_small_and_big(segmentated)
    cleaned = cleaned.astype(np.uint8)

    masked = cleaned
    imshow(masked)

    # eliminate not red
    red_mask = mask_from_channel(img, 0, 100)
    masked = cv2.bitwise_and(cleaned, cleaned, mask = red_mask)

    # eliminate white (or blue)
    # blue_mask = mask_from_channel(img, 2, 200)
    # blue_mask = cv2.bitwise_not(blue_mask)
    # masked = cv2.bitwise_and(masked, masked, mask = blue_mask)

    img_dark = ((img_sat-0.5)/2).clip(0,1)
    res = cv2.add(img_dark, masked.astype(np.float64))

    imgs_obr.append(masked)
    imgs_both.append(res)

# show_array(imgs, "oryginały")
show_array(imgs_obr, "results")
show_array(imgs_both, "overlapped")




# """ Podejście drugie - wykrywanie konturów - canny + findContours """
# # czasem udaje mu się wykryć koła, ale jest za dużo śmieci, żeby to miało sens
# imgs = []
#
# for tram in tram_names:
#     img = imread("dane/"+tram+".jpg")
#
#     # preprocessing
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blurred = cv2.GaussianBlur(gray, (7,7), 0)
#     edged = cv2.Canny(blurred, 50, 200, 255)
#
#     contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#     cv2.drawContours(img, contours, -1, (0,255,0), 3)
#
#     # choosing contours with the right area
#     contour_list = []
#     for contour in contours:
#         area = cv2.contourArea(contour)
#         if (area <100 and area > 20):
#             contour_list.append(contour)
#     # może lepiej to wykrywać jakimś stosunkiem pola do obwodu albo czymś takim?
#
#     cv2.drawContours(img, contour_list, -1, (255,0,0), 3)
#
#     #dalej trzeba by rozpoznać koła np. cv2.approxPolyDP(), albo jakimś innym Houghem
#
#     imgs.append(img)
# show_array(imgs)
#
#
# # In[ ]:
#
#
# """Podejście trzecie - wykrywanie kół - HoughCircles"""
# # wykrywa koła tam gdzie ich nie ma, ale nie tam gdzie są
# # czy one powinny być zamalowane, albo czy robić to na jakkolwiek obrobionym zdjęciu?
#
# img = imread("dane/"+tram_names[0]+".jpg")
#
# img_circles = draw_circles(img)
#
# show(img_circles)
#
#
# # In[ ]:
#
#
# hist, hist_centers = exposure.histogram(img_sat)
# plt.plot(hist_centers, hist)


# # ideas:
# 1. **więcej preprocessingu** (jakieś podbijanie kontrastu, rozmycie, ustalenie jasności...)
# 1. operowanie jednak na skali szarości?
# 1. **łączenie rozpoznanych obiektów ze skali szarości i z nasycenia albo z nasycenia i wartości**
# 1. jakoś inaczej dobrać parametry przed canny?
#     - Inne rozmycie?
#     - cv2.bilateralFilter(rawImage, 5, 175, 175) zamiast gaussian?
# 1. zmniejszenie rozdzielczości? (Czy to ma jakieś znaczenie)
#
# 1. wykryć koła, sprawdzić ich wielkość, wyciąć i tam szukać lizczb tym algorytmem, który mam
#     - może być wiele kół, może nie wykryć poprawnie koła
#
# 1. Jak wykryć te koła?
#     - HoughCircles
#     - minEnclosingCircle
#
# 1. **Kanał czerwony**
#
#
# Raczej nie:
# 1. wykryć największy obiekt (prawdopodobnie to będzie tramwaj) i szukać na górze od niego
#     - największy może nie być tramwaj, może wykrywać tramwaj w częściach
# 1. ograniczyć szukanie tylko do górnej połowy zdjęcia, obciąć boki
#     - jest ryzyko, że tam właśnie będzie numer, bo zdjęcie będzie słabe
#
#

# - transformata hougha - raczej nieprzydatna
# - momenty hu - do rozpoznawania koła?
# - cv2.find_contorurs
#

# # useful links
#
# wykrywanie obiektów - segmentacja i canny
# [1] https://scikit-image.org/docs/dev/user_guide/tutorial_segmentation.html?fbclid=IwAR3If7rhedSZYwVebDG6oBgy8pPsh6aFgEHUKh1wL7NhZ3XYrDwT4eUOBk4
# [2] https://scikit-image.org/docs/0.12.x/auto_examples/xx_applications/plot_coins_segmentation.html?fbclid=IwAR0JfJK-Nh5Nb8W5rLdySQTCYm0uFPQPsd-AEq1TaExUX0kfpzrkVrk8MJA
#
# wykrywanie liczb
# [3] LCD https://www.pyimagesearch.com/2017/02/13/recognizing-digits-with-opencv-and-python/
#
# wycinanie tła
# [4] messi https://docs.opencv.org/3.1.0/d8/d83/tutorial_py_grabcut.html
# [5] z kamerki https://towardsdatascience.com/background-removal-with-python-b61671d1508a
#
# HoughCircles
# [6] https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
