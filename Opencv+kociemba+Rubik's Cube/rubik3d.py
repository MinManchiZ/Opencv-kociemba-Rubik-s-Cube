import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
from RLFBUD import capture_faces  # 导入颜色捕捉功能
import cv2

# 颜色定义
COLORS = {
    'white':  (1.0, 1.0, 1.0),
    'yellow': (1.0, 1.0, 0.0),
    'green':  (0.0, 0.8, 0.0),
    'blue':   (0.0, 0.0, 1.0),
    'red':    (1.0, 0.0, 0.0),
    'orange': (1.0, 0.5, 0.0),
    'black':  (0.0, 0.0, 0.0)  # 纯黑色用于边框
}

# 颜色映射（从RLFBUD到我们的颜色系统）
COLOR_MAPPING = {
    'W': 'white',
    'Y': 'yellow',
    'G': 'green',
    'B': 'blue',
    'R': 'red',
    'O': 'orange',
    'U': 'black'  # 未知颜色映射为黑色
}

class CubeRotation:
    def __init__(self):
        self.angle_x = 0
        self.angle_y = 0
        self.target_x = 0
        self.target_y = 0
        self.smooth_factor = 0.1

    def update(self):
        # 平滑插值更新角度
        self.angle_x += (self.target_x - self.angle_x) * self.smooth_factor
        self.angle_y += (self.target_y - self.angle_y) * self.smooth_factor

class Cubelet:
    """表示魔方中的一个小方块"""
    def __init__(self, position, colors):
        self.position = position
        self.colors = colors
        self.rotation = [0, 0, 0]
        self.size = 0.48  # 调整大小以确保正确的间距
        self.gap = 0.02   # 方块之间的间隙
        
    def draw(self):
        glPushMatrix()
        
        # 移动到正确的位置
        glTranslatef(self.position[0], self.position[1], self.position[2])
        
        # 应用旋转
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        
        # 绘制六个面
        self._draw_faces()
        
        glPopMatrix()
    
    def _draw_faces(self):
        vertices = (
            ( self.size, -self.size, -self.size),
            ( self.size,  self.size, -self.size),
            (-self.size,  self.size, -self.size),
            (-self.size, -self.size, -self.size),
            ( self.size, -self.size,  self.size),
            ( self.size,  self.size,  self.size),
            (-self.size, -self.size,  self.size),
            (-self.size,  self.size,  self.size)
        )

        faces = (
            (0, 1, 2, 3),  # 后面 (-z)
            (3, 2, 7, 6),  # 左面 (-x)
            (6, 7, 5, 4),  # 前面 (+z)
            (4, 5, 1, 0),  # 右面 (+x)
            (1, 5, 7, 2),  # 上面 (+y)
            (4, 0, 3, 6)   # 下面 (-y)
        )

        # 绘制面
        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            color = self.colors[i]
            glColor3fv(COLORS[color])
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()

        # 绘制黑色边框 - 使用更细的线条
        glLineWidth(2.0)
        glColor3f(0.0, 0.0, 0.0)  # 纯黑色
        for i, face in enumerate(faces):
            glBegin(GL_LINE_LOOP)
            for vertex in face:
                glVertex3fv(vertices[vertex])
            glEnd()

class RubiksCube:
    """完整的魔方"""
    def __init__(self, cube_data=None):
        self.cubelets = []
        self.rotation = CubeRotation()
        if cube_data:
            self._init_cubelets_from_data(cube_data)
        else:
            self._init_cubelets()
    
    def _init_cubelets_from_data(self, cube_data):
        """从RLFBUD数据初始化魔方
        cube_data格式：每个面的数据都是从上到下、从左到右排列的9个颜色值
        """
        print("初始化魔方数据:", cube_data)
        cubelet_count = 0

        def get_face_color(face, row, col):
            """获取指定面上指定位置的颜色
            face: 面的标识符
            row, col: 从0到2的索引
            """
            if face not in cube_data:
                print(f"警告: 未找到面 {face}")
                return 'black'
            
            # 确保索引在有效范围内
            row = max(0, min(2, row))
            col = max(0, min(2, col))
            idx = row * 3 + col
            return COLOR_MAPPING[cube_data[face][idx]]

        # 创建3x3x3的魔方结构
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    colors = ['black'] * 6
                    
                    # 将-1,0,1映射到0,1,2
                    map_coord = lambda c: c + 1
                    
                    # 后面 (B)
                    if z == -1:
                        row = 2 - map_coord(y)  # 上下翻转
                        col = 2 - map_coord(x)  # 水平翻转
                        colors[0] = get_face_color('B', row, col)
                    
                    # 左面 (L)
                    if x == -1:
                        row = 2 - map_coord(y)  # 上下翻转
                        col = map_coord(z)
                        colors[1] = get_face_color('L', row, col)
                    
                    # 前面 (F)
                    if z == 1:
                        row = 2 - map_coord(y)  # 上下翻转
                        col = map_coord(x)
                        colors[2] = get_face_color('F', row, col)
                    
                    # 右面 (R)
                    if x == 1:
                        row = 2 - map_coord(y)  # 上下翻转
                        col = 2 - map_coord(z)  # 水平翻转
                        colors[3] = get_face_color('R', row, col)
                    
                    # 上面 (U)
                    if y == 1:
                        row = map_coord(z)
                        col = map_coord(x)
                        colors[4] = get_face_color('U', row, col)
                    
                    # 下面 (D) - 只需要上下翻转
                    if y == -1:
                        row = 2 - map_coord(z)  # 上下翻转
                        col = map_coord(x)      # 不需要水平翻转
                        colors[5] = get_face_color('D', row, col)
                    
                    cubelet = Cubelet((x, y, z), colors)
                    self.cubelets.append(cubelet)
                    cubelet_count += 1

        print(f"创建的小方块数量: {cubelet_count}")
    
    def _init_cubelets(self):
        """初始化标准配色的魔方"""
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    colors = ['black'] * 6
                    
                    if z == -1: colors[0] = 'blue'    # 后面
                    if x == -1: colors[1] = 'orange'  # 左面
                    if z == 1:  colors[2] = 'green'   # 前面
                    if x == 1:  colors[3] = 'red'     # 右面
                    if y == 1:  colors[4] = 'white'   # 上面
                    if y == -1: colors[5] = 'yellow'  # 下面
                    
                    cubelet = Cubelet((x, y, z), colors)
                    self.cubelets.append(cubelet)
    
    def draw(self):
        glPushMatrix()
        
        # 应用整体旋转
        glRotatef(self.rotation.angle_x, 1, 0, 0)
        glRotatef(self.rotation.angle_y, 0, 1, 0)
        
        # 绘制所有小方块
        for cubelet in self.cubelets:
            cubelet.draw()
        
        glPopMatrix()
    
    def update(self):
        self.rotation.update()

def run_3d_visualization(cube_data):
    """运行3D魔方可视化"""
    pygame.init()
    
    # 获取显示器信息
    info = pygame.display.Info()
    display = (info.current_w, info.current_h)
    window_size = (800, 600)
    
    try:
        # 初始设置为全屏
        screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL|FULLSCREEN)
        pygame.display.set_caption("3D Rubik's Cube")

        # OpenGL设置
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.8, 0.8, 0.8, 1.0)

        def setup_perspective(width, height):
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(30, width/height, 0.1, 50.0)
            glTranslatef(0.0, 0.0, -15)
            glMatrixMode(GL_MODELVIEW)

        # 初始设置视角
        setup_perspective(display[0], display[1])

        # 创建魔方实例
        cube = RubiksCube(cube_data)
        cube.rotation.target_x = 20
        cube.rotation.target_y = 30

        mouse_pressed = False
        last_mouse_pos = None
        clock = pygame.time.Clock()
        is_fullscreen = True

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_f:
                        is_fullscreen = not is_fullscreen
                        if is_fullscreen:
                            screen = pygame.display.set_mode(display, DOUBLEBUF|OPENGL|FULLSCREEN)
                            setup_perspective(display[0], display[1])
                        else:
                            screen = pygame.display.set_mode(window_size, DOUBLEBUF|OPENGL)
                            setup_perspective(window_size[0], window_size[1])
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pressed = True
                        last_mouse_pos = event.pos
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_pressed = False
                
                elif event.type == pygame.MOUSEMOTION and mouse_pressed:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    cube.rotation.target_y += dx * 0.5
                    cube.rotation.target_x += dy * 0.5
                    last_mouse_pos = event.pos

            cube.update()
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            cube.draw()
            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        print(f"运行时错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit() 