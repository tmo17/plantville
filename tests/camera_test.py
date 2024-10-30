import cv2

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print(cap.isOpened())
if ret:
    cv2.imwrite('frame.jpg', frame)
cap.release()
