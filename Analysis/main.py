import matplotlib.pyplot as plt
from algorithms import wall_analysis, morphological as morph, room_detection as rd
import cv2
import json
import numpy as np
import haar_cascade.classifier as cls

image_outer_walls = []
image_outer_walls_closed = []
image_outer_walls_contours = []

image_inner_walls = []
image_inner_walls_closed = []
image_inner_walls_contours = []

image_inner_outer_walls = []

outer_wall_contours = []
outer_wall_corners = []
outer_wall_closure_areas = []

inner_wall_contours = []
inner_wall_corners = []
inner_wall_closure_areas = []


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


def export_json_list(walls, file_name):
    file = open(file_name+'.json', 'w')
    file.write(json.dumps(walls, cls=MyEncoder))
    file.close()


def show_images(img1, img2):
    plt.subplot(121), plt.imshow(img1)
    plt.subplot(122), plt.imshow(img2)
    plt.show()


def show_image(img1):
    plt.imshow(img1, cmap='gray')
    plt.show()


def extract_outer_wall_image(thresh_img):
    return morph.morph_operation(thresh_img, 8, 8, 8)


def extract_inner_outer_walls(thresh_img):
    return morph.morph_operation(thresh_img, 3, 3, 3)


def extract_inner_wall_image(thresh_img):
    outer = extract_outer_wall_image(thresh_img)
    inner = extract_inner_outer_walls(thresh_img)
    inner_only = cv2.subtract(outer, inner)
    cv2.bitwise_not(inner_only, inner_only)
    return inner_only


def extract_outer_wall_closure_areas():
    return wall_analysis.extract_closure_areas(image_outer_walls_contours, outer_wall_contours, 'outer')


def extract_inner_wall_closure_areas(door_objects):
    return wall_analysis.extract_closure_areas(image_inner_walls_contours, inner_wall_contours, door_objects, 'inner')


def extract_wall_contours(image):
    return wall_analysis.extract_wall_contours(image)


def extract_corners(contours_image, contours):
    return wall_analysis.extract_corners_from_contours(contours_image, contours)


if __name__ == "__main__":
    # Read in the image as a gray scale image
    img = cv2.imread("floor_maps//test1.jpg", 0)

    # Binerise the image
    ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Segment inner and outer walls
    image_outer_walls = extract_outer_wall_image(thresh)
    image_inner_walls = extract_inner_wall_image(thresh)
    image_inner_outer_walls = extract_inner_outer_walls(thresh)

    # Find inner and outer wall contours
    outer_wall_contours, image_outer_walls_contours = extract_wall_contours(image_outer_walls)
    inner_wall_contours, image_inner_walls_contours = extract_wall_contours(image_inner_walls)

    # Find inner and outer wall corners
    outer_wall_corners = extract_corners(image_outer_walls_contours, outer_wall_contours)
    inner_wall_corners = extract_corners(image_inner_walls_contours, inner_wall_contours)

    # Find outer wall closure areas
    outer_wall_closure_areas = extract_outer_wall_closure_areas()

    # Find inner wall closure areas
    door_cascade = cv2.CascadeClassifier('haar_cascade//door_classifier_40x40.xml')
    door_objects = cls.find_objects(img, door_cascade, 5, 1)
    inner_wall_closure_areas = extract_inner_wall_closure_areas(door_objects)

    # Close inner and outer areas
    wall_analysis.draw_closure_areas(image_inner_outer_walls, outer_wall_closure_areas)
    wall_analysis.draw_closure_areas(image_inner_outer_walls, inner_wall_closure_areas)

    # Extract room contours
    extracted_rooms_contours, markers = rd.extract_rooms(image_inner_outer_walls)

    # Append inner and outer walls to one array
    for val in inner_wall_corners:
        outer_wall_corners.append(val)

    # Export values as JSON
    export_json_list(inner_wall_closure_areas, "output/doors")
    export_json_list(outer_wall_closure_areas, "output/windows")
    export_json_list(outer_wall_corners, "output/walls")


