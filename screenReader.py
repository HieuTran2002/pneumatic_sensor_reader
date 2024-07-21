import cv2
import asyncio
from subprocess import check_output
from image2text import reader

class screenReader:
    camera_file = None
    cap = None
    check_cam_file_cmd = '/bin/bash getcam.sh'
    reader = reader()
    logger = None
    latest_frame = None

    def __init__(self, _logger=None):
        print(f'Using OpenCV {cv2.__version__}')

        # Assign logger
        if not _logger:
            from theLogger import Logger
            self.logger = Logger()
        else:
            self.logger = _logger

        # Check available camera
        result = check_output([self.check_cam_file_cmd], shell=True).decode('utf-8').strip()
        arr_result = result.split('\n')

        for cam_file in arr_result:
            cap = cv2.VideoCapture(cam_file)
            success, _ = cap.read()
            cap.release()

            if success:
                self.logger.log('info', f"Camera: Successfully initialized camera {cam_file}.")
                self.camera_file = cam_file
                break
            else:
                self.logger.log('error', f"Camera: Failed to open camera {cam_file}")

        if self.camera_file:
            print(self.camera_file)
            self.cap = cv2.VideoCapture(self.camera_file)
        else:
            text = self.logger.log('error', 'No valid camera was found.')
            print(text)
            sys.exit(-1)

    async def update_frame(self):
        while True:
            success, frame = self.cap.read()
            if success:
                self.latest_frame = frame
            await asyncio.sleep(0.11)  # Small sleep to prevent CPU overuse

    async def read(self):
        if self.latest_frame is None:
            self.logger.log('error', f'Unable to extract frame from {self.camera_file}')
            return None
        result = self.reader.readText(self.latest_frame)

        # Check return value
        if result == "":
            return None
        else:
            return result

async def main():
    screen_reader = screenReader()

    while True:
        what_i_see = await screen_reader.read()
        if what_i_see:
            print(what_i_see)
        await asyncio.sleep(1)  # Adjust the sleep time as needed

if __name__ == '__main__':
    asyncio.run(main())

