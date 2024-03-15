# This is a file created for a specific dataset project
# It captures images synchronously from both TIR and RGB cameras
# It is based on combined.py with the display code removed so that it can run
# headless
#
# Original author: Michael S. Mead <mmead@thermal.com>
# Modified for use in this application by Emma Wadsworth <u1081622@utah.edu>
# Modified for use in this application by Dudley Irish <d.irish@utah.edu>
#
# The license for the original code is here: https://www.apache.org/licenses/LICENSE-2.0
#   
# As a note, this requires the seekcamera.dll file provided in the seek thermal programming kit

import argparse
import cv2
import os
import time
from threading import Condition
from datetime import datetime
from picamera2 import Picamera2

from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCamera,
    SeekFrame,
)

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [COUNT] [DELAY]",
        description="Capture data from IR and RGB cameras."
        )
    parser.add_argument('count', nargs='?', default = 1);
    parser.add_argument('delay', nargs='?', default = 1);
    return parser

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
    parser = init_argparse()
    args = parser.parse_args()
    print(f'count: {args.count}')
    print(f'delay: {args.delay}')
    count = int(args.count);
    delay = int(args.delay);
    pairNum = 1

    # Set up folder to save new capture data in
    now = datetime.now()
    date_time = now.strftime("%Y%m%d%H%M")
    rgbdir = os.path.join(os.getcwd(),"RGB" + date_time)
    os.mkdir(rgbdir)
    tirdir = os.path.join(os.getcwd(),"TIR" + date_time)
    os.mkdir(tirdir)

    rgb = Picamera2()
    camera_config = rgb.create_still_configuration()
    rgb.configure(camera_config)
    rgb.start()

    start = time.time()

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
                    #get images into img (TIR) and frame (RGB)
                    img = renderer.frame.data
                    
                    ogrgb = rgb.capture_array()
                    #rgbimg = cv2.rotate(ogrgb, cv2.ROTATE_180)
                    rgbimg = ogrgb;

                    filename = f"{pairNum:04d}.jpg"
                    #TIR img to file here
                    os.chdir(tirdir)
                    cv2.imwrite(filename, img)
                    
                    #RGB img to file here
                    os.chdir(rgbdir)
                    cv2.imwrite(filename, rgbimg)

                    print(f"Written: {filename}")
                    pairNum+=1
                    if pairNum > count:
                        break

                    if ((start + delay) - time.time()) > 0:
                        time.sleep((start + delay) - time.time())
                        start = time.time()

            # Process key events.
            key = cv2.waitKey(1)
            if key == ord("q"):
                break

if __name__ == "__main__":
    main()
