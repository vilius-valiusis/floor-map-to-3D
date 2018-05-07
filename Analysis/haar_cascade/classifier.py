
import cv2


def find_objects(img, classifier, scale_factor, min_neighbors):
    objects = classifier.detectMultiScale(img, scaleFactor=scale_factor, minNeighbors=min_neighbors)
    return objects


def draw_bounding_rectangles(img, objects):
    img_copy = img.copy()
    for (x, y, w, h) in objects:
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return img_copy
