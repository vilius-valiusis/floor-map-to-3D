import cv2
import numpy as np
import matplotlib.pyplot as plt

# Distance between corners that is define weather the corners
# are to be considered to be on the same line.
PIX_RANGE = 5
INNER_WALL_PIX_RANGE = 10
wall_contours = []
wall_contour_images = []
wall_closure_areas = []


##################################################
# Show image for test purposes
##################################################
def show_images(img):
    plt.imshow(img, cmap='gray')
    plt.show()


##################################################
# Draws a contour on a blank canvas
##################################################
def draw_wall_contour(img, contour):
    canvas = np.zeros(img.shape, np.uint8)
    cv2.drawContours(canvas, contour, -1, (123, 125, 245), 1)
    return canvas


##################################################
# Extract wall contours from the provided image
##################################################
def extract_wall_contours(img):
    canvas = np.zeros(img.shape, np.uint8)
    im2, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canvas, contours, -1, (123, 125, 245), 1)
    return contours, canvas


############################################################################################
# Uses Harris algorithm to detect corners on the provided image.
# Each corner is then detected and roundedc
############################################################################################
def extract_wall_corners_sub(img):
    gray = np.float32(img)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)
    dst = cv2.dilate(dst, None)
    ret, dst = cv2.threshold(dst, 0.001 * dst.max(), 255, 0)
    dst = np.uint8(dst)

    # find centroids
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

    # for corner in np.int0(centroids):
    #     x, y = corner
    #     cv2.circle(img, (x, y), 2, 255, -1)
    # show_images(img)
    return img, np.int0(centroids)


############################################################################################
# Helper function to check if a pixel is within a range of another pixel, using the maximum
# pixel variance e.g. PIX_RANGE
############################################################################################
def is_in_range(a, b):
    return a + PIX_RANGE > b > a - PIX_RANGE


############################################################################################
# Checks for the direction of the corner
# So if a corner is 'L' shaped it will return top = True and right = True
############################################################################################
def check_direction(corner, contour_img):
    top, right, bottom, left = False, False, False, False
    y, x = corner

    for i, v in enumerate(reversed(contour_img[x][:y])):
        if 4 < i < 8:
            for r in range(-5, 5):
                if contour_img[x + r][y - i] == 123:
                    left = True
                if contour_img[x + r][y + i] == 123:
                    right = True
                if contour_img[x + i][y + r] == 123:
                    bottom = True
                if contour_img[x - i][y + r] == 123:
                    top = True

    return top, right, bottom, left


############################################################################################
# Finds the next direction/axis the corner should be on depending on the previous corners.
# Requires minimum of two sequential corners.
# 0 = top, 1 = right, 2 = bottom, 3 = left
############################################################################################
def get_next_direction(corners, contour_img, last_direction):
    current_corner = corners[-1]
    last_corner = corners[-2]
    t1, r1, b1, l1 = check_direction(last_corner, contour_img)
    t2, r2, b2, l2 = check_direction(current_corner, contour_img)
    if (t1 and b2) and (t2 and b1) and is_in_range(current_corner[0], last_corner[0]):
        return last_direction

    if (t1 and b2) and is_in_range(current_corner[0], last_corner[0]):
        if t2:
            return 0
        if r2:
            return 1
        if l2:
            return 3

    if (t2 and b1) and is_in_range(current_corner[0], last_corner[0]):
        if r2:
            return 1
        if b2:
            return 2
        if l2:
            return 3

    if (r1 and l2) and (r2 and l1) and is_in_range(current_corner[1], last_corner[1]):
        return last_direction

    if (r1 and l2) and is_in_range(current_corner[1], last_corner[1]):
        if t2:
            return 0
        if r2:
            return 1
        if b2:
            return 2

    if (r2 and l1) and is_in_range(current_corner[1], last_corner[1]):
        if t2:
            return 0
        if b2:
            return 2
        if l2:
            return 3


################################################################
# Walk the shortest distance from x->x or y->y on the same line
################################################################
def walk_shortest_corners(corners, contour_img):
    rearranged_corners = []
    last_direction = 0
    for i1, corner1 in enumerate(corners):
        y1, x1 = corner1
        if i1 == 0:
            continue
        elif i1 == 1 or i1 == 2:
            rearranged_corners.append((y1, x1))
        else:
            # x-current, x-last, y-current, y-last
            xc, xl, yc, yl = (0, 0), (0, 0), (0, 0), (0, 0)
            last_added = rearranged_corners[-1]
            next_direction = get_next_direction(rearranged_corners, contour_img, last_direction)

            # Loop through all the corners to find the next one
            for i2, corner2 in enumerate(corners):
                y2, x2 = corner2
                # If a corner was previously added
                if i2 == 0 or (y2, x2) in rearranged_corners:
                    continue
                # Filters any values that do no follow the direction of the contour
                # from the previous corner.
                if next_direction == 0:
                    if last_added[1] < x2:
                        continue
                if next_direction == 1:
                    if last_added[0] > y2:
                        continue
                if next_direction == 2:
                    if last_added[1] > x2:
                        continue
                if next_direction == 3:
                    if last_added[0] < y2:
                        continue

                # Checks if y coordinate is in range of the last added corner
                # If it is it will try to find the smallest/largest possible value
                # depending on the direction 2 = down, 0 = up
                if is_in_range(y2, last_added[0]):
                    if next_direction == 2:
                        if yc[1] <= yl[1]:
                            yl = yc
                            yc = (y2, x2)
                    if next_direction == 0:
                        if yc[1] >= yl[1]:
                            yl = yc
                            yc = (y2, x2)
                # Checks if x coordinate is in range of the last added corner
                # If it is it will try to find the smallest/largest possible value
                # depending on the direction 1 = right, 3 = left
                if is_in_range(x2, last_added[1]):
                    if next_direction == 1:
                        if xc[0] <= xl[0]:
                            xl = xc
                            xc = (y2, x2)
                    if next_direction == 3:
                        if xc[0] >= xl[0]:
                            xl = xc
                            xc = (y2, x2)

            # Add value to corner array
            if yc == (0, 0) and xc != (0, 0):
                rearranged_corners.append(xc)
                last_direction = next_direction
            elif xc == (0, 0) and yc != (0, 0):
                rearranged_corners.append(yc)
                last_direction = next_direction

    return readjust_corner_coordinates(rearranged_corners)


##############################################################################
# Due some corner pixel on the same line may vary
# This step is done to offset this variance by following the previous line
##############################################################################
def readjust_corner_coordinates(corners):
    new_corners = []
    for i, corner in enumerate(corners):
        x, y = corner
        if i == 0:
            new_corners.append(corner)
            continue
        elif is_in_range(x, corners[i - 1][0]):
            new_corners.append((corners[i - 1][0], y))
        elif is_in_range(y, corners[i - 1][1]):
            new_corners.append((x, corners[i - 1][1]))
    return new_corners


#################################################################################
# Checks for illegal structures such as ones that contain coordinates like (1,1)
#################################################################################
def is_wall_a_legal_structure(corners):
    for corner in corners:
        x, y = corner
        if x == 1 or y == 1:
            return False
    return True


def is_corner_pair_usable(c1: tuple, c2: tuple, axis):
    # axis = x = 0, y = 1
    if c1[1] and c1[2] and c2[2] and c2[3] and axis == 1:
        return True
    elif c1[3] and c1[2] and c2[0] and c2[3] and axis == 0:
        return True
    elif c1[3] and c1[0] and c2[0] and c2[1] and axis == 1:
        return True
    elif c1[1] and c1[2] and c2[0] and c2[1] and axis == 0:
        return True
    else:
        return False


def find_distance_between_corners(c1, c2):
    if is_in_range(c1[0], c2[0]):
        return abs(c1[1] - c2[1])
    else:
        return abs(c1[0] - c2[0])


def find_shortest_pairs(corner_pairs, limit):
    if limit != 0:
        sorted_cps = sorted(corner_pairs, key=lambda corner_pair: corner_pair[1])[:limit]
    else:
        sorted_cps = sorted(corner_pairs, key=lambda corner_pair: corner_pair[1])
    return sorted_cps


def find_viable_corner_pairs(wall, contour_img):
    corner_pairs = []
    for corner in wall:
        x, y = corner
        t1, r1, b1, l1 = check_direction(corner, contour_img)
        corners1 = (t1, r1, b1, l1)
        for corner2 in wall:
            x2, y2 = corner2
            x_in_range = is_in_range(x, x2)
            y_in_range = is_in_range(y, y2)
            if x_in_range or y_in_range:
                t2, r2, b2, l2 = check_direction(corner2, contour_img)
                corners2 = (t2, r2, b2, l2)
                axis = 0 if x_in_range else 1
                # print(corner, corner2, is_corner_pair_usable(corners1, corners2, axis))
                if is_corner_pair_usable(corners1, corners2, axis):

                    distance = find_distance_between_corners((x, y), (x2, y2))
                    # print(corner, corner2, distance)
                    corner_pairs.append((((x, y), (x2, y2)), distance, axis))
    return corner_pairs


def find_outer_wall_closure_areas(corner_pairs):
    closure_areas = []
    closest_corner = ((0, 0), (0, 0)), 0
    # Corner_pair contains an array of x2 consisting of 2 corners of a wall, distance and the axis
    # axis 0=x, 1=y
    # Loop through all corner pairs
    for i, cpd in enumerate(corner_pairs):
        for cp in cpd:

            for ii, cpd2 in enumerate(corner_pairs):
                for cp2 in cpd2:
                    # If corners are on the same axis AND and have the same width or height AND are not the same corners
                    if cp[2] == cp2[2] and is_in_range(cp[1], cp2[1]) and cp != cp2:
                        if i == ii:
                            continue
                        # If corner is on x axis AND
                        if cp[2] == 0:

                            if is_in_range(cp[0][0][1], cp2[0][0][1]):
                                distance = find_distance_between_corners(cp[0][0], cp2[0][0])
                            elif is_in_range(cp[0][0][1], cp2[0][1][1]):
                                distance = find_distance_between_corners(cp[0][0], cp2[0][1])

                            if distance < closest_corner[1] or closest_corner[1] == 0:
                                closest_corner = ((cp2[0][0], cp2[0][1]), distance)

                        elif cp[2] == 1:

                            if is_in_range(cp[0][0][0], cp2[0][0][0]):
                                distance = find_distance_between_corners(cp[0][0], cp2[0][0])
                            elif is_in_range(cp[0][0][0], cp2[0][1][0]):
                                distance = find_distance_between_corners(cp[0][0], cp2[0][1])

                            if distance < closest_corner[1] or closest_corner[1] == 0:
                                closest_corner = ((cp2[0][0], cp2[0][1]), distance)

            closure_areas.append([cp[0][0], cp[0][1], closest_corner[0][0], closest_corner[0][1]])
            closest_corner = ((0, 0), (0, 0)), 0
            remove_duplicate_closure_areas(closure_areas)
    return closure_areas


def find_inner_wall_closure_areas(found_objects, corner_pairs):
    viable_closure_pairs = []
    for obj in found_objects:
        x, y, w, h = obj
        min_coord = (x-PIX_RANGE, y-PIX_RANGE)
        max_coord = (x+w+PIX_RANGE, y+h+PIX_RANGE)
        areas = []
        for cpd in corner_pairs:
            for cps in cpd:
                for cp in cps[0]:
                    if cp[0] >= min_coord[0] and cp[1] >= min_coord[1] and cp[0] <= max_coord[0] and cp[1] <= max_coord[1]\
                            and cps[1] < w:

                        if [(cps[0][0], cps[0][1]), cps[1], cps[2]] not in areas \
                                and [(cps[0][1], cps[0][0]), cps[1], cps[2]] not in areas:
                            areas.append([cps[0], cps[1], cps[2]])

        if 2 <= len(areas):
            viable_closure_pairs.append(areas)

    closure_areas = []
    closest_corner = ((0, 0), (0, 0)), 0

    for i, pairs1 in enumerate(viable_closure_pairs):
        for pair1 in pairs1:

            for ii, pair2 in enumerate(viable_closure_pairs[i]):
                if is_in_range(pair1[1], pair2[1]) and pair1[2] == pair2[2] and pair1 != pair2:

                    if pair1[2] == 0:
                        if is_in_range(pair1[0][0][1], pair2[0][0][1]):
                            distance = find_distance_between_corners(pair1[0][0], pair2[0][0])
                        elif is_in_range(pair1[0][0][1], pair2[0][1][1]):
                            distance = find_distance_between_corners(pair1[0][0], pair2[0][1])

                        if distance < closest_corner[1] or closest_corner[1] == 0:
                            closest_corner = ((pair2[0][0], pair2[0][1]), distance)

                    elif pair1[2] == 1:
                        if is_in_range(pair1[0][0][0], pair2[0][0][0]):
                            distance = find_distance_between_corners(pair1[0][0], pair2[0][0])
                        elif is_in_range(pair1[0][0][0], pair2[0][1][0]):
                            distance = find_distance_between_corners(pair1[0][0], pair2[0][1])

                        if distance < closest_corner[1] or closest_corner[1] == 0:
                            closest_corner = ((pair2[0][0], pair2[0][1]), distance)

                    closure_areas.append([pair1[0][0], pair1[0][1], closest_corner[0][0], closest_corner[0][1]])
                    closest_corner = ((0, 0), (0, 0)), 0
                    remove_duplicate_closure_areas(closure_areas)

    return closure_areas


def remove_duplicate_closure_areas(closure_areas):
    for area in closure_areas:
        for area2 in closure_areas:
            if area[0] in area2 and area != area2:
                closure_areas.remove(area2)


def draw_closure_areas(img, closure_areas):
    for area in closure_areas:
        if is_in_range(area[0][0], area[2][0]):
            cv2.rectangle(img, area[0], area[3], (0, 0, 0), -1)
        elif is_in_range(area[0][0], area[3][0]):
            cv2.rectangle(img, area[0], area[2], (0, 0, 0), -1)
        elif is_in_range(area[0][1], area[2][1]):
            cv2.rectangle(img, area[0], area[3], (0, 0, 0), -1)
        elif is_in_range(area[0][1], area[3][1]):
            cv2.rectangle(img, area[0], area[2], (0, 0, 0), -1)


def build_wall_contour_image_list(edges_img, contours):
    for i,contour in enumerate(contours):
            wall_contour_images.append(draw_wall_contour(edges_img, [contour]))


def readjust_closure_areas(closure_areas):
    readjusted_closure_areas = []
    for area in closure_areas:
        if is_in_range(area[1][0], area[2][0]) or is_in_range(area[1][1], area[2][1]):
            readjusted_closure_areas.append([area[0], area[1], area[2], area[3]])
        else:
            readjusted_closure_areas.append([area[0], area[1], area[3], area[2]])
    return readjusted_closure_areas


#######################################
# For each contour extract all corners
#######################################
def extract_corners_from_contours(edges_img, contours):
    new_corners = []
    wall_contour_images.clear()
    build_wall_contour_image_list(edges_img, contours)
    for i, img in enumerate(wall_contour_images):
        contour_img, corners = extract_wall_corners_sub(img)
        if is_wall_a_legal_structure(corners):
            new_corners.append(walk_shortest_corners(corners, contour_img))
    return new_corners


def extract_closure_areas(edges_img, contours, objects=None, wall_position='outer'):
    corner_pairs = []
    max_corner_pairs = 2
    wall_contour_images.clear()

    if wall_position == 'inner':
        max_corner_pairs = 0

    build_wall_contour_image_list(edges_img, contours)

    for i, img in enumerate(wall_contour_images):
        contour_img, corners = extract_wall_corners_sub(img)
        if is_wall_a_legal_structure(corners):
            cp = find_viable_corner_pairs(corners, contour_img)
            scp = find_shortest_pairs(cp, max_corner_pairs)
            corner_pairs.append(scp)

    if wall_position == 'inner':
        closure_areas = find_inner_wall_closure_areas(objects, corner_pairs)
    else:
        closure_areas = find_outer_wall_closure_areas(corner_pairs)

    return readjust_closure_areas(closure_areas)


