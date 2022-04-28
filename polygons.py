import math
from shapely.geometry import Point, Polygon
import pygame.gfxdraw

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
    hover_points = [[[None for x in range(8)] for y in range(4)] for segment in range(3)]  # Places where pieces move to when hovered over
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
                                                   rotated_half_segment_polygon[1 - 3 * half_segment],
                                                   (x + i) * 0.25)
                            bottom_lerp = lerp_vector(rotated_half_segment_polygon[3 - 3 * half_segment],
                                                      rotated_half_segment_polygon[2 - 3 * half_segment],
                                                      (x + i) * 0.25)
                            lerp_point = lerp_vector(
                                top_lerp, bottom_lerp, (y + j) * 0.25)
                            polygon.append(lerp_point)
                    segment_polygons[y][x + 4 * half_segment] = polygon

                    top_midpoint = lerp_vector(polygon[0], polygon[3], 0.5)
                    bottom_midpoint = lerp_vector(polygon[1], polygon[2], 0.5)
                    hover_point = lerp_vector(bottom_midpoint, top_midpoint, 0.6)

                    hover_points[segment][y][x + 4 * half_segment] = hover_point

        all_polygons.append(segment_polygons)

    return [all_polygons, hover_points]


def handle_polygon_resize(polygon_data, new_scale, offset):
    polygons_copy = [[[None for x in range(8)] for y in range(4)] for s in range(3)]
    hover_points_copy = [[[None for x in range(8)] for y in range(4)] for s in range(3)]
    for segment in range(3):
        for y in range(4):
            for x in range(8):
                new_point = []
                for point in polygon_data[0][segment][y][x]:
                    new_point.append(
                        (point[0] * new_scale + offset[0], point[1] * new_scale + offset[1]))
                polygons_copy[segment][y][x] = new_point

                hover_point = polygon_data[1][segment][y][x]
                hover_points_copy[segment][y][x] = (hover_point[0] * new_scale + offset[0], hover_point[1] * new_scale + offset[1])

    return [polygons_copy, hover_points_copy]


# gfxdraw doesn't support thick antialiased shapes
def draw_thick_aaline(surface, colour, start_pos, end_pos, width=1):
    # ref https://stackoverflow.com/a/30599392/355230

    x0, y0 = start_pos
    x1, y1 = end_pos
    midpnt_x, midpnt_y = (x0 + x1) / 2, (y0 + y1) / 2  # Center of line segment.
    length = math.hypot(x1 - x0, y1 - y0)
    angle = math.atan2(y0 - y1, x0 - x1)  # Slope of line.
    width2, length2 = width / 2, length / 2
    sin_ang, cos_ang = math.sin(angle), math.cos(angle)

    width2_sin_ang = width2 * sin_ang
    width2_cos_ang = width2 * cos_ang
    length2_sin_ang = length2 * sin_ang
    length2_cos_ang = length2 * cos_ang

    # Calculate box ends.
    ul = (midpnt_x + length2_cos_ang - width2_sin_ang,
          midpnt_y + width2_cos_ang + length2_sin_ang)
    ur = (midpnt_x - length2_cos_ang - width2_sin_ang,
          midpnt_y + width2_cos_ang - length2_sin_ang)
    bl = (midpnt_x + length2_cos_ang + width2_sin_ang,
          midpnt_y - width2_cos_ang + length2_sin_ang)
    br = (midpnt_x - length2_cos_ang + width2_sin_ang,
          midpnt_y - width2_cos_ang - length2_sin_ang)

    pygame.gfxdraw.aapolygon(surface, (ul, ur, br, bl), colour)
    pygame.gfxdraw.filled_polygon(surface, (ul, ur, br, bl), colour)


def draw_thick_aapolygon(surface, colour, points, width=1):
    for i in range(len(points)):
        start_pos = points[i]
        end_pos = points[(i + 1) % len(points)]
        draw_thick_aaline(surface, colour, start_pos, end_pos, width)
