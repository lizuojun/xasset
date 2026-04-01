# -*- coding: utf-8 -*-

"""
@Author:
@Date: 2019-01-18
@Description:

"""

import math
from functools import cmp_to_key


class Point2D(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return 'Point (' + str(self.x) + ', ' + str(self.y) + ')'

    def __repr__(self):
        return self.__str__()

    def copy_from(self, pt):
        self.x = pt.x
        self.y = pt.y
        return self

    def dist_to(self, pt):
        return math.sqrt(math.pow(pt.x - self.x, 2) + math.pow(pt.y - self.y, 2))


class Seg(object):
    def __init__(self, end0, end1):
        self.end0 = Point2D(0, 0).copy_from(end0)
        self.end1 = Point2D(0, 0).copy_from(end1)
        self.xmin = 0.0
        self.xmax = 0.0
        self.ymin = 0.0
        self.ymax = 0.0
        self.update_domain()

    def __str__(self):
        return 'Seg (' + self.end0.__str__() + ', ' + self.end1.__str__() + ')'

    def __repr__(self):
        return self.__str__()

    def update_domain(self):
        self.xmin = min(self.end0.x, self.end1.x)
        self.xmax = max(self.end0.x, self.end1.x)
        self.ymin = min(self.end0.y, self.end1.y)
        self.ymax = max(self.end0.y, self.end1.y)

    def get_ratio(self):
        if (self.end1.x - self.end0.x) == 0:
            return math.inf
        else:
            return (self.end1.y - self.end0.y) / (self.end1.x - self.end0.x)

    def dist_to(self, pt):
        a = self.end1.y - self.end0.y
        b = self.end0.x - self.end1.x
        c = self.end1.x * self.end0.y - self.end0.x * self.end1.y
        return math.fabs(a * pt.x + b * pt.y + c) / math.sqrt(a * a + b * b)

    def on_seg(self, pt):
        if (pt.x - self.xmin) < -2e-3 or \
                (pt.x - self.xmax) > 2e-3 or \
                (pt.y - self.ymin) < -2e-3 or \
                (pt.y - self.ymax) > 2e-3:
            return False
        e = self.dist_to(pt)
        if e < 1e-3:
            return True
        else:
            return False

    def on_seg_end(self, pt):
        if pt.dist_to(self.end0) < 1e-5 or pt.dist_to(self.end1) < 1e-5:
            return True
        else:
            return False

    def direction_to(self, seg):
        x1 = self.end1.x - self.end0.x
        y1 = self.end1.y - self.end0.y
        x2 = seg.end1.x - seg.end0.x
        y2 = seg.end1.y - seg.end0.y
        ang = math.atan2(x1 * y2 - y1 * x2, x1 * x2 + y1 * y2)
        return math.pi if math.fabs(ang + math.pi) < 1e-5 else ang

    def is_same(self, seg):
        if self.end0.dist_to(seg.end0) < 1e-5 and self.end1.dist_to(seg.end1) < 1e-5:
            return 1
        if self.end0.dist_to(seg.end1) < 1e-5 and self.end1.dist_to(seg.end0) < 1e-5:
            return -1
        return 0


class BBox(object):
    def __init__(self, xmin, ymin, xmax, ymax):
        self.min = Point2D(xmin, ymin)
        self.max = Point2D(xmax, ymax)


class Polygon(object):
    def __init__(self, segs):
        self.segs = segs
        self.bbox = self.compute_bbox()

    def compute_bbox(self):
        xmin = math.inf
        ymin = math.inf
        xmax = -math.inf
        ymax = -math.inf
        for seg in self.segs:
            xmin = min(xmin, seg.end0.x, seg.end1.x)
            ymin = min(ymin, seg.end0.y, seg.end1.y)
            xmax = max(xmax, seg.end0.x, seg.end1.x)
            ymax = max(ymax, seg.end0.y, seg.end1.y)
        return BBox(xmin, ymin, xmax, ymax)

    def pt_on_polygon(self, pt):
        for seg_one in self.segs:
            if seg_one.on_seg(pt):
                return True
        return False

    def seg_on_polygon(self, seg):
        for seg_one in self.segs:
            if seg_one.on_seg(seg.end0) and seg_one.on_seg(seg.end1):
                return True
        return False

    def to_pt_array(self, index_start=0):
        pts = []
        seg_cnt = len(self.segs)
        for i in range(seg_cnt):
            seg_now = self.segs[index_start % seg_cnt]
            pts.append(seg_now.end0.x)
            pts.append(seg_now.end0.y)
            index_start += 1
        return pts


def is_intersecting(v1x1, v1y1, v1x2, v1y2, v2x1, v2y1, v2x2, v2y2):
    # Convert vector 1 to a line (line 1) of infinite length.
    # We want the line in linear equation standard form: A*x + B*y + C = 0
    # See: http://en.wikipedia.org/wiki/Linear_equation
    a1 = v1y2 - v1y1
    b1 = v1x1 - v1x2
    c1 = (v1x2 * v1y1) - (v1x1 * v1y2)

    # Every point (x,y), that solves the equation above, is on the line,
    # every point that does not solve it, is not. The equation will have a
    # positive result if it is on one side of the line and a negative one
    # if is on the other side of it. We insert (x1,y1) and (x2,y2) of vector
    # 2 into the equation above.
    d1 = (a1 * v2x1) + (b1 * v2y1) + c1
    d2 = (a1 * v2x2) + (b1 * v2y2) + c1

    # If d1 and d2 both have the same sign, they are both on the same side
    # of our line 1 and in that case no intersection is possible. Careful,
    # 0 is a special case, that's why we don't test ">=" and "<=",
    # but "<" and ">".
    if math.fabs(d1) < 1e-12:
        d1 = 0
    if math.fabs(d2) < 1e-12:
        d2 = 0
    if d1 > 0 and d2 > 0:
        return 0
    if d1 < 0 and d2 < 0:
        return 0

    # The fact that vector 2 intersected the infinite line 1 above doesn't
    # mean it also intersects the vector 1. Vector 1 is only a subset of that
    # infinite line 1, so it may have intersected that line before the vector
    # started or after it ended. To know for sure, we have to repeat the
    # the same test the other way round. We start by calculating the
    # infinite line 2 in linear equation standard form.
    a2 = v2y2 - v2y1
    b2 = v2x1 - v2x2
    c2 = (v2x2 * v2y1) - (v2x1 * v2y2)

    # Calculate d1 and d2 again, this time using points of vector 1.
    d1 = (a2 * v1x1) + (b2 * v1y1) + c2
    d2 = (a2 * v1x2) + (b2 * v1y2) + c2

    # Again, if both have the same sign (and neither one is 0),
    # no intersection is possible.
    if math.fabs(d1) < 1e-12:
        d1 = 0
    if math.fabs(d2) < 1e-12:
        d2 = 0
    if d1 > 0 and d2 > 0:
        return 0
    if d1 < 0 and d2 < 0:
        return 0

    # If we get here, only two possibilities are left. Either the two
    # vectors intersect in exactly one point or they are collinear, which
    # means they intersect in any number of points from zero to infinite.
    if (a1 * b2) - (a2 * b1) == 0.0:
        return 2

    # If they are not collinear, they must intersect in exactly one point.
    return 1


def intersect_lines(seg0, seg1):
    a0 = seg0.end1.y - seg0.end0.y
    b0 = seg0.end0.x - seg0.end1.x
    c0 = seg0.end1.x * seg0.end0.y - seg0.end0.x * seg0.end1.y
    a1 = seg1.end1.y - seg1.end0.y
    b1 = seg1.end0.x - seg1.end1.x
    c1 = seg1.end1.x * seg1.end0.y - seg1.end0.x * seg1.end1.y
    det = a0 * b1 - a1 * b0
    if det == 0:
        return Point2D(math.inf, math.inf)
    return Point2D((b0 * c1 - b1 * c0) / det, (a1 * c0 - a0 * c1) / det)


def intersect_polygon(poly, pt0, pt1):
    intersections = []
    for i in range(len(poly.segs)):
        seg = poly.segs[i]
        if is_intersecting(pt0.x, pt0.y, pt1.x, pt1.y, seg.end0.x, seg.end0.y, seg.end1.x, seg.end1.y) == 1:
            intersections.append(i)
    return intersections


def index_of_list(seg_list, predicate):
    try:
        return next(i for i in range(len(seg_list)) if predicate(seg_list[i]))
    except Exception as e:
        print(e)
        return -1


def index_of_segs(seg_one, seg_list):
    predicate = lambda seg: seg_one.end0.dist_to(seg.end0) < 1e-3 and seg_one.end1.dist_to(seg.end1) < 1e-3
    try:
        return next(i for i in range(len(seg_list)) if predicate(seg_list[i]))
    except Exception as e:
        print(e)
        return -1


def merge_rect(poly, seg_list):
    for i in range(len(seg_list)):
        ends = [seg_list[i].end0, seg_list[i].end1]
        for j in [0, 1]:
            pt_id = index_of_list(poly.segs, lambda aSeg: aSeg.on_seg(ends[j]))
            if pt_id != -1 and not poly.segs[pt_id].on_seg_end(ends[j]):
                seg_to_insert = Seg(ends[j], poly.segs[pt_id].end1)
                poly.segs[pt_id].end1.copy_from(ends[j])
                poly.segs[pt_id].update_domain()
                poly.segs.insert(pt_id + 1, seg_to_insert)

    # prepare directional edges for the polygon
    # toAddSegs are bidirectional edges
    seg_pool = list(poly.segs)
    for seg in seg_list:
        seg_pool.append(seg)
        seg_pool.append(Seg(seg.end1, seg.end0))

    # merge directional edges to generate rectangles
    rect_list = []
    while len(seg_pool) != 0:
        rect = []
        cur_id = 0
        found = True
        while found:
            cur = seg_pool[cur_id]
            rect.append(seg_pool[cur_id])
            del seg_pool[cur_id]
            # find next connected
            # (1) find all connected
            connect_ids = []
            for i in range(len(seg_pool)):
                if seg_pool[i].end0.dist_to(cur.end1) < 1e-5:
                    connect_ids.append(i)
            # (2) find clockwise most one
            if len(connect_ids) != 0:
                cmp = lambda aId, bId: cur.direction_to(seg_pool[aId]) - cur.direction_to(seg_pool[bId])
                connect_ids.sort(key=cmp_to_key(cmp))
                cur_id = connect_ids[0]
            else:
                found = False
        rect_list.append(rect)

    rect_list_new = []
    for rect in rect_list:
        p = Polygon(rect)
        rect_info = {
            'center': [(p.bbox.min.x + p.bbox.max.x) / 2, (p.bbox.min.y + p.bbox.max.y) / 2],
            'extend': {'x': [p.bbox.max.x - p.bbox.min.x, 0], 'y': [0, p.bbox.max.y - p.bbox.min.y]}
        }
        rect_list_new.append(rect_info)
    return rect_list_new


def slicing(poly):
    pt0 = Point2D(0.0, 0.0)
    pt1 = Point2D(0.0, 0.0)
    pt_check = Point2D(poly.bbox.max.x + (poly.bbox.max.x - poly.bbox.min.x) / 2.0,
                       poly.bbox.max.y + (poly.bbox.max.y - poly.bbox.min.y) / 2.0)
    seg_to_add = []
    for seg_one in poly.segs:
        if math.fabs(seg_one.get_ratio()) > 1e-2:
            continue
        # for each horizontal seg, check its two ends
        # check if left is inside polygon
        if seg_one.end0.x < seg_one.end1.x:
            pt0.x = seg_one.end0.x - 0.01
            pt0.y = seg_one.end0.y
            pt1.y = seg_one.end0.y
        else:
            pt0.x = seg_one.end1.x - 0.01
            pt0.y = seg_one.end1.y
            pt1.y = seg_one.end1.y
        pt0.x = min(seg_one.end0.x, seg_one.end1.x) - 0.01
        pt1.x = poly.bbox.min.x - 1
        intersects = intersect_polygon(poly, pt0, pt_check)
        if (len(intersects) & 1) == 1:
            intersects = intersect_polygon(poly, pt0, pt1)
            if len(intersects) > 0:
                seg_cut = Seg(pt0, pt1)
                cut_pt_list = list(map(lambda sId: intersect_lines(poly.segs[sId], seg_cut), intersects))
                cut_pt_list.sort(key=cmp_to_key(lambda aPt, bPt: pt0.dist_to(aPt) - pt0.dist_to(bPt)))
                cut_pt = cut_pt_list[0]
                seg_to_add.append(Seg(cut_pt, Point2D(pt0.x + 0.01, pt0.y)))

        # check if right is inside polygon
        if seg_one.end0.x > seg_one.end1.x:
            pt0.x = seg_one.end0.x + 0.01
            pt0.y = seg_one.end0.y
            pt1.y = seg_one.end0.y
        else:
            pt0.x = seg_one.end1.x + 0.01
            pt0.y = seg_one.end1.y
            pt1.y = seg_one.end1.y
        pt1.x = poly.bbox.max.x + 1
        intersects = intersect_polygon(poly, pt0, pt_check)
        if (len(intersects) & 1) == 1:
            intersects = intersect_polygon(poly, pt0, pt1)
            if len(intersects) > 0:
                seg_cut = Seg(pt0, pt1)
                cut_pt_list = list(map(lambda sId: intersect_lines(poly.segs[sId], seg_cut), intersects))
                cut_pt_list.sort(key=cmp_to_key(lambda aPt, bPt: pt0.dist_to(aPt) - pt0.dist_to(bPt)))
                cut_pt = cut_pt_list[0]
                seg_to_add.append(Seg(Point2D(pt0.x - 0.01, pt0.y), cut_pt))
    # remove duplicates
    seg_to_add_uniq = []
    for i in range(len(seg_to_add)):
        if index_of_segs(seg_to_add[i], seg_to_add) == i:
            seg_to_add_uniq.append(seg_to_add[i])
    return seg_to_add_uniq


def split_vertical(data):
    seg_list = []
    for i in range(0, len(data) - 3, 2):
        # rotate 90 degree
        end0 = Point2D(data[i + 1], -data[i + 0])
        end1 = Point2D(data[i + 3], -data[i + 2])
        seg_list.append(Seg(end0, end1))
    poly = Polygon(seg_list)
    seg_list_new = slicing(poly)
    rect_list = merge_rect(poly, seg_list_new)
    for rect_info in rect_list:
        # rotate the rect info back
        old_center = rect_info['center']
        old_extend_x = rect_info['extend']['x']
        old_extend_y = rect_info['extend']['y']
        new_center = [-old_center[1], old_center[0]]
        new_extend_x = [old_extend_y[1], old_extend_y[0]]
        new_extend_y = [old_extend_x[1], old_extend_x[0]]
        rect_info['center'] = new_center
        rect_info['extend']['x'] = new_extend_x
        rect_info['extend']['y'] = new_extend_y
    # print(rect_list)
    return rect_list


def split_horizontal(data):
    seg_list = []
    for i in range(0, len(data) - 3, 2):
      end0 = Point2D(data[i + 0], data[i + 1])
      end1 = Point2D(data[i + 2], data[i + 3])
      seg_list.append(Seg(end0, end1))
    poly = Polygon(seg_list)
    seg_list_new = slicing(poly)
    rect_list = merge_rect(poly, seg_list_new)
    # print(rect_list)
    return rect_list
