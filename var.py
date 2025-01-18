import time
import os
import threading
import numpy as np
import math
import sys
import ctypes as cts
import ctypes.wintypes as wts




projection_matrix = np.matrix([
    [1, 0, 0],
    [0, 1, 0]
])

LF_FACESIZE = 32
STD_OUTPUT_HANDLE = -11




def get_vertices(file_path):
    vertices = []
    # Open the file and read its content
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('v '):
                vertex = line.split()[1:]
                vertices.append([float(coord) for coord in vertex])
    return vertices

def get_faces(file_path):
    faces = []
    
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('f '):
                face = line.split()[1:]
                faces.append([int(vertex_idx.split('/')[0]) - 1 for vertex_idx in face])  
    return faces

def set_cmd_font_size(size=5):
    os.system(f"reg add \"HKCU\\Console\" /v FontSize /t REG_DWORD /d {size} /f")

def restore_cmd_font_size():
    os.system("reg delete \"HKCU\\Console\" /v FontSize /f")

def load_model(file_path):
    points = []
    for vertices in get_vertices(file_path):
        points.append(np.matrix(vertices))
    faces = get_faces(file_path)


    return [points, faces]

class CONSOLE_FONT_INFOEX(cts.Structure):
    _fields_ = (
        ("cbSize", wts.ULONG),
        ("nFont", wts.DWORD),
        ("dwFontSize", wts._COORD),
        ("FontFamily", wts.UINT),
        ("FontWeight", wts.UINT),
        ("FaceName", wts.WCHAR * LF_FACESIZE)
    )

class Screen():
    def __init__(self, width:int, height:int, font_size:int, show_fps:bool, obj_scale:int, obj:load_model):
        self.width = width
        self.height = height
        self.verticeholder = "#"
        self.emptyholder = " "
        self.lineholder = "."
        self.screen = []
        self.fontSize = font_size
        self.angle = 0 
        self.scale = obj_scale
        self.points = obj[0]
        self.faces = obj[1]
        self.frame_count = 0
        self.start_time = time.time()
        self.show_fps = show_fps

        self.projected_points = []

        self.rc = self.Resize_Terminal(self.fontSize)


    def Resize_Terminal(self, size):
        self.kernel32 = cts.WinDLL("Kernel32.dll")
        self.GetLastError = self.kernel32.GetLastError
        self.GetLastError.argtypes = ()
        self.GetLastError.restype = wts.DWORD
        self.GetStdHandle = self.kernel32.GetStdHandle
        self.GetStdHandle.argtypes = (wts.DWORD,)
        self.GetStdHandle.restype = wts.HANDLE
        self.GetCurrentConsoleFontEx = self.kernel32.GetCurrentConsoleFontEx
        self.GetCurrentConsoleFontEx.argtypes = (wts.HANDLE, wts.BOOL, cts.POINTER(CONSOLE_FONT_INFOEX))
        self.GetCurrentConsoleFontEx.restype = wts.BOOL
        self.SetCurrentConsoleFontEx = self.kernel32.SetCurrentConsoleFontEx
        self.SetCurrentConsoleFontEx.argtypes = (wts.HANDLE, wts.BOOL, cts.POINTER(CONSOLE_FONT_INFOEX))
        self.SetCurrentConsoleFontEx.restype = wts.BOOL

        self.stdout = self.GetStdHandle(STD_OUTPUT_HANDLE)
        if not self.stdout:
            return
        self.font = CONSOLE_FONT_INFOEX()
        self.font.cbSize = cts.sizeof(CONSOLE_FONT_INFOEX)
        self.res = self.GetCurrentConsoleFontEx(self.stdout, False, cts.byref(self.font))
        if not self.res:
            return

        self.font.dwFontSize.X = 10 # <- irrelevant
        self.font.dwFontSize.Y = self.fontSize
        self.res = self.SetCurrentConsoleFontEx(self.stdout, False, cts.byref(self.font))
        if not self.res:
            return
        self.res = self.GetCurrentConsoleFontEx(self.stdout, False, cts.byref(self.font))
        if not self.res:
            return

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
                self.angle += 0.02

                for point in self.points:
                    rotated2d = np.dot(rotation_z, point.reshape((3, 1)))
                    rotated2d = np.dot(rotation_y, rotated2d)
                    rotated2d = np.dot(rotation_x, rotated2d)

                    projected2d = np.dot(projection_matrix, rotated2d)

                    x = int(projected2d[0][0] * self.scale) + self.width//2
                    y = int(projected2d[1][0] * self.scale) + self.height//2

                    
                    try:
                        if y>=0 and x>=0:
                            self.screen[y][x] = self.verticeholder

                    except:
                        pass
                    self.projected_points.append([y, x])

                    
                for face in self.faces:
                    num_vertices = len(face)
                    for i in range(num_vertices):
                        start_idx = face[i]
                        end_idx = face[(i + 1) % num_vertices]


                        self.connect_line(self.projected_points[start_idx], self.projected_points[end_idx])


                if self.show_fps:
                    self.frame_count += 1
                    self.elapsed_time = time.time() - self.start_time
                    if self.elapsed_time > 0:
                        fps = str(int(self.frame_count / self.elapsed_time))
                        for i, digit in enumerate(fps):
                            self.screen[0][-len(fps) + i] = digit

                
                sys.stdout.write("\n".join("".join(row) for row in self.screen) + "\n")

                
                
                

                
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

        if self.x1>=0 and self.x1<self.height and self.y1>=0 and self.y1<self.width:
            self.screen[self.x1][self.y1] = self.verticeholder
        if self.x2>=0 and self.x2<self.height and self.y2>=0 and self.y2<self.width:
            self.screen[self.x2][self.y2] = self.verticeholder



        
        

    def plot(self, x, y):

        try:
            if y>=0 and x>=0:

                self.screen[x][y] = self.lineholder
        except:
            pass
        


        pass

