import os

import cv2

from datetime import datetime
from picamera2 import Picamera2

#print(cv2.getBuildInformation())

# Set up folder to save new capture data in
now = datetime.now()
date_time = now.strftime("%Y%m%d%H%M")
dirname = "arducamRGB" + date_time
filepath = os.path.join(os.getcwd(),dirname)
os.mkdir(filepath)
print("saving images to: " + filepath)
os.chdir(filepath)

camera = Picamera2()
camera_config = camera.create_still_configuration()
camera.configure(camera_config)
camera.start()

#print(camera)

count = 1
first = True

# Set up display
window_name = "Webcam Capture"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

result = True
while result:
    img = camera.capture_array()

    print(result)

    if result:
        #img = img[0:480, 0:480]
        #resize window to image
        if first:
            (height, width, _) = img.shape
            cv2.resizeWindow(window_name, width * 2, height * 2)
            first == False
        
        #show image in window
        cv2.imshow(window_name, img)

        name = str(count) + ".png"#note--change filetype to option
        cv2.imwrite(name, img)
        count+=1

        # Process key events.
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

        # Check if the window has been closed manually.
        if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
            break

cv2.destroyWindow(window_name)
