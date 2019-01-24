# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 11:44:22 2019

@author: Biswajit
"""

import tensorflow as tf
import numpy as np
from Generator import Generator
from Discriminator import Discriminator
from HelperFunc import loss
import matplotlib.pyplot as plt
from HelperFunc import get_next_batch
class DCGAN:
    
    
    def __init__(self,img_shape, d_lr=.0001, g_lr=.0004, z_shape=100, number_of_iter=1000, batch_size=1000, epochs=1000):
        self.d_lr = d_lr
        self.g_lr = g_lr
        self.number_of_iter = number_of_iter
        self.batch_size = batch_size
        self.generator = Generator(img_shape,z_shape)
        self.discriminator = Discriminator(img_shape)
        self.z_shape = z_shape
        self.epochs = epochs
        self.rows,self.cols,self.channels = img_shape
        
        mnist = tf.keras.datasets.mnist
        (x_train, y_train), (x_test, y_test)=mnist.load_data(path="mnist.npz")
        
        x_train = x_train.reshape(60000, 784)
        x_test = x_test.reshape(10000, 784)
        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        
        x_train /= 255
        x_test /= 255
        y_train = tf.keras.utils.to_categorical(y_train,10)
        y_test = tf.keras.utils.to_categorical(y_test,10)
        
        self.x_data = np.concatenate((x_train,x_test),axis=0)
        self.y_data = np.concatenate((y_train,y_test),axis=0)
        
        print("Train matrix shape", self.x_data.shape)
        
        self.phX = tf.placeholder(tf.float32,[None,784])
        self.phY = tf.placeholder(tf.float32,[None,10])
        self.phZ = tf.placeholder(tf.float32,[None,self.z_shape])
        
        self.generator_output = self.generator.generatorFn(self.phZ,self.phY)
        
        D_output_fake, D_logits_fake = self.discriminator.discriminatorFn(self.generator_output,self.phY)
        D_output_real, D_logits_real = self.discriminator.discriminatorFn(self.phX,self.phY,reuse=True)
        
        
        D_loss_fake = loss(tf.zeros_like(D_logits_fake),D_logits_fake)
        D_loss_real = loss(tf.ones_like(D_logits_real),D_logits_real)
        
        self.D_loss = tf.add(D_loss_real,D_loss_fake)
        self.G_loss = loss(tf.ones_like(D_logits_fake),D_logits_fake)
        
        tvars = tf.trainable_variables()
        
        self.gvars = [var for var in tvars if "gen" in var.name]
        self.dvars = [var for var in tvars if "dis" in var.name]
        
        self.train_gen = tf.train.AdamOptimizer(g_lr).minimize(self.G_loss,var_list=self.gvars)
        self.train_dis = tf.train.AdamOptimizer(d_lr).minimize(self.D_loss,var_list=self.dvars)
        
        
    def train(self):
        init = tf.global_variables_initializer()
        cfg = tf.ConfigProto(allow_soft_placement=True )
        cfg.gpu_options.allow_growth = True
        self.sess = tf.Session(config=cfg)
        self.sess.run(init)
        saver = tf.train.Saver(var_list=self.gvars)
        
        for i in range(self.epochs):
        
            _,train_gen_batch_y = get_next_batch(self.x_data,self.y_data,self.batch_size)
            train_gen_batch_z = np.random.uniform(-1, 1, (self.batch_size, self.z_shape))
            g_loss,_=self.sess.run([self.G_loss,self.train_gen],feed_dict={self.phZ:train_gen_batch_z, self.phY:train_gen_batch_y})

            train_dis_batch_x,train_dis_batch_y = get_next_batch(self.x_data,self.y_data,self.batch_size)
            train_dis_batch_z = np.random.uniform(-1, 1, (self.batch_size, self.z_shape))
            d_loss,_=self.sess.run([self.D_loss,self.train_dis],feed_dict={self.phX:train_dis_batch_x, self.phY:train_dis_batch_y,self.phZ:train_dis_batch_z})            
            
            if i%100 == 0:
                print("Epoch: {} Discriminator loss: {} Generator loss: {}".format(i,d_loss,g_loss))   
        saver.save(self.sess, './models/10000_epoch_model.ckpt')
        
        
    def test(self):
        init = tf.global_variables_initializer()
        cfg = tf.ConfigProto(allow_soft_placement=True )
        cfg.gpu_options.allow_growth = True
        self.sess = tf.Session(config=cfg)
        self.sess.run(init)
        saver = tf.train.Saver(var_list=self.gvars)
        saver.restore(self.sess,'./models/10000_epoch_model.ckpt')
        
        for i in range(10):
            new_samples=[]
            y_val=np.zeros([1,10])
            y_val[0][i]=1
            plt.subplots(figsize=(15,15))
            for j in range(5):
                sample_z = np.random.uniform(-1,1,size=(1,100))
                gen_sample = self.sess.run(self.generator.generatorFn(self.phZ,self.phY,reuse=True),feed_dict={self.phZ:sample_z,self.phY:y_val})
                new_samples.append(gen_sample*255)
                plt.subplot(10,5,i*5+j+1)
                plt.imshow(new_samples[j].reshape(28,28),cmap='Greys')
        
                
if __name__ == '__main__':
    
    tf.reset_default_graph()
    img_shape = (28, 28, 1)
    epochs = 10000
    dcgan = DCGAN(img_shape, epochs=epochs)
    '''   TRAIN '''
    
    dcgan.train()
            
    ''' TEST '''
    dcgan.test()