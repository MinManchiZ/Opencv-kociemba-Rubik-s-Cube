import numpy as np
import copy as cp
import os

# 图形化界面实现
import pyglet
from pyglet.gl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import locale
from pyglet.window import key

# 导入魔方求解库kociemba
import random  # 替换kociemba依赖
try:
    import kociemba
    has_kociemba = True
except ImportError:
    has_kociemba = False
    print("警告：kociemba库未安装，将使用随机步骤代替")

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")  # 强制设置英文环境

# 创建六个面，放在faces列表里，顺序为上（0），下（1），左（2），右（3），前（4），后（5）
# 初始化faces数组
def initialize_faces():
    global faces
    faces = [np.zeros((3, 3))]
    for i in range(1, 6):
        faces.append(np.ones((3, 3)) + faces[i - 1])
    return faces

# 全局变量初始化
global faces
faces = initialize_faces()

"""faces:
      0 0 0
      0 0 0
      0 0 0
2 2 2 4 4 4 3 3 3 5 5 5
2 2 2 4 4 4 3 3 3 5 5 5
2 2 2 4 4 4 3 3 3 5 5 5
      1 1 1
      1 1 1
      1 1 1
"""

t = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])


# 顺时针旋转 90 度
def clockwise(face):
    face = face.transpose().dot(t)
    return face


# 逆时针旋转 90 度
def antiClockwise(face):
    face = face.dot(t).transpose()
    return face


# 魔方顶面顺时针旋转90度
def U(FACES):
    # 上面单一个面的处理
    FACES[0] = clockwise(FACES[0])
    # 处理其它受到影响的面
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = FACES_new[4], FACES_new[2], FACES_new[5], FACES_new[3]
    FACES[4][0], FACES[2][0], FACES[5][0], FACES[3][0] = d[0], a[0], b[0], c[0]


# 顶面逆时针旋转90度
def _U(FACES):
    FACES[0] = antiClockwise(FACES[0])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = FACES_new[4], FACES_new[2], FACES_new[5], FACES_new[3]
    FACES[4][0], FACES[2][0], FACES[5][0], FACES[3][0] = b[0], c[0], d[0], a[0]


# 底面顺时针旋转90度
def D(FACES):
    FACES[1] = clockwise(FACES[1])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = FACES_new[4], FACES_new[2], FACES_new[5], FACES_new[3]
    FACES[4][2], FACES[2][2], FACES[5][2], FACES[3][2] = b[2], c[2], d[2], a[2]


def _D(FACES):
    FACES[1] = antiClockwise(FACES[1])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = FACES_new[4], FACES_new[2], FACES_new[5], FACES_new[3]
    FACES[4][2], FACES[2][2], FACES[5][2], FACES[3][2] = d[2], a[2], b[2], c[2]


# 魔方左面顺时针旋转90度
def L(FACES):
    FACES[2] = clockwise(FACES[2])
    FACES_new = cp.deepcopy(FACES)
    # 为方便处理，将a,b,c,d赋值为FACES_new中的前、底、后、顶面
    # 经过旋转后，只需要各自交换它们的第一行即可，前面的第一行给底面，底面给后面，后面给顶面，顶面给前面
    a, b, c, d = (
        clockwise(FACES_new[4]),
        clockwise(FACES_new[1]),
        antiClockwise(FACES_new[5]),
        clockwise(FACES_new[0]),
    )
    e, f, g, h = cp.deepcopy(a), cp.deepcopy(b), cp.deepcopy(c), cp.deepcopy(d)
    e[0], f[0], g[0], h[0] = d[0], a[0], b[0], c[0]
    # 交换完后，再旋转回来
    FACES[4], FACES[1], FACES[5], FACES[0] = (
        antiClockwise(e),
        antiClockwise(f),
        clockwise(g),
        antiClockwise(h),
    )


# 魔方左面逆时针旋转90度
def _L(FACES):
    FACES[2] = antiClockwise(FACES[2])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = (
        clockwise(FACES_new[4]),
        clockwise(FACES_new[1]),
        antiClockwise(FACES_new[5]),
        clockwise(FACES_new[0]),
    )
    e, f, g, h = cp.deepcopy(a), cp.deepcopy(b), cp.deepcopy(c), cp.deepcopy(d)
    e[0], f[0], g[0], h[0] = b[0], c[0], d[0], a[0]
    FACES[4], FACES[1], FACES[5], FACES[0] = (
        antiClockwise(e),
        antiClockwise(f),
        clockwise(g),
        antiClockwise(h),
    )


def R(FACES):
    FACES[3] = clockwise(FACES[3])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = (
        antiClockwise(FACES_new[4]),
        antiClockwise(FACES_new[1]),
        clockwise(FACES_new[5]),
        antiClockwise(FACES_new[0]),
    )
    e, f, g, h = cp.deepcopy(a), cp.deepcopy(b), cp.deepcopy(c), cp.deepcopy(d)
    g[0], f[0], e[0], h[0] = d[0], c[0], b[0], a[0]
    FACES[4], FACES[1], FACES[5], FACES[0] = (
        clockwise(e),
        clockwise(f),
        antiClockwise(g),
        clockwise(h),
    )


def _R(FACES):
    FACES[3] = antiClockwise(FACES[3])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = (
        antiClockwise(FACES_new[4]),
        antiClockwise(FACES_new[1]),
        clockwise(FACES_new[5]),
        antiClockwise(FACES_new[0]),
    )
    e, f, g, h = cp.deepcopy(a), cp.deepcopy(b), cp.deepcopy(c), cp.deepcopy(d)
    f[0], g[0], h[0], e[0] = a[0], b[0], c[0], d[0]
    FACES[4], FACES[1], FACES[5], FACES[0] = (
        clockwise(e),
        clockwise(f),
        antiClockwise(g),
        clockwise(h),
    )


def F(FACES):
    FACES[4] = clockwise(FACES[4])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = (
        clockwise(clockwise(FACES_new[0])),
        FACES_new[1],
        antiClockwise(FACES_new[2]),
        clockwise(FACES_new[3]),
    )
    e, f, g, h = cp.deepcopy(a), cp.deepcopy(b), cp.deepcopy(c), cp.deepcopy(d)
    e[0], g[0], f[0], h[0] = c[0], b[0], d[0], a[0]
    FACES[0], FACES[1], FACES[2], FACES[3] = (
        clockwise(clockwise(e)),
        f,
        clockwise(g),
        antiClockwise(h),
    )


def _F(FACES):
    FACES[4] = antiClockwise(FACES[4])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = (
        clockwise(clockwise(FACES_new[0])),
        FACES_new[1],
        antiClockwise(FACES_new[2]),
        clockwise(FACES_new[3]),
    )
    e, f, g, h = cp.deepcopy(a), cp.deepcopy(b), cp.deepcopy(c), cp.deepcopy(d)
    g[0], f[0], h[0], e[0] = a[0], c[0], b[0], d[0]
    FACES[0], FACES[1], FACES[2], FACES[3] = (
        clockwise(clockwise(e)),
        f,
        clockwise(g),
        antiClockwise(h),
    )


def B(FACES):
    FACES[5] = clockwise(FACES[5])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = (
        FACES_new[0],
        clockwise(clockwise(FACES_new[1])),
        clockwise(FACES_new[2]),
        antiClockwise(FACES_new[3]),
    )
    e, f, g, h = cp.deepcopy(a), cp.deepcopy(b), cp.deepcopy(c), cp.deepcopy(d)
    g[0], f[0], h[0], e[0] = a[0], c[0], b[0], d[0]
    FACES[0], FACES[1], FACES[2], FACES[3] = (
        e,
        clockwise(clockwise(f)),
        antiClockwise(g),
        clockwise(h),
    )


def _B(FACES):
    FACES[5] = antiClockwise(FACES[5])
    FACES_new = cp.deepcopy(FACES)
    a, b, c, d = (
        FACES_new[0],
        clockwise(clockwise(FACES_new[1])),
        clockwise(FACES_new[2]),
        antiClockwise(FACES_new[3]),
    )
    e, f, g, h = cp.deepcopy(a), cp.deepcopy(b), cp.deepcopy(c), cp.deepcopy(d)
    e[0], g[0], f[0], h[0] = c[0], b[0], d[0], a[0]
    FACES[0], FACES[1], FACES[2], FACES[3] = (
        e,
        clockwise(clockwise(f)),
        antiClockwise(g),
        clockwise(h),
    )


# 把魔方2D数组转换成字符串输出
def toString(FACES):
    os.system("cls")
    for i in range(3):
        print("     ", int(FACES[0][i][0]), int(FACES[0][i][1]), int(FACES[0][i][2]))
    for i in range(3):
        print(int(FACES[2][i][0]), int(FACES[2][i][1]), int(FACES[2][i][2]), end=" ")
        print(int(FACES[4][i][0]), int(FACES[4][i][1]), int(FACES[4][i][2]), end=" ")
        print(int(FACES[3][i][0]), int(FACES[3][i][1]), int(FACES[3][i][2]), end=" ")
        print(int(FACES[5][i][0]), int(FACES[5][i][1]), int(FACES[5][i][2]))
    for i in range(3):
        print("     ", int(FACES[1][i][0]), int(FACES[1][i][1]), int(FACES[1][i][2]))
    print()

# 设置faces数组，可以从外部导入
def set_faces(new_faces):
    global faces
    faces = new_faces
    return faces

# 颜色映射函数（根据数值生成颜色）
def get_color(value):
    colors = [
        [1.0, 0.0, 0.0],  # 红色（对应0）
        [0.0, 1.0, 0.0],  # 绿色（对应1）
        [0.0, 0.0, 1.0],  # 蓝色（对应2）
        [1.0, 1.0, 0.0],  # 黄色（对应3）
        [1.0, 0.5, 0.0],  # 橙色（对应4）
        [1.0, 1.0, 1.0],  # 白色（对应5）
    ]
    return colors[int(value) % len(colors)]


config = pyglet.gl.Config(double_buffer=True)
# 创建窗口
window = pyglet.window.Window(
    width=800, height=600, caption="3D Rubik's Cube", config=config
)

# 把faces数组映射成大写字母串以输入kociemba
FACE_MAP = {
    0: "U",  # 上面(Up)
    1: "D",  # 下面(Down)
    2: "L",  # 左面(Left)
    3: "R",  # 右面(Right)
    4: "F",  # 前面(Front)
    5: "B",  # 后面(Back)
}

COLOR_MAP = {
    0: "U",  # 红色对应上面
    1: "D",  # 绿色对应下面
    2: "L",  # 蓝色对应左面
    3: "R",  # 黄色对应右面
    4: "F",  # 橙色对应前面
    5: "B",  # 白色对应后面
}

def face_to_string(face):
    result = ""
    for row in face:
        for value in row:
            result += COLOR_MAP[int(value) % 6]
    return result

# 得到魔方的字符串表示用于输入kociemba求解
def encode_cube(faces):
    # 按照kociemba的顺序: U, R, F, D, L, B
    cube_str = ""
    cube_str += face_to_string(faces[0])  # U
    cube_str += face_to_string(faces[3])  # R
    cube_str += face_to_string(faces[4])  # F
    cube_str += face_to_string(faces[1])  # D
    cube_str += face_to_string(faces[2])  # L
    cube_str += face_to_string(faces[5])  # B
    return cube_str


def solve_cube(faces):
    if has_kociemba:
        try:
            cube_str = encode_cube(faces)
            solution = kociemba.solve(cube_str)
            return solution.split()  # 返回步骤列表，如 ["R", "U'", "F2"]
        except Exception as e:
            print(f"kociemba求解出错: {e}")
            print("使用随机步骤代替")
    
    # 如果kociemba不可用或出错，返回随机步骤
    possible_moves = ["U", "U'", "U2", "D", "D'", "D2", 
                     "L", "L'", "L2", "R", "R'", "R2",
                     "F", "F'", "F2", "B", "B'", "B2"]
    # 生成10-15步的随机解法
    num_steps = random.randint(10, 15)
    solution = [random.choice(possible_moves) for _ in range(num_steps)]
    return solution  # 返回步骤列表，如 ["R", "U'", "F2"]

# 旋转函数映射表
MOVE_MAP = {
    "U": U,    "U'": _U,  "U2": lambda f: (U(f), U(f)),
    "D": D,    "D'": _D,  "D2": lambda f: (D(f), D(f)),
    "L": L,    "L'": _L,  "L2": lambda f: (L(f), L(f)),
    "R": R,    "R'": _R,  "R2": lambda f: (R(f), R(f)),
    "F": F,    "F'": _F,  "F2": lambda f: (F(f), F(f)),
    "B": B,    "B'": _B,  "B2": lambda f: (B(f), B(f))
}

is_solving = False  # 标记是否正在执行解法
solution_steps = []  # 存储待执行的解法步骤
# 键盘控制
@window.event
def on_key_press(symbol, modifiers):
    global faces, is_solving, solution_steps
    if symbol == pyglet.window.key.F:
        # 检查是否同时按下了Shift键
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _F(faces)
        else:
            F(faces)
    elif symbol == pyglet.window.key.B:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _B(faces)
        else:
            B(faces)
    elif symbol == pyglet.window.key.L:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _L(faces)
        else:
            L(faces)
    elif symbol == pyglet.window.key.R:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _R(faces)
        else:
            R(faces)
    elif symbol == pyglet.window.key.U:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _U(faces)
        else:
            U(faces)
    elif symbol == pyglet.window.key.D:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _D(faces)
        else:
            D(faces)
    elif symbol == key.ENTER and not is_solving:
        solution = solve_cube(faces)
        print("解法：", solution)
        solution_steps = solution.copy()
        is_solving = True
        # 安排第一个步骤
        pyglet.clock.schedule_once(execute_step, 0.5)

    toString(faces)
    window.invalid = True  # 重绘窗口


def execute_step(dt):
    global faces, is_solving, solution_steps

    if solution_steps:
        move = solution_steps.pop(0)
        MOVE_MAP[move](faces)
        print("执行:", move)
        window.invalid = True
        # 安排下一步
        pyglet.clock.schedule_once(execute_step, 0.5)
    else:
        is_solving = False


# 显示3D魔方
@window.event
def on_draw():
    # 清除缓冲时添加深度缓冲清除
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # 修改清除方式

    # window.clear()
    glEnable(GL_DEPTH_TEST)

    # 设置投影矩阵
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, window.width / window.height, 0.1, 50.0)

    # 设置模型视图矩阵
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -5)
    glRotatef(30, 1, 0, 0)  # 俯视角30度
    glRotatef(-45, 0, 1, 0)  # 水平旋转-45度

    # 绘制可见的三个面（前、右、上）
    draw_face(4, position=(0, 0, 0.5))  # 前面
    draw_face(3, position=(0.5, 0, 0))  # 右面
    draw_face(0, position=(0, 0.5, 0))  # 上面

    # 添加操作提示
    label = pyglet.text.Label(
        "按下F/B/L/R/U/D顺时针转动前/后/左/右/上/下面；按下Shift+字母逆时针转动；按下回车求解",
        font_size=14,
        x=10,
        y=10,
        color=(255, 255, 255, 255),
    )
    label.draw()

# 绘制每一面
def draw_face(face_idx, position):
    # 获取面数据,并根据面的位置进行旋转
    if face_idx == 3: 
        face_data = np.rot90(faces[face_idx].T,k=2)
    elif face_idx == 0: 
        face_data = faces[face_idx].T
    else:
        face_data = np.rot90(faces[face_idx],k=-1)
    x, y, z = position

    # 遍历3x3网格
    for i in range(3):
        for j in range(3):
            # 计算每个小格子的位置
            offset_x = (i - 1) * 0.33
            offset_y = (j - 1) * 0.33

            # 设置颜色
            glColor3f(*get_color(face_data[i][j]))

            # 绘制四边形
            glBegin(GL_QUADS)
            if face_idx == 4:  # 前面
                glVertex3f(x + offset_x - 0.15, y + offset_y - 0.15, z)
                glVertex3f(x + offset_x + 0.15, y + offset_y - 0.15, z)
                glVertex3f(x + offset_x + 0.15, y + offset_y + 0.15, z)
                glVertex3f(x + offset_x - 0.15, y + offset_y + 0.15, z)
            elif face_idx == 3:  # 右面
                glVertex3f(x, y + offset_y - 0.15, z + offset_x - 0.15)
                glVertex3f(x, y + offset_y - 0.15, z + offset_x + 0.15)
                glVertex3f(x, y + offset_y + 0.15, z + offset_x + 0.15)
                glVertex3f(x, y + offset_y + 0.15, z + offset_x - 0.15)
            elif face_idx == 0:  # 上面
                glVertex3f(x + offset_x - 0.15, y, z + offset_y - 0.15)
                glVertex3f(x + offset_x + 0.15, y, z + offset_y - 0.15)
                glVertex3f(x + offset_x + 0.15, y, z + offset_y + 0.15)
                glVertex3f(x + offset_x - 0.15, y, z + offset_y + 0.15)
            glEnd()


def main():
    # 如果脚本被直接运行，则初始化faces
    global faces
    if __name__ == "__main__":
        faces = initialize_faces()
    toString(faces)
    # 只有直接运行时才启动pyglet应用
    if __name__ == "__main__":
        pyglet.app.run()

if __name__ == "__main__":
    main()
