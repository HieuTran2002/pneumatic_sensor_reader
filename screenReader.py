import cv2
from imutils.convenience import sys
from subprocess import check_output
from image2text import reader


class screenReader():
    cameraFile = None
    cap = None
    checkCamFileCMD = '/bin/bash getcam.sh'
    reader = reader()
    logger = None

    def __init__(self, _logger=None):
        print(f'Using Opencv {cv2.__version__}')

        # assign logger
        if not _logger:
            from theLogger import Logger
            self.logger = Logger()
        else:
            self.logger = _logger

        # check available camera
        result = check_output([self.checkCamFileCMD], shell=True).decode('utf-8').strip()
        arrResult = result.split('\n')

        for camFile in arrResult:

            cap = cv2.VideoCapture(camFile)
            success, _ = cap.read()
            cap.release()

            if success:
                self.logger.log('info', f"Camera: Successfully initialized camera {camFile}.")
                self.cameraFile = camFile
                break
            else:
                self.logger.log('error', f"Camera: Failed to open camera {camFile}")

        if self.cameraFile:
            print(self.cameraFile)
            # self.cap = cv2.VideoCapture(self.cameraFile)
            self.cap = cv2.VideoCapture('/dev/video2')
        else:
            text = self.logger.log('error', 'No valid camera was found.')
            print(text)
            sys.exit(-1)

    def read(self):
        success, frame = self.cap.read()

        # check cam
        if success:
            result = self.reader.readText(frame)

            # check return value
            if result == "":
                return None
            else:
                return result
        else:
            self.logger.log('error', f'Unable to extract frame from {self.cameraFile}')
            return None


if __name__ == '__main__':
    screenReader = screenReader()
    while 1:
        whatIC = screenReader.read()
        if whatIC:
            print(whatIC)
