from imports import *

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
