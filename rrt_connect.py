#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mapinfo import MapInfo
from random import randint
from scipy.spatial import cKDTree
import math
from rrt import RRT
from rrt import reconstruct_path as constructpath
import aer1516

def reconstruct_path(rrta, rrtb, q_reach, map_info):
    if rrta.is_root(map_info.start):
        rrt_start = rrta
        rrt_end = rrtb
    else:
        rrt_start = rrtb
        rrt_end = rrta
    p1 = constructpath(rrt_start, q_reach)
    p2 = constructpath(rrt_end, q_reach)
    p2.reverse()
    return p2 + p1

def rrt_connect_planning(map_info, display=False, points_generator_type=aer1516.RandomPointsGenerator):
    rrt_start = RRT(map_info.start)
    rrt_end = RRT(map_info.end)
    rrt_a = rrt_start
    rrt_b = rrt_end

    points_generator_a = points_generator_type(map_info, rrt_a, map_info.end, visualize=True)
    points_generator_b = points_generator_type(map_info, rrt_b, map_info.start, visualize=True)

    okdtree = cKDTree(map_info.obstacle)
    while True:
        q_rand = points_generator_a.generate_point()
        if q_rand == map_info.start or q_rand in map_info.obstacle or rrt_a.is_contain(q_rand):
            points_generator_a.report_invalid_point()
            continue
        q_new = rrt_a.extend(q_rand, okdtree)
        if not q_new:
            points_generator_a.report_invalid_point()
            continue
        points_generator_a.report_successful_point()
        while True:
            q_new_ = rrt_b.extend(q_new, okdtree)
            if display:
                map_info.set_rand(q_rand)
                map_info.set_rrt_connect(rrt_a.get_rrt(), rrt_b.get_rrt())
            # 2 rrts reached
            if q_new == q_new_:
                return reconstruct_path(rrt_a, rrt_b, q_new, map_info)
            elif q_new_ == None:
                break
        # swap 2 rrts
        rrt_a, rrt_b = rrt_b, rrt_a
        points_generator_a, points_generator_b = points_generator_b, points_generator_a

if __name__ == "__main__":
    m = MapInfo(50, 50)
    m.show()
    m.start = (10, 10)
    m.end = (40, 40)
    m.obstacle = [(15, i) for i in range(30)] + [(35, 50 - i) for i in range(30)]
    input('enter to start ...')
    m.path = rrt_connect_planning(m, display=True)
    print('success!')
    m.wait_close()
