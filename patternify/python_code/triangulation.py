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

def point_on_triangle(pt1, pt2, pt3):
    """
    Random point on the triangle with vertices pt1, pt2 and pt3.
    """
    s, t = sorted([random.random(), random.random()])
    return (s * pt1[0] + (t-s)*pt2[0] + (1-t)*pt3[0],
            s * pt1[1] + (t-s)*pt2[1] + (1-t)*pt3[1])

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


def fix_image(img):
    # flip image vertically
    img = cv2.flip(img, 0)

    # flip image horizontally
    img = cv2.flip(img, 1)

    # transpose image
    img = cv2.transpose(img)

    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    return img

# end of the function

resize_size = 600
linewidth_var = 0.5
noise_amount = 400

img = cv2.imread('input.jpg',-1)
img_bw = cv2.imread('input.jpg',0)

img = fix_image(img)
img_bw = fix_image(img_bw)

resized_fc_image = image_resize(img, resize_size)

#split into chanels
b,g,r = cv2.split(resized_fc_image)

#resize splits
resized_image_b = b
resized_image_g = g
resized_image_r = r

#resize
find_lines_low_treshold = 150
find_lines_high_treshold = 200

resized_image = image_resize(img_bw, resize_size)

only_lines_image = cv2.Canny(resized_image, find_lines_low_treshold , find_lines_high_treshold)

#ans will be an array to store points
ans = []
for y in range(0, only_lines_image.shape[0]):
     for x in range(0, only_lines_image.shape[1]):
            if only_lines_image[y, x] != 0:
                ans = ans + [[x, y]]

height, width  = resized_image.shape
output_size_x = 15
ratio = output_size_x/float(width)
output_size_y = int(float(width) * ratio)

#append noise to array
n=int(noise_amount)

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

# print resized_image.shape
# print resized_image_r.shape
# print resized_image_g.shape
# print resized_image_b.shape
# print points[tri.simplices].shape
# print 'this'
# print width
# print height

for i in range(len(tri.simplices)):

    pt1 = points[tri.simplices[i,:][0]]
    pt2 = points[tri.simplices[i,:][1]]
    pt3 = points[tri.simplices[i,:][2]]

    #get 3 random points in the triangle and get their avarage

    point_1_x = int(point_on_triangle(pt1, pt2, pt3)[0])
    point_1_y = int(point_on_triangle(pt1, pt2, pt3)[1])

    point_2_x = int(point_on_triangle(pt1, pt2, pt3)[0])
    point_2_y = int(point_on_triangle(pt1, pt2, pt3)[1])

    point_3_x = int(point_on_triangle(pt1, pt2, pt3)[0])
    point_3_y = int(point_on_triangle(pt1, pt2, pt3)[1])

    point_x_final = int(float(point_1_x + point_2_x + point_3_x) / 3)
    point_y_final = int(float(point_1_y + point_2_y + point_3_y) / 3)

    b_val = (resized_image_b[point_y_final, point_x_final])
    g_val = (resized_image_g[point_y_final, point_x_final])
    r_val = (resized_image_r[point_y_final, point_x_final])

    b_val = map_value_to_range(b_val, 0, 255, 0 , 1)
    g_val = map_value_to_range(g_val, 0, 255, 0 , 1)
    r_val = map_value_to_range(r_val, 0, 255, 0 , 1)

    # polygon = Polygon(np.array(points[tri.simplices[i,:]]), True, facecolor='white', linewidth=linewidth_var, edgecolor='r')

    polygon = Polygon(np.array(points[tri.simplices[i,:]]), True, facecolor=(r_val, g_val, b_val), linewidth=linewidth_var, edgecolor=(r_val, g_val, b_val))
    patches.append(polygon)
    printing_patches.append(points[tri.simplices[i,:]])


fig = plt.figure()

p = PatchCollection(patches, alpha=1.0, match_original=True)

ax = plt.Axes(fig, [0., 0., 1., 1.])

ax.set_axis_off()

ax.add_collection(p)

fig.add_axes(ax)

fig.set_size_inches(output_size_x, output_size_y)

plt.axis('equal')

# plt.subplots_adjust(left=0.1, right=0.2, top=0.2, bottom=0.1)

plt.savefig('foo.jpg', dpi=70, bbox_inches='tight', pad_inches = 0)
