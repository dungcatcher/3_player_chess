import math
from position import *
from board import board_position
from shapely.geometry import Point, Polygon

# half_segment_polygon = [  # Entire polygon for half segment 1
#     [587, 72], [1092, 72], [1092, 946], [335, 509]
# ]
half_segment_polygon = [(335, 1382), (1092, 946), (1092, 1820), (587, 1820)]


def lerp(v0, v1, t):
    return (1 - t) * v0 + t * v1


def lerp_vector(v0, v1, t):
    return lerp(v0[0], v1[0], t), lerp(v0[1], v1[1], t)


def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]


def position_to_pixel(position, board_polygons):
    polygon_points = board_polygons[int(
        position.segment)][int(position.square.y)][int(position.square.x)]
    polygon = Polygon(polygon_points)
    pixel_pos = polygon.centroid.coords[:][0]
    return pixel_pos


def compute_polygons():
    all_polygons = []
    for segment in range(3):
        # 8x4 array of polygons for the segment
        segment_polygons = [[[] for x in range(8)] for y in range(4)]
        for half_segment in range(2):
            angle = -math.radians((2 * segment + half_segment) * 60)
            rotated_half_segment_polygon = []
            for point in half_segment_polygon:
                rotated_half_segment_polygon.append(
                    rotate(half_segment_polygon[1], point, angle))

            for y in range(4):  # Top left corners of polygons
                for x in range(4):
                    polygon = []
                    for i in range(2):  # Offset corners for polygon
                        for j in range(2):
                            if i == 1:  # Points go anti-clockwise
                                j = 1 if j == 0 else 0
                            top_lerp = lerp_vector(rotated_half_segment_polygon[0 - 3 * half_segment],
                                                   rotated_half_segment_polygon[1 -
                                                                                3 * half_segment],
                                                   (x + i) * 0.25)
                            bottom_lerp = lerp_vector(rotated_half_segment_polygon[3 - 3 * half_segment],
                                                      rotated_half_segment_polygon[2 -
                                                                                   3 * half_segment],
                                                      (x + i) * 0.25)
                            lerp_point = lerp_vector(
                                top_lerp, bottom_lerp, (y + j) * 0.25)
                            polygon.append(lerp_point)
                    segment_polygons[y][x + 4 * half_segment] = polygon
        all_polygons.append(segment_polygons)

    return all_polygons


def handle_polygon_resize(polygons, new_scale, margin):
    polygons_copy = [[[[] for x in range(8)]
                      for y in range(4)] for s in range(3)]
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                new_point = []
                for point in polygons[segment][y][x]:
                    new_point.append(
                        (point[0] * new_scale + margin, point[1] * new_scale))
                polygons_copy[segment][y][x] = new_point

    return polygons_copy
