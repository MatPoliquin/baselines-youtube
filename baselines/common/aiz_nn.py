import cv2
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import numpy as np
import math
import tensorflow as tf
import gc
from py3nvml.py3nvml import *
from PIL import Image
import os
from cpuinfo import get_cpu_info
import psutil
from _thread import start_new_thread
from time import sleep
#import Queue
import threading
#import broadcast


class AIZ_NeuralNet():
    def __init__(self):
        #self.tf = None
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.UpdateNeuralNetFrameCount=0
        self.action_meaning = []
        self.action = 0
        self.action_prob = 0
    
    def clear_screen(self, final, posX, posY, width, height, color = (0,0,0)):
        final[posY:posY+height,posX:posX+width] = color

    def set_action_taken(self, action):
        self.action = action

    def set_action_prob(self, logprob):
        self.action_prob = logprob

    def set_action_meaning(self, actionlist):
        #self.env = env
        #for i in range(0,36):
        #    print(self.env.unwrapped.get_action_meaning(i))
        
        self.action_meaning = actionlist.copy()
        #print('==============ACTION MEANINGS SET================')
        #print('Size:%d' % len(self.action_meaning))
        #for i in range(0,len(self.action_meaning)):
        #    print(self.action_meaning[i])
        #print('=================================================')

    def DrawInputLayer(self, final, img, posX, posY):
        cv2.putText(final, ("Input"), (posX, posY), self.font, 2.0, (255,255,255), 1 ,2)
        cv2.putText(final, ("84x84 greyscale"), (posX, posY + 15), self.font, 1.0, (0,255,0), 1 ,2)
        cv2.putText(final, ("Last 4 frames"), (posX, posY + 30), self.font, 1.0, (0, 255,0), 1 ,2)

        dim = (84,84)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        input = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
        #final[500:dim[1]+500,0:dim[0]] = input

        imgPosX = posX
        imgPosY = posY + 50
        final[imgPosY:imgPosY+dim[1],imgPosX:imgPosX+dim[0]] = input
        imgPosY += dim[1] + 50
        cv2.putText(final, ("[...]"), (posX, imgPosY), self.font, 1.0, (0,255,0), 1 ,2)
        #final[imgPosY:imgPosY+dim[1],imgPosX:imgPosX+dim[0]] = input
        #imgPosY += dim[1] + 50
        #final[imgPosY:imgPosY+dim[1],imgPosX:imgPosX+dim[0]] = input
        #imgPosY += dim[1] + 50
        #final[imgPosY:imgPosY+dim[1],imgPosX:imgPosX+dim[0]] = input
    
    def DrawConvNetLayer(self, final, posX, posY, numFilters, filterSize, name, param_name, input_dim):
        cv2.putText(final, ("%s" % name), (posX, posY), self.font, 1.0, (255,255,255), 1 ,2)
        cv2.putText(final, ("%d filters" % (numFilters)), (posX, posY + 15), self.font, 1.0, (0,255,0), 1 ,2)
        cv2.putText(final, ("%dx%d" % (filterSize, filterSize)), (posX, posY + 30), self.font, 1.0, (0,255,0), 1 ,2)
        
        #cv2.rectangle(final, (posX + 100,posY + 480), (180, 560), (255,255,255))

        #test = tf.get_variable(param_name)
        #print(test)
        #print(test.shape)

        with tf.variable_scope(param_name, reuse=True) as conv_scope:
            hello = tf.get_variable('w', shape=[filterSize,filterSize,input_dim,numFilters])
            #print(hello)
            weights0 = tf.transpose(hello, [3,0,1,2])
            weights = weights0.eval()
            #print(weights.shape)

            num_channels = hello.shape.dims[3]
            filter_w = hello.shape.dims[0]
            filter_h = hello.shape.dims[1]

            x = posX
            y = posY + 40

            for channel in range(0,10):
                img = weights[channel,:,:,0]
                #print(img.eval())
                #img = img * 255.0

                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                #img2 = []
                img2 = cv2.normalize(img,None,0,255,cv2.NORM_MINMAX)

                dim = (filter_w*4,filter_h*4)
                upscaled = cv2.resize(img2, dim, interpolation=cv2.INTER_NEAREST)

          
                

                final[y:y+dim[1], x:x+dim[0]] = upscaled
                y+=dim[1] + 5

            
            cv2.putText(final, ("[...]"), (posX, y + 40), self.font, 1.0, (0,255,0), 1 ,2)
        

    def DrawHiddenLayer(self, final, posX, posY):
        cv2.putText(final, ("Hidden Layer"), (posX, posY), self.font, 1.0, (255,255,255), 1 ,2)
        cv2.putText(final, ("512 units"), (posX, posY + 30), self.font, 1.0, (0,255,0), 1 ,2)
        cv2.putText(final, ("Fully Connected"), (posX, posY + 15), self.font, 1.0, (0,255,0), 1 ,2)

        with tf.variable_scope('ppo2_model/pi/fc1', reuse=tf.AUTO_REUSE) as conv_scope:
            hello = tf.get_variable('w', shape=[3136,512])
            weights0 = tf.transpose(hello, [1,0])
            weights = weights0.eval()
            x = posX
            y = posY + 40
            for channel in range(0,3):
                #print(channel)
                img = np.reshape(weights[channel,:], (56,56))
            
                '''
                for img_x in range(0,img.shape[0]):
                    for img_y in range(0,img.shape[1]):
                        if img[img_x, img_y] > 0:
                            img[img_x, img_y] = 255
                        else:
                            img[img_x, img_y] = 0
                '''
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                img2 = cv2.normalize(img,None,0,255,cv2.NORM_MINMAX)
                dim = (56*2,56*2)
                upscaled = cv2.resize(img2, dim, interpolation=cv2.INTER_NEAREST)

                #x = (channel % 3) * (56 * 4)
                #y = int(channel / 3) * (56 * 4)
                
                final[y:y+dim[1], x:x+dim[0]] = upscaled
                y+=dim[1] + 5

            #del hello
            #del weights0
            #del weights
            #del img
            #del img2
            #gc.collect()

        cv2.putText(final, ("[...]"), (posX, y + 40), self.font, 1.0, (0,255,0), 1 ,2)
        

    def DrawOutputLayer(self, final, posX, posY):
        cv2.putText(final, ("Output"), (posX, posY), self.font, 2.0, (255,255,255), 1 ,2)
        cv2.putText(final, ("36 Actions"), (posX, posY + 15), self.font, 1.0, (0,255,0), 1 ,2)
        #cv2.putText(final, ("Prob:%f" % self.action_prob), (posX, posY + 30), self.font, 1.0, (0,255,0), 1 ,2)
        for i in range(0,len(self.action_meaning)):
            color = (255,255,255)
            if self.action == i:
                color = (0,255,0)
            cv2.putText(final, ("%s" % self.action_meaning[i]), (posX, posY + i*8), self.font, 0.5, color, 1 ,2)

    
    def DrawInput(self, final, img, posX, posY, width, height):
        cv2.putText(final, ("INPUT"), (posX, posY), self.font, 1.0, (255,255,255), 2 ,2)
        cv2.putText(final, ("LAST 4"), (posX, posY + 15), self.font, 1.0, (0,255,0), 1 ,2)
        cv2.putText(final, ("FRAMES"), (posX, posY + 30), self.font, 1.0, (0, 255,0), 1 ,2)
        

        dim = (width,height)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        input = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
        #final[500:dim[1]+500,0:dim[0]] = input


        posY += 150
        for i in range(0,3):
            cv2.rectangle(final, (posX, posY), (posX + width, posY + height), (0,255,255), 1)
            posX += 2
            posY += 2

        imgPosX = posX
        imgPosY = posY
        final[imgPosY:imgPosY+dim[1],imgPosX:imgPosX+dim[0]] = input
        imgPosY += dim[1] + 50
        #cv2.putText(final, ("[...]"), (posX, imgPosY), self.font, 1.0, (0,255,0), 1 ,2)


        #posX += 2
        posY += height + 15
        cv2.putText(final, ("%dx%d" % (84, 84)), (posX, posY), self.font, 1.0, (0,255,0), 1 ,2)


    def DrawConv(self, final, posX, posY, width, height, name, numFilters, filterSize):
        cv2.putText(final, ("%s" % name), (posX, posY), self.font, 1.0, (255,255,255), 1 ,2)
        posY += 15
        cv2.putText(final, ("%d FILTERS" % (numFilters)), (posX, posY), self.font, 1.0, (0,255,0), 1 ,2)
        
        posY += 150
        for i in range(0,8):
            cv2.rectangle(final, (posX, posY), (posX + width, posY + height), (0,0,255), 1)
            posX += 2
            posY += 2

        posX += int(width / 4)
        posY += int(height / 2)

        cv2.putText(final, ("%dx%d" % (filterSize, filterSize)), (posX, posY), self.font, 1.0, (0,255,0), 1 ,2)

    
    def DrawFC(self, final, posX, posY, width, height, name, numUnits):
        posX += 30

        cv2.putText(final, ("%s" % name), (posX, posY), self.font, 1.0, (255,255,255), 1 ,2)
        posY += 15
        cv2.putText(final, ("%d Units" % (numUnits)), (posX, posY), self.font, 1.0, (0,255,0), 1 ,2)
        posY += 45
        cv2.rectangle(final, (posX, posY), (posX + width, posY + height), (0,0,255), 1)


        posX += int(width / 2)
        posY += 20
        for i in range(0,16):
            cv2.circle(final, (posX, posY), 7, (0,255,0), -1)
            posY += 20

        posX -= int(width / 2)
        #posY += 10
        cv2.putText(final, ("[...]"), (posX, posY), self.font, 1.0, (0,255,0), 1 ,2)

    def DrawOutput(self, final, posX, posY, width, height):
        cv2.putText(final, ("OUTPUT"), (posX, posY), self.font, 1.0, (255,255,255), 2 ,2)
        posY += 15
        cv2.putText(final, ("%d ACTIONS" % len(self.action_meaning)), (posX, posY), self.font, 1.0, (0,255,0), 1 ,2)
        posY += 15
        cv2.putText(final, "PROBABILITIES", (posX, posY), self.font, 1.0, (0,255,0), 1 ,2)
        #posY += 15
        #cv2.rectangle(final, (posX, posY), (posX + width, posY + height), (0,0,255), 1)

        #for i in range(0,len(self.action_meaning)):
        #    color = (255,255,255)
        #    if self.action == i:
        #        color = (0,255,0)
        #    cv2.putText(final, ("%s" % self.action_meaning[i]), (posX, posY + i*8), self.font, 0.5, color, 1 ,2)

        posX -= 60
        posY += 140
        self.clear_screen(final, posX, posY-15, 240, 90, (0,0,0))
        cv2.putText(final, ("CHOSEN ACTION:"), (posX, posY), self.font, 1.0, (255,255,255), 1 ,2)
        posY += 15
        cv2.putText(final, ("%d: %s" % (self.action, self.action_meaning[self.action])), (posX, posY), self.font, 1.0, (255,255,255), 1 ,2)
        posY += 30
        cv2.putText(final, ("LOG PROBABILITY:"), (posX, posY), self.font, 1.0, (255,255,255), 1 ,2)
        posY += 15
        cv2.putText(final, ("%f" % self.action_prob), (posX, posY), self.font, 1.0, (255,255,255), 1 ,2)

    
    def Draw(self, final, img, posX, posY):


        self.DrawInput(final, img, posX, posY, 84, 84)
        posX += 100
        self.DrawConv(final, posX, posY, 75, 75, 'CONV 1', 32, 8)
        posX += 100
        self.DrawConv(final, posX, posY, 75, 75, 'CONV 2', 64, 4)
        posX += 100
        self.DrawConv(final, posX, posY, 75, 75, 'CONV 3', 64, 3)
        posX += 100
        self.DrawFC(final, posX, posY, 25, 350, 'FC 1', 512)
        posX += 150
        self.DrawOutput(final, posX, posY, 25, 100)



    """
        #Input layer
        self.DrawInputLayer(final, img, posX, posY)


        if self.UpdateNeuralNetFrameCount == 0:
            #Conv net layer 1
            self.DrawConvNetLayer(final, posX + 150, posY, 32, 8, "Conv Layer 1", 'ppo2_model/pi/c1',4)

            #Conv net layer 2
            self.DrawConvNetLayer(final, posX + 300, posY, 64, 4, "Conv Layer 2", 'ppo2_model/pi/c2',32)
        
            #Conv net layer 3
            self.DrawConvNetLayer(final, posX + 450, posY, 64, 3, "Conv Layer 3", 'ppo2_model/pi/c3',64)
        
            #Hidden layer
            self.DrawHiddenLayer(final, posX + 600, posY)

            print('UPDATE CONV NETS!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            self.UpdateNeuralNetFrameCount = 4000

        
        #Output layer
        self.DrawOutputLayer(final, posX + 750, posY)

        #Draw Enclosing Rectangle
        #cv2.rectangle(final, (posX-10, posY), (700, 800), (0,255,0), 2)
    

        self.UpdateNeuralNetFrameCount -= 1
    """
