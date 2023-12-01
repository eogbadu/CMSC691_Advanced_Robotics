import cv2
import os

# Constants
IMAGES_PATH = 'images'

def GetFrames (time, video_file_path, image_filename):
    try: 
        video = cv2.VideoCapture(video_file_path)
        
        # Check if the video can be opened
        if not video.isOpened():
            print(f"Error in opening video in path: {video_file_path}")
        fps = video.get(cv2.CAP_PROP_FPS)

        timestamp = time

        #video set expects a whole number
        frame_nbr = int(timestamp * fps)

        # use cv2.CAP_PROP_POS_FRAMES not 1 for propId
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_nbr)
    
        success, frame = video.read()

        # check if the video was successfully read at that frame
        if not success:
            print(f"Error: Failed to read frame: {image_filename} in path: {video_file_path}")
        
        # get the current working dir
        current_directory = os.getcwd()

        # set the images dir
        images_dir = os.path.join(current_directory,IMAGES_PATH)
        
        #crop the images
        frame = frame[70:480, 0:630]
        
        # now write the image to the directory
        cv2.imwrite(os.path.join(images_dir,image_filename), frame)
        
        print(f"Successfully converted {image_filename} to image")

        return True
    
    except Exception as e:
        print(f"Error: {e}")
    return False
    
