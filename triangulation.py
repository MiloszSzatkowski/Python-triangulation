#!/usr/bin/python

import cv2
import numpy as np
import random
from scipy.spatial import Delaunay
import pickle as pickle
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

#############################################

def map_value_to_range (value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    return resized


# end of the function

resize_size = 400

img = cv2.imread('input.jpg',-1)
img_bw = cv2.imread('input.jpg',0)

#split into chanels
b,g,r = cv2.split(img);

#resize splits
resized_image_b = cv2.flip(image_resize(b, resize_size),0)
resized_image_g = cv2.flip(image_resize(g, resize_size),0)
resized_image_r = cv2.flip(image_resize(r, resize_size),0)

#resize
find_lines_low_treshold = 150
find_lines_high_treshold = 200

resized_image = cv2.flip(image_resize(img_bw, resize_size),0)
only_lines_image = cv2.Canny(resized_image, find_lines_low_treshold , find_lines_high_treshold)

#ans will be an array to store points
ans = []
for y in range(0, only_lines_image.shape[0]):
     for x in range(0, only_lines_image.shape[1]):
            if only_lines_image[y, x] != 0:
                ans = ans + [[x, y]]

height, width = resized_image.shape

#append noise to array
n=int(2)

for j in range(n):
       ans.append([random.randint(1,width),random.randint(1,height)])

#append corners
ans.append([0,0])
ans.append([0,height])
ans.append([width, height])
ans.append([width, 0])

#slice array - that simplifies a picture
##ans = np.array(ans)[::2]

##print ans - print a finished arrays

points = np.array(ans)

tri = Delaunay(points)

patches = []
printing_patches = []

# triangles in a form of [xy, xy, xy]  - points[tri.simplices[index,:]]

for i in range(len(tri.simplices)):

    # find the center of a triangle to extract a colour of a point from the original picture (and fill the polygon later on)
    centerX =  int((float(points[tri.simplices[i,:][0]][0]) + float(points[tri.simplices[i,:][1]][0]) + float(points[tri.simplices[i,:][2]][0])) / 3.0)
    centerY =  int((float(points[tri.simplices[i,:][1]][1]) + float(points[tri.simplices[i,:][1]][1]) + float(points[tri.simplices[i,:][2]][1])) / 3.0)

    center = [centerX,centerY]

    b_val = (resized_image_b[centerX, centerY])
    g_val = (resized_image_g[centerX, centerY])
    r_val = (resized_image_r[centerX, centerY])

    b_val = map_value_to_range(b_val, 0, 255, 0 , 1)
    g_val = map_value_to_range(g_val, 0, 255, 0 , 1)
    r_val = map_value_to_range(r_val, 0, 255, 0 , 1)

    polygon = Polygon(np.array(points[tri.simplices[i,:]]), True, color=(b_val, g_val, r_val))
    patches.append(polygon)
    printing_patches.append(points[tri.simplices[i,:]])

fig,ax = plt.subplots(1)

p = PatchCollection(patches, alpha=1.0, linewidth=0.0, edgecolor='grey', match_original=True)
ax.add_collection(p)

plt.axis('equal')
plt.show()

# print printing_patches

# print len(center)
# print center[0]

# cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [ 'black' , 'white'])
# plt.tripcolor(points[:,0], points[:,1], tri.simplices.copy(), facecolors=np.array(center), edgecolors='grey', lw=0.1, cmap=cmap)
# plt.trip(points[:,0], points[:,1], tri.simplices.copy(), facecolors=np.array(center), edgecolors='grey', lw=0.1)

#plt.triplot(points[:,0], points[:,1], tri.simplices.copy(), patch_artist=True)
#plt.plot(points[:,0], points[:,1], 'o')

#
# ##plt.colorbar()
#
#
# plt.show()
