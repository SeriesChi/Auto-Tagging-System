import cv2
import os
import numpy as np
import faceRecognition as fr


faces,faceID=fr.labels_for_training_data('trainingImage')
face_recognizer=fr.train_classifier(faces,faceID)
face_recognizer.save('trainingData.yml')
face_recognizer=cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read('trainingData.yml')#use this to load training data for subsequent runs