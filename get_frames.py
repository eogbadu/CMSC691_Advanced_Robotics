import cv2
video = cv2.VideoCapture("assn1.mp4")
nbr_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
fps = video.get(cv2.CAP_PROP_FPS)

timestamp = 2.75
frame_nbr = timestamp * fps


video.set(1, frame_nbr)

success, frame = video.read()
cv2.imwrite(f'Frame at {timestamp}.jpg', frame)
