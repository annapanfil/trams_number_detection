from imports import *

# showing
def show_array(arr, filename="tramwaje"):
    "Show a mosaic of images list and save it to jpg"
    cols = int(np.sqrt(len(arr)))
    rows = ceil(len(arr)/cols)
    plt.figure(figsize=(cols*30,rows*20))

    for i,img in enumerate(arr):
        ax = plt.subplot(rows, cols, i+1)
        ax.set_xticks([])
        ax.set_yticks([])
        imshow(img, cmap='gray')
    plt.savefig(filename, dpi=50)
    plt.show()

def show(*args):
    """Show multiple images in a row"""
    plt.figure(figsize=(20,12))
    for i,img in enumerate(args):
        plt.subplot(1, len(args), i+1)
        imshow(img, cmap='gray')

# preprocessing
def normalize_size(img):
    """change proportions to 3:2"""
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



# processing

def discard_small_and_big(segmentated_img, min_size_tresh, max_size_tresh):
    """discard small object - noise and big - tram or buildings"""
    label_objects, nb_labels = ndi.label(segmentated_img)

    sizes = np.bincount(label_objects.ravel())  #ilość wystąpień każdej cyfry w sprasowanej tabeli

#     print("sizes", sizes, max(sizes), min(sizes))
#     n, bins, patches = plt.hist(sizes[np.logical_and(sizes<1000, sizes>50)])
#     print(n, bins)

    mask_sizes = np.logical_and(sizes<max_size_tresh, sizes>min_size_tresh) # dobrać wartości do eliminacji małych i dużych obiektów
    cleaned = mask_sizes[label_objects]

    return cleaned

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

def mask_from_channel(img, x:int, treshold:int ):
    img_chann = img[:,:,x]

    img_chann_bw = np.zeros_like(img_chann)
    img_chann_bw[img_chann > treshold] = 1

    return img_chann_bw





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
