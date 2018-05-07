import cv2

defaultKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))


def morph_operation(img, erosion_iter=0, opening_iter=0, dilation_iter=0, kernel=defaultKernel):
    erosion = cv2.dilate(img, kernel, iterations=erosion_iter)
    opening = cv2.morphologyEx(erosion, cv2.MORPH_OPEN, kernel, iterations=opening_iter)
    dilation = cv2.erode(opening, kernel, iterations=dilation_iter)
    return dilation
