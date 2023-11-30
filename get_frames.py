import cv2

def GetFrames ( time, file_name, img_file):
    video = cv2.VideoCapture(file_name)
    nbr_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)

    timestamp = time
    frame_nbr = timestamp * fps


    video.set(1, frame_nbr)

    success, frame = video.read()
    cv2.imwrite(img_file, frame)
