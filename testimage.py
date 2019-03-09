import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

net = cv2.dnn.readNetFromCaffe("mobilenet_ssd/MobileNetSSD_deploy.prototxt", "mobilenet_ssd/MobileNetSSD_deploy.caffemodel")
# 0.050,0.119
frame = cv2.imread("cap.jpg")
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)#0.001,0.000
(H, W) = frame.shape[:2]
blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)#0.004,0.006
net.setInput(blob)#0.001,0.001
detections = net.forward()#1.010,0.533(different picture size)

# loop over the detections
for i in np.arange(0, detections.shape[2]):
# extract the confidence (i.e., probability) associated
# with the prediction
	confidence = detections[0, 0, i, 2]
	# filter out weak detections by requiring a minimum
	# confidence
	if confidence > 0.4:
		# extract the index of the class label from the
		# detections list
		idx = int(detections[0, 0, i, 1])
		# if the class label is not a person, ignore it
		if CLASSES[idx] != "person":
			continue
		# compute the (x, y)-coordinates of the bounding box
		# for the object
		box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
		(startX, startY, endX, endY) = box.astype("int")
		cv2.rectangle(frame,(startX, startY),(endX,endY),(0,255,0),3)
#cv2.imshow("Frame", frame)
#key = cv2.waitKey() & 0xFF

#cv2.destroyAllWindows()
