import cv2
import os

# Constants
IMAGES_PATH = 'images'  #name of the images folder
PATTERN_NAVIGATOR = 'navigator' #name pattern to cut navigator files
PATTERN_WIZARD = 'wizard'    #name pattern to cut wizard files


def GetFrames (time, video_file_path, image_filename):
    """Extracts one single frame from a video path at a 
    given timestamp and saves it to a folder"

    Args:
        time (_type_): _description_
        video_file_path (string): path of a video file
        image_filename (string): _description_

    Returns:
        image_filename: returns image filename in images folder if successful
    """

    # try to extract the frame
    try: 
        video = cv2.VideoCapture(video_file_path)
        
        # Check if the video can be opened
        if not video.isOpened():
            print(f"Error in opening video in path: {video_file_path}")
            return False
        fps = video.get(cv2.CAP_PROP_FPS)

        timestamp = time

        #video set expects a whole number
        frame_nbr = int(timestamp * fps)

        # use cv2.CAP_PROP_POS_FRAMES not 1 for propId
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_nbr)
    
        success, frame = video.read()

        # check if the video was successfully read at that frame
        if not success:
            print(f"Error: Failed to read frame in path: {video_file_path}")
            return False
        
        # get the current working dir
        current_directory = os.getcwd()

        # set the images dir
        images_dir = os.path.join(current_directory,IMAGES_PATH)
        
        # Check what type of video_file it is 
        if PATTERN_NAVIGATOR in image_filename:
            print("cropping to navigator layout")
            frame = frame[70:480, 0:630]
        # otherwise it is pattern_two
        elif PATTERN_WIZARD in image_filename:
            print("cropping to wizard layout")
            pass
               
        # now write the image to the directory
        cv2.imwrite(os.path.join(images_dir,image_filename), frame)
        
        print(f"Successfully converted {image_filename} to image")

        return image_filename
    
    except Exception as e:
        print(f"Error: {e}")
    # else we should return False
    return False
    
