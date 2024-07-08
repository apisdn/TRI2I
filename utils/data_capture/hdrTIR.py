#!/usr/bin/env python3
# Copyright 2021 Seek Thermal Inc.
#
# This is a basic file that will capture thermal data from the SeekThermal camera 
# and save it to a specified file in a specified format
#
# Original author: Michael S. Mead <mmead@thermal.com>
# Modified for use in continuous capture applications by Emma Wadsworth <u1081622@utah.edu>
#
# The license for the original code is here: https://www.apache.org/licenses/LICENSE-2.0
#

from threading import Condition

import os

import cv2

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
        camera.color_palette = SeekCameraColorPalette.WHITE_HOT #change to TYRIAN for pretty pink

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
    # Make sure that seekcamera.dll is in the current working directory of this project. 
    # Also make sure you have installed the Seek Camera SDK
    cwd = os.getcwd()
    os.environ["SEEKTHERMAL_LIB_DIR"] = cwd

    # Set up folder to save new capture data in
    now = datetime.now()
    date_time = now.strftime("%Y%m%d%H%M")
    dirname = "hdrTIR_" + date_time
    filepath = os.path.join(cwd,dirname)
    os.mkdir(filepath)
    print("saving images to: " + filepath)
    os.chdir(filepath)

    count = 1
    gainmode = 0
    gains = np.array([0.45, 0.85, 0.15])

    # Set up display
    window_name = "Thermal Capture"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Create a context structure responsible for managing all connected USB cameras.
    # Cameras with other IO types can be managed by using a bitwise or of the
    # SeekCameraIOType enum cases.
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)

        renderer.camera.histeq_agc_gain_limit = 0.15 #0.65 is default

        while True:
            # Wait a maximum of 150ms for each frame to be received.
            # A condition variable is used to synchronize the access to the renderer;
            # it will be notified by the user defined frame available callback thread.
            with renderer.frame_condition:
                if renderer.frame_condition.wait(150.0 / 1000.0):
                    img = renderer.frame.data
                    img = img[0:240, 0:240]

                    # Resize the rendering window.
                    if renderer.first_frame:
                        (height, width, _) = img.shape
                        cv2.resizeWindow(window_name, width * 2, height * 2)
                        renderer.first_frame = False
                        renderer.camera.histeq_agc_gain_limit = gains[gainmode] #0.65 is default
                    else:
                        name = str(count) + "_" + str(gainmode) + ".png"

                        if gainmode == 2:
                            gainmode = 0
                            count += 1
                        else:
                            gainmode += 1

                        renderer.camera.histeq_agc_gain_limit = gains[gainmode] #0.65 is default

                        # Render the image to the window.
                        cv2.imshow(window_name, img)
                
                        #name = str(count) + ".png"#note--change filetype to option
                        cv2.imwrite(name, img)
                        #count+=1


            # Process key events.
            key = cv2.waitKey(1)
            if key == ord("q"):
                break

            # Check if the window has been closed manually.
            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                break


    cv2.destroyWindow(window_name)


if __name__ == "__main__":
    main()
