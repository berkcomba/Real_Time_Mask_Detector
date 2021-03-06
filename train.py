#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 11:43:10 2020

@author: berk
"""



import os
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D,Dense,Flatten,MaxPool2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelBinarizer

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split
from imutils import paths
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

#------------------------------------------------------
#This section for reduce some errors related to GPU allocation on my system.
#it may not neccesary for yours. If it is, removing this part may increase the performance.
from tensorflow import Session,ConfigProto
from keras.backend.tensorflow_backend import set_session
config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.7
set_session(Session(config=config))
#--------------------------------------------------------


# initialize the learning rate, number of epochs to train for,
# and batch size
INIT_LR = 1e-4
EPOCHS = 25
BATCHSIZE = 32

width= 150
height= 150


#Define model function
def defineModel():
    model = Sequential()                                         
    model.add(Conv2D(32,(3,3),activation="relu",input_shape=(width,height,3)))    
    model.add(MaxPool2D((2,2)))
    model.add(Conv2D(64,(3,3),activation="relu"))
    model.add(MaxPool2D((2,2)))
    model.add(Conv2D(128,(3,3),activation="relu"))
    model.add(MaxPool2D((2,2)))
    model.add(Conv2D(128,(3,3),activation="relu"))
    model.add(MaxPool2D((2,2)))
    model.add(Flatten())
    model.add(Dense(512,activation="relu"))
    model.add(Dense(2,activation="sigmoid"))
    
    model.summary()
    return model



Paths = list(paths.list_images(os.getcwd()+"/dataset"))
images = []
labels = []


#process the images and labels
for i in Paths:
	label = i.split(os.path.sep)[-2]

	image = load_img(i, target_size=(width, height))
	image = img_to_array(image)
	image = preprocess_input(image)

	images.append(image)
	labels.append(label)
    

images = np.array(images, dtype="float32")
labels = np.array(labels)    

# One Hot 
lb = LabelBinarizer()
labels = lb.fit_transform(labels)
labels = to_categorical(labels)

    

(trainX, testX, trainY, testY) = train_test_split(images, labels,
	test_size=0.20, stratify=labels, random_state=42)

# Define an image generator for data aug and increas generalization
aug = ImageDataGenerator(
	rotation_range=10,
	zoom_range=0.10,
	width_shift_range=0.1,
	height_shift_range=0.1,
	shear_range=0.15,
	horizontal_flip=True,
	fill_mode="nearest")
    
opt = Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS)

model=defineModel()


model.compile(loss="binary_crossentropy", optimizer=opt,
	metrics=["accuracy"])

#training
H = model.fit(
	aug.flow(trainX, trainY, batch_size=BATCHSIZE),
	steps_per_epoch=len(trainX) // BATCHSIZE,
	validation_data=(testX, testY),
	validation_steps=len(testX) // BATCHSIZE,
	epochs=EPOCHS)

#testing
predIdxs = model.predict(testX, batch_size=BATCHSIZE)

#take the index of the max value for each prediction. 0=mask on 1=mask of
predIdxs = np.argmax(predIdxs, axis=1)

# show a nicely formatted classification report
print(classification_report(testY.argmax(axis=1), predIdxs,
	target_names=lb.classes_))

#saving the model into current directory
model.save(os.path.join(os.getcwd(),"model.h5"))

# plot the training loss and accuracy
plt.plot(np.arange(0, EPOCHS), H.history["acc"], label="train_acc")
plt.plot(np.arange(0, EPOCHS), H.history["val_acc"], label="val_acc")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.show()









