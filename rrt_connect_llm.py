#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from mapinfo import MapInfo
from rrt_connect import rrt_connect_planning
import aer1516

if __name__ == "__main__":
    m = MapInfo(50, 50)
    m.show()
    m.start = (10, 10)
    m.end = (40, 40)
    m.obstacle = [(15, i) for i in range(30)] + [(35, 50 - i) for i in range(30)]
    input('enter to start ...')
    m.path = rrt_connect_planning(m, display=True, points_generator_type=aer1516.LlmPointsGenerator)
    print('success!')
    m.wait_close()
