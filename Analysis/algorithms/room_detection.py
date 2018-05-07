import numpy as np

import cv2


def extract_rooms(closed_wall_image):
    gray_img = closed_wall_image.copy()
    color_img = cv2.cvtColor(closed_wall_image, cv2.COLOR_GRAY2RGB)

    dist_transform = cv2.distanceTransform(gray_img, cv2.DIST_L2, 3)
    ret, sure_fg = cv2.threshold(dist_transform, 0.1 * dist_transform.max(), 255, 0)

    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(gray_img, sure_fg)
    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1
    # Now, mark the region of unknown with zero
    markers[unknown == 255] = 0
    markers = markers.astype('int32')

    markers = cv2.watershed(color_img, markers)
    canvas = np.zeros(color_img.shape, np.uint8)

    canvas[markers == -1] = [255, 0, 0]

    return canvas,markers

