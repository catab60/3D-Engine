import os
import threading
import numpy as np
import math


points = []
scale = 10
points.append(np.matrix([-1, -1, 1]))
points.append(np.matrix([1, -1, 1]))
points.append(np.matrix([1,  1, 1]))
points.append(np.matrix([-1, 1, 1]))
points.append(np.matrix([-1, -1, -1]))
points.append(np.matrix([1, -1, -1]))
points.append(np.matrix([1, 1, -1]))
points.append(np.matrix([-1, 1, -1]))

projection_matrix = np.matrix([
    [1, 0, 0],
    [0, 1, 0]
])



class Screen():
    def __init__(self):
        self.width = 150
        self.height = 50
        self.placeholder = "#"
        self.emptyholder = " "
        self.lineholder = "#"
        self.screen = []
        self.angle = 0 

        self.projected_points = []

    def render(self):
        def sub_proccess():
            while True:
                self.clear()
                os.system(f"mode con cols={self.width+1} lines={self.height+1}")

                rotation_z = np.matrix([
                    [math.cos(self.angle), -math.sin(self.angle), 0],
                    [math.sin(self.angle), math.cos(self.angle), 0],
                    [0, 0, 1],
                ])

                rotation_y = np.matrix([
                    [math.cos(self.angle), 0, math.sin(self.angle)],
                    [0, 1, 0],
                    [-math.sin(self.angle), 0, math.cos(self.angle)],
                ])

                rotation_x = np.matrix([
                    [1, 0, 0],
                    [0, math.cos(self.angle), -math.sin(self.angle)],
                    [0, math.sin(self.angle), math.cos(self.angle)],
                ])
                self.angle += 0.1

                for point in points:
                    rotated2d = np.dot(rotation_z, point.reshape((3, 1)))
                    rotated2d = np.dot(rotation_y, rotated2d)
                    rotated2d = np.dot(rotation_x, rotated2d)

                    projected2d = np.dot(projection_matrix, rotated2d)

                    x = int(projected2d[0][0] * scale) + self.width//2
                    y = int(projected2d[1][0] * scale) + self.height//2

                    self.screen[y][x] = self.placeholder
                    self.projected_points.append([y, x])

                    

                self.connect_line(self.projected_points[0], self.projected_points[1])
                self.connect_line(self.projected_points[1], self.projected_points[2])
                self.connect_line(self.projected_points[2], self.projected_points[3])
                self.connect_line(self.projected_points[3], self.projected_points[0])

                self.connect_line(self.projected_points[4], self.projected_points[5])
                self.connect_line(self.projected_points[5], self.projected_points[6])
                self.connect_line(self.projected_points[6], self.projected_points[7])
                self.connect_line(self.projected_points[7], self.projected_points[4])

                self.connect_line(self.projected_points[0], self.projected_points[4])
                self.connect_line(self.projected_points[1], self.projected_points[5])
                self.connect_line(self.projected_points[2], self.projected_points[6])
                self.connect_line(self.projected_points[3], self.projected_points[7])
                
                for row in range(len(self.screen)):
                    for col in range(len(self.screen[row])):
                        print(self.screen[row][col], end="")
                    print()
                
        threading.Thread(target=sub_proccess).start()

    def clear(self):
        self.projected_points = []
        self.screen = [[self.emptyholder for row in range(int(self.width))] for column in range(int(self.height))]

    def connect_line(self, p1, p2):
        self.x1 = p1[0]
        self.y1 = p1[1]
        self.x2 = p2[0]
        self.y2 = p2[1]

        self.dx = abs(self.x2 - self.x1)
        self.dy = abs(self.y2 - self.y1)

        self.sx = 1 if self.x1 < self.x2 else -1
        self.sy = 1 if self.y1 < self.y2 else -1

        self.error = self.dx - self.dy

        x, y = self.x1, self.y1

        while True:
            self.plot(x, y)
            
            if x == self.x2 and y == self.y2:
                break
            
            e2 = self.error * 2
            
            if e2 > -self.dy:
                self.error -= self.dy
                x += self.sx
            
            if e2 < self.dx:
                self.error += self.dx
                y += self.sy
    def plot(self, x, y):
        self.screen[x][y] = self.lineholder



p = Screen()

p.render()
input()