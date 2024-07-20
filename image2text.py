import cv2
import numpy as np
from imutils import resize
from birbeye import get_birdseye_view 
import pytesseract
from struct import pack


def split_32bit_to_16bit(value, inverse=False):
    """Split a 32-bit integer into two 16-bit integers."""
    high = (value >> 16) & 0xFFFF
    low = value & 0xFFFF
    if inverse:
        return [low, high] 

    return [high, low] 


def doNothing(e):
    pass


def ocr_from_image(gray):
    """Use pytesseract to do OCR on the gray.""" 
    text = pytesseract.image_to_string(gray, lang='eng')
    return text


class reader():
    screen_hsv_lower = np.array([0, 0, 170])
    screen_hsv_upper = np.array([255, 255, 255])
    devMode = False

    def __init__(self, _devMode=False):
        from sys import platform
        if platform == 'win32':
            pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'
        print("Initializing")
        self.devMode = _devMode

    def readText(self, image):
        """Read and return a list of text within the given image"""
        textBinary = None
        birdeye = None
        resultList = []
        result = ""

        # coordinate for each line of text
        line_text = [[150, 260, 5, 330], [20, 114, 5, 390]]

        # pre-processing
        image = resize(image, height=300)

        # find contour of screen
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        first, second, third = cv2.split(hsv_image)
        hsv_binary = cv2.inRange(hsv_image, self.screen_hsv_lower, self.screen_hsv_upper)

        # find contours
        contours, _ = cv2.findContours(hsv_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            contour_area = cv2.contourArea(contour)
            if contour_area > 40000:
                # find min-enclosing rectangle around the screen
                rect = cv2.minAreaRect(contour) 
                box = cv2.boxPoints(rect) 
                box = np.intp(box) 

                for i in range(0, 2):
                    birdeye = get_birdseye_view(third, box)[line_text[i][0]:line_text[i][1], line_text[i][2]:line_text[i][3]]

                    if not birdeye.any():
                        return None
                    textBinary = cv2.inRange(birdeye, 0, 140)

                    # enclosing frame of the text
                    text_contours, _ = cv2.findContours(textBinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    x_min = 500
                    for cnt in text_contours:
                        x, y, w, h = cv2.boundingRect(cnt)
                        area = cv2.contourArea(cnt)
                        if x_min > x:
                            x_min = x
                        # print(f"width {i}", x, area)
                    if x_min > 10:
                        x_min -= 10
                    
                    textBinary = textBinary[:, x_min:]
                    textBinary = cv2.dilate(textBinary, np.ones((3, 3), np.uint8))
                    textBinary = resize(textBinary, height=50)

                    raw_result = ocr_from_image(textBinary)



                    # remove the \n at the end
                    raw_result = raw_result[:-1]

                    # remove the last char if it's not a digit. 
                    if len(raw_result) > 2 and not raw_result[-1].isdigit():
                        result = raw_result[:-1]
                    else:
                        result = raw_result
                    
                    try:
                        # add the number the list, the order should be [int, float] 
                        if i == 0:
                            resultList.append(int(float(result)))
                        else:
                            resultList.append(float(result))
                        
                    except Exception as e:
                        if self.devMode:
                            print(e)
                        continue

                    if self.devMode:
                        cv2.imshow(f"{i}", textBinary)

                # only work with the biggest
                break

        if self.devMode:
            for box in line_text:
                image = cv2.rectangle(image, (box[2], box[0]), (box[3], box[1]), (0, 255, 0), 2) 

            result_statck = np.concatenate([image, cv2.cvtColor(hsv_binary, cv2.COLOR_GRAY2RGB)], axis=1)
            print("Readed text ", resultList)
            cv2.imshow('Press Q to exit.', result_statck)

        if len(resultList) == 2:
            # convert and split the list of number int bytes
            byte1 = int.from_bytes(pack("!f", resultList[0]))
            byte2 = int.from_bytes(pack("!f", resultList[1]))
            return split_32bit_to_16bit(byte1, True) + split_32bit_to_16bit(byte2, False)

        return None


if __name__ == "__main__":
    from sys import platform
    _reader = reader(_devMode=True)
    camereFile = '/dev/video0'
    cap = cv2.VideoCapture(camereFile)

    if platform == 'win32':
        # find the index of camera if OS is window
        camereFile = 5
        # cap = cv2.VideoCapture(camereFile)
        for i in range(5, -1, -1):
            success, _ = cap.read()
            if not success:
                print(f"{camereFile} isn't valide.")
                camereFile -= 1
                cap = cv2.VideoCapture(camereFile)
            else:
                print(f"Currently working with {camereFile} camera.")
                break

    while 1:
        _, image = cap.read()
        result = _reader.readText(image)
        print("Bytes: ", result)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    cv2.destroyAllWindows()
