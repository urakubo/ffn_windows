import os
filename  = 'seg-0_0_0.npz'
outputdir = os.getcwd()  + os.sep + 'inferred_segmentation'
inputdir  = os.getcwd()


import numpy as np
import h5py

import PIL
import PIL.Image
import cv2
import png


def save_tif8(id_data, filename):
    cv2.imwrite(filename, id_data.astype('uint8'))

def save_tifc(id_data, filename, colordata):
    pilOUT = gen_col_pil(id_data, colordata)
    pilOUT.save(filename)

def save_png16(id_data, filename):
    # Use pypng to write zgray as a grayscale PNG.
    with open(filename, 'wb') as f:
        writer = png.Writer(width=id_data.shape[1], height=id_data.shape[0], bitdepth=16, greyscale=True)
        id_data_list = id_data.astype('uint16').tolist()
        writer.write(f, id_data_list)

def save_png8(id_data, filename):
    # Use pypng to write zgray as a grayscale PNG.
    with open(filename, 'wb') as f:
        writer = png.Writer(width=id_data.shape[1], height=id_data.shape[0], bitdepth=8, greyscale=True)
        id_data_list = id_data.astype('uint8').tolist()
        writer.write(f, id_data_list)

def save_pngc(id_data, filename, colordata):
    pilOUT = gen_col_pil(id_data, colordata)
    pilOUT.save(filename)

def save_npy(id_data, filename):
    np.save(filename, id_data)


inputdir  = os.getcwd()


data = np.load(inputdir+ os.sep+filename)
# print data.files
# print data['segmentation'].shape

num_z = data['segmentation'].shape[0]
num_y = data['segmentation'].shape[1]
num_x = data['segmentation'].shape[2]

for idz in range(num_z):
    tmp = outputdir + os.sep + 'z' + '%04d' % (idz) + '.png'
    save_png8(data['segmentation'][idz,:,:].transpose(), tmp)

