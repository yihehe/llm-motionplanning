from openai import OpenAI
import secretkey
import re
import random

client = OpenAI(
    api_key=secretkey.openai_api_key
)

def gpt4(prompt):
    response = client.chat.completions.create(
      model="gpt-4-turbo-preview",
      messages=[
        {
          "role": "user",
          "content": prompt
        }
      ],
      temperature = 1,
      max_tokens = 256,
      top_p = 1,
      frequency_penalty = 0,
      presence_penalty= 0
    )

    print("user_content: ", prompt)
    print("response: ", response)

    return response.choices[0].message.content

def get_prompt(start, end):
    return f"""
    You are a robot on a 50x50 map. We will work with coordinates on the map, where (0,0) is the south west corner, and (49,49) is north east corner.

    There are the coordinates of the obstacles on the map that you cannot pass through (consider these coordinates as inclusive):
    1. Solid rectangle with corners at (15,0), (16,0), (15,30), (16,30). This obstacle meets the bottom boundary of the map.
    2. Solid rectange with corners at (35,20), (36,20), (35,49), (36,49). This obstacle meets the top boundary of the map.
    Some obstacles extend from the boundaries of the map and you cannot pass through the obstacle and the boundaries of the map.

    You must avoid passing through any of the mentioned obstacles and stay within the bounds of the map.

    Your starting position is {start}, and the goal is to reach {end}. Think of a path that can lead from the starting position to the goal position. Be mindful of obstacles and the boundaries of the map.
    Give a list of points along this path, making sure not to pass through the stated obstacles and staying within the bounds of the map.
    """

def llm_points(start, end):
    gpt_response = gpt4(get_prompt(start, end))

    # extract points in tuple format from free-form response
    tuple_list = re.findall(r'\(\d+,\s*\d+\)', gpt_response)
    candidate_points = [tuple(map(int, t.strip('()').split(','))) for t in tuple_list]

    # remove start and end points
    candidate_points = [point for point in candidate_points if point != start and point != end]

    return candidate_points

class PointsGenerator(object):
    def __init__(self, map_info, rrt, visualize=False):
        self.map_info = map_info
        self.rrt = rrt
        self.width = map_info.width
        self.height = map_info.height

        self.visualize = visualize

        self.points_counter = 0

    def generate_point(self):
        pass

    def report_successful_point(self):
        self.reset_points_counter()

    def report_invalid_point(self):
        self.points_counter += 1

    def reset_points_counter(self):
        self.points_counter = 0

class RandomPointsGenerator(PointsGenerator):
    def generate_point(self):
        return (random.randint(0, self.width - 1), random.randint(0, self.height - 1))

class LlmPointsGenerator(PointsGenerator):
    def generate_point(self):
        print(self.points_counter)
        if not hasattr(self, 'candidate_points'):
            self.candidate_points = []

        if len(self.candidate_points) == 0 or self.should_update_points(self.points_counter):
            self.update_points()

        point = random.choice(self.candidate_points)
        # fuzz the point since the llm likes to generate points that are too close to the wall
        point = (point[0] + random.randint(-2, 2), point[1] + random.randint(-2, 2))
        point = (min(max(point[0], 0), self.width - 1), min(max(point[1], 0), self.height - 1))
        return point

    def update_points(self):
        start = self.rrt.search_nearest_vertex(self.map_info.end)
        end = self.map_info.end

        start = (int(start[0]), int(start[1]))
        end = (int(end[0]), int(end[1]))

        if self.visualize:
            print(f"llm update_points from {start} to {end}")

        new_points = llm_points(start, end)
        interpolated_points = []
        for i in range(len(new_points) - 1):
            point1 = new_points[i]
            point2 = new_points[i + 1]
            interpolated_points.extend(self.interpolate_points(point1, point2, 5))
        new_points.extend(interpolated_points)
        self.candidate_points.extend(new_points)
        self.candidate_points = list(set(self.candidate_points))

        self.reset_points_counter()

        if self.visualize:
            # plot the new points for visualization
            for new in new_points:
                self.map_info.set_rand(new)
            input('press enter to continue...')


    def interpolate_points(self, point1, point2, num_points):
        interpolated_points = []
        for i in range(1, num_points + 1):
            x = point1[0] + (point2[0] - point1[0]) * i / (num_points + 1)
            y = point1[1] + (point2[1] - point1[1]) * i / (num_points + 1)
            interpolated_points.append((int(x), int(y)))
        return interpolated_points

    # determines how often we should update the points. this is a hyperparameter that needs to be tuned
    def should_update_points(self, num_consecutive_skips):
        return num_consecutive_skips > len(self.candidate_points)
