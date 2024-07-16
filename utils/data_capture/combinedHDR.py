# This is a file created for a specific dataset project
# It captures images synchronously from both TIR and RGB cameras
# Really it's just a combination of the other code in this repository
# And it is more use specific than the others, so check croppint and camera alignment well
#
# Original author: Michael S. Mead <mmead@thermal.com>
# Modified for use in this application by Emma Wadsworth <u1081622@utah.edu>
#
# The license for the original code is here: https://www.apache.org/licenses/LICENSE-2.0
#   
# As a note, this requires the seekcamera.dll file provided in the seek thermal programming kit

from threading import Condition

import cv2
import os
from datetime import datetime
import numpy as np

from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCamera,
    SeekFrame,
)


class Renderer:
    """Contains camera and image data required to render images to the screen."""

    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True


def on_frame(_camera, camera_frame, renderer):
    """Async callback fired whenever a new frame is available.
    Parameters
    ----------
    _camera: SeekCamera
        Reference to the camera for which the new frame is available.
    camera_frame: SeekCameraFrame
        Reference to the class encapsulating the new frame (potentially
        in multiple formats).
    renderer: Renderer
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the renderer object.
    """

    # Acquire the condition variable and notify the main thread
    # that a new frame is ready to render. This is required since
    # all rendering done by OpenCV needs to happen on the main thread.
    with renderer.frame_condition:
        renderer.frame = camera_frame.color_argb8888
        renderer.frame_condition.notify()


def on_event(camera, event_type, event_status, renderer):
    """Async callback fired whenever a camera event occurs.
    Parameters
    ----------
    camera: SeekCamera
        Reference to the camera on which an event occurred.
    event_type: SeekCameraManagerEvent
        Enumerated type indicating the type of event that occurred.
    event_status: Optional[SeekCameraError]
        Optional exception type. It will be a non-None derived instance of
        SeekCameraError if the event_type is SeekCameraManagerEvent.ERROR.
    renderer: Renderer
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the Renderer object.
    """
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return

        # Claim the renderer.
        # This is required in case of multiple cameras.
        renderer.busy = True
        renderer.camera = camera

        # Indicate the first frame has not come in yet.
        # This is required to properly resize the rendering window.
        renderer.first_frame = True

        # Set a custom color palette.
        # Other options can set in a similar fashion.
        camera.color_palette = SeekCameraColorPalette.WHITE_HOT
        # WHITE_HOT, TYRIAN

        # Start imaging and provide a custom callback to be called
        # every time a new frame is received.
        camera.register_frame_available_callback(on_frame, renderer)
        camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        # Check that the camera disconnecting is one actually associated with
        # the renderer. This is required in case of multiple cameras.
        if renderer.camera == camera:
            # Stop imaging and reset all the renderer state.
            camera.capture_session_stop()
            renderer.camera = None
            renderer.frame = None
            renderer.busy = False

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return


def main():
    cwd = os.getcwd()
    os.environ["SEEKTHERMAL_LIB_DIR"] = cwd

    window_name = "Thermal Capture"
    other_window = "RGB Capture"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.namedWindow(other_window, cv2.WINDOW_NORMAL)

    # file name will be pairnum--change it every session so you have different names for everything
    pairNum = 1
    gainmode = 0
    gains = np.array([0.45, 0.85, 0.15])

    # Set up folder to save new capture data in
    now = datetime.now()
    date_time = now.strftime("%Y%m%d%H%M")
    dir1 = os.path.join(os.getcwd(),"TIR" + date_time)
    os.mkdir(dir1)
    dir2 = os.path.join(os.getcwd(),"RGB" + date_time)
    os.mkdir(dir2)
    dir3 = os.path.join(os.getcwd(),"TIRfull" + date_time)
    os.mkdir(dir3)
    dir4 = os.path.join(os.getcwd(),"RGBfull" + date_time)
    os.mkdir(dir4)

    rgb = cv2.VideoCapture(0) # video capture source camera

    # Create a context structure responsible for managing all connected USB cameras.
    # Cameras with other IO types can be managed by using a bitwise or of the
    # SeekCameraIOType enum cases.
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)

        while True:
            # Wait a maximum of 150ms for each frame to be received.
            # A condition variable is used to synchronize the access to the renderer;
            # it will be notified by the user defined frame available callback thread.
            with renderer.frame_condition:
                if renderer.frame_condition.wait(150.0 / 1000.0):
                    # Resize the rendering window.
                    if renderer.first_frame:
                        renderer.camera.histeq_agc_gain_limit = gains[2] #0.65 is default

                        height = 256
                        width = 256
                        cv2.resizeWindow(window_name, width * 2, height * 2)
                        cv2.resizeWindow(other_window, width * 2, height * 2)
                        renderer.first_frame = False
                    else:
                        #get images into img (TIR) and frame (RGB)
                        img = renderer.frame.data
                        pureTIR = img;#tir normal
                        img = img[0:240, 20:260]#tir square was 40:280 on second one
                        #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                        ret,ogrgb = rgb.read()
                        rgbimg = cv2.flip(ogrgb, 1)#flip horizontally
                        rgbimg = cv2.rotate(rgbimg, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        pureRGB = rgbimg[140:500, 0:480]#480x640->480x360
                        pureDim = (320,240)
                        pureRGBr = cv2.resize(pureRGB, pureDim, interpolation = cv2.INTER_AREA)
                        rgbimg = rgbimg[64:576, 0:512]

                        filename = str(pairNum)
                    
                        #TIR img to file here
                        os.chdir(dir1)
                        dim = (256, 256)
                        resizedt = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
                        cv2.imwrite(filename + "_" + str(gainmode) + ".png", resizedt)
                    
                        #RGB img to file here
                        os.chdir(dir2)
                        resizedr = cv2.resize(rgbimg, dim, interpolation = cv2.INTER_AREA)
                        cv2.imwrite(filename + ".png", resizedr)

                        #saving pure versions
                        filename = str(pairNum) + ".bmp"
                        os.chdir(dir3)
                        cv2.imwrite(filename + "_" + str(gainmode) + ".png", pureTIR)
                        os.chdir(dir4)
                        cv2.imwrite(filename + ".png", pureRGBr)

                        # deal with getting hdr settings right
                        if gainmode == 2:
                            gainmode = 0
                            pairNum += 1
                        else:
                            gainmode += 1

                        renderer.camera.histeq_agc_gain_limit = gains[gainmode] #0.65 is default

                        # Render the image to the window.
                        cv2.imshow(window_name, img)
                        cv2.imshow(other_window, rgbimg)

            # Process key events.
            key = cv2.waitKey(1)
            if key == ord("q"):
                break

            # Check if the window has been closed manually.
            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                break

    cv2.destroyWindow(window_name)
    cv2.destroyWindow(other_window)


if __name__ == "__main__":
    main()