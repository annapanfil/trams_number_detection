from imports import *

def digits_processing(img):
    """Digit from image"""
    custom_config = r'--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789X' # single char, default ocr engine

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
    """Return stats for result"""
    true_number = filename.split("_")[0]

    true_positive = [x for x in digits if x in true_number] #true_number & digits
    false_positive = [x for x in digits if x not in true_number] #digits - true_number
    false_negative = [x for x in true_number if x not in digits] # true_number - digits

    correct_number = number == true_number

    return (true_positive, false_positive, false_negative, correct_number)
