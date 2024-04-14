import time
from mapinfo import MapInfo
from rrt import rrt_planning
from rrt_star import rrt_star_planning
from rrt_connect import rrt_connect_planning
import aer1516

class Stats:
    def __init__(self, name):
        self.name = name
        self.iterations = 0
        self.time_spent = 0
        self.distance = 0
        self.num_points = 0
        self.success = False

        self.path = []

    def iterate(self):
        self.iterations += 1

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.time_spent = time.time() - self.start_time

    def final_path(self, path):
        self.success = True
        self.path = path

        for i in range(len(path)-1):
            self.distance += self.l2_distance(path[i], path[i+1])

    def l2_distance(self, p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

    def rrt(self, rrt_points):
        self.num_points = len(rrt_points)

    def rrt_connect(self, rrt_points_a, rrt_points_b):
        self.num_points = len(rrt_points_a) + len(rrt_points_b)

    def print(self, m=None):
        print("---------------------------------")
        print(f"Name:\t\t{self.name}")
        print(f"Success:\t{self.success}")
        print(f"Iterations:\t{self.iterations}")
        print(f"Time spent:\t{self.time_spent}")
        print(f"Distance:\t{self.distance}")
        print(f"Num Points:\t{self.num_points}")
        print("---------------------------------")


def setup_map():
    m = MapInfo(50, 50)
    m.show()
    m.start = (10, 10)
    m.end = (40, 40)
    m.obstacle = [(15, i) for i in range(30)] + [(35, 50 - i) for i in range(30)]

    # m.obstacle = [(15,1)]
    return m

def rrt():
    m = setup_map()
    stats = Stats("rrt")
    path = rrt_planning(m, display=display, stats=stats)
    if display:
        m.path = path
        m.wait_close()
    stats.print()
    return stats

def rrt_llm():
    m = setup_map()
    stats = Stats("rrt_llm")
    path = rrt_planning(m, display=display, stats=stats, points_generator_type=aer1516.LlmPointsGenerator)
    if display:
        m.path = path
        m.wait_close()
    stats.print()
    return stats

def rrt_star():
    m = setup_map()
    stats = Stats("rrt_star")
    path = rrt_star_planning(m, display=display, stats=stats)
    if display:
        m.path = path
        m.wait_close()
    stats.print()
    return stats

def rrt_star_llm():
    m = setup_map()
    stats = Stats("rrt_star_llm")
    path = rrt_star_planning(m, display=display, stats=stats, points_generator_type=aer1516.LlmPointsGenerator)
    if display:
        m.path = path
        m.wait_close()
    stats.print()
    return stats

def rrt_connect():
    m = setup_map()
    stats = Stats("rrt_connect")
    path = rrt_connect_planning(m, display=display, stats=stats)
    if display:
        m.path = path
        m.wait_close()
    stats.print()
    return stats

def rrt_connect_llm():
    m = setup_map()
    stats = Stats("rrt_connect_llm")
    path = rrt_connect_planning(m, display=display, stats=stats, points_generator_type=aer1516.LlmPointsGenerator)
    if display:
        m.path = path
        m.wait_close()
    stats.print()
    return stats

display = False
iterations = 10
stats = []

run = [rrt, rrt_llm, rrt_star, rrt_star_llm, rrt_connect, rrt_connect_llm]

for r in run:
    for i in range(iterations):
        print(f"Running {r.__name__} iteration {i+1}:")
        stats.append(r())

# print it all in csv
fieldnames = ['Name', 'Success', 'Iterations', 'Time Spent (s)', 'Distance', 'Num Points']
print(','.join(fieldnames))
for stat in stats:
    row = [stat.name, stat.success, stat.iterations, stat.time_spent, stat.distance, stat.num_points]
    print(','.join(str(value) for value in row))
