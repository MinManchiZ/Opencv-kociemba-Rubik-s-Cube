#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import random
import pyglet
from pyglet.window import key
from collections import defaultdict
import datetime
import numpy as np
import copy as cp
import locale
import sys

# 标记是否导入了高级求解器
has_advanced_solver = False

# 尝试导入简化的高级求解器
try:
    from simple_cube_solver import solve_cube_advanced as simple_advanced_solver
    has_advanced_solver = True
    print("成功导入简化高级求解器")
except ImportError:
    print("无法导入简化高级求解器，将使用基本算法")
    simple_advanced_solver = None

# 尝试导入kociemba求解器
try:
    import kociemba
    print("成功导入kociemba求解器")
except ImportError:
    print("未安装kociemba库，将使用替代算法")
    kociemba = None

# 图形化界面实现
import pyglet
from pyglet.gl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import locale
from pyglet.window import key

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")  # 强制设置英文环境

# 定义一个简化版的保存解法步骤到文件函数，避免循环引用问题
def save_solution_to_file(steps):
    """将解法步骤保存到文件，同时进行校验"""
    if not steps:
        print("没有执行任何步骤，不保存文件")
        return
    
    # 验证步骤的有效性
    valid_steps = []
    invalid_steps = []
    for step in steps:
        if step in MOVE_MAP or step in ["U2", "D2", "L2", "R2", "F2", "B2"]:
            valid_steps.append(step)
        else:
            invalid_steps.append(step)
    
    if invalid_steps:
        print(f"警告: 发现 {len(invalid_steps)} 个无效步骤，这些步骤不会被保存")
        print(f"无效步骤: {invalid_steps}")
    
    # 只保存有效步骤
    if not valid_steps:
        print("没有有效的步骤可以保存")
        return
    
    # 创建文件名，使用时间戳
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cube_solution_{timestamp}.txt"
    
    # 在终端显示完整解法
    print(f"\n完整魔方解法 - 共 {len(valid_steps)} 步有效操作（已保存到文件: {filename}）")
    print(f"完整步骤: {' '.join(valid_steps)}")
    
    # 编写步骤含义映射表
    step_meaning = {
        "U": "顶面顺时针旋转",
        "U'": "顶面逆时针旋转",
        "U2": "顶面旋转180度",
        "D": "底面逆时针旋转", 
        "D'": "底面顺时针旋转",
        "D2": "底面旋转180度",
        "L": "左面顺时针旋转",
        "L'": "左面逆时针旋转",
        "L2": "左面旋转180度",
        "R": "右面顺时针旋转",
        "R'": "右面逆时针旋转",
        "R2": "右面旋转180度",
        "F": "前面顺时针旋转",
        "F'": "前面逆时针旋转",
        "F2": "前面旋转180度",
        "B": "后面顺时针旋转",
        "B'": "后面逆时针旋转",
        "B2": "后面旋转180度"
    }
    
    # 写入文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write(f" 魔方解法步骤 - 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"总步数: {len(valid_steps)}\n\n")
        
        f.write("█ 步骤详情:\n")
        f.write("─" * 40 + "\n")
        
        # 按照步骤类型进行分组
        step_types = {}
        for step in valid_steps:
            step_type = step[0]  # 取第一个字符作为类型 (U, D, L, R, F, B)
            if step_type not in step_types:
                step_types[step_type] = []
            step_types[step_type].append(step)
        
        # 显示分组统计
        f.write("【步骤类型统计】\n")
        for step_type in sorted(step_types.keys()):
            count = len(step_types[step_type])
            f.write(f"  {step_type}类动作: {count}步 ({(count/len(valid_steps))*100:.1f}%)\n")
        f.write("\n")
        
        # 写入所有步骤，每20步一组，带计数器
        f.write("【详细步骤列表】\n")
        for i, step in enumerate(valid_steps):
            # 添加组编号，每20步一组
            if i % 20 == 0:
                if i > 0:
                    f.write("\n")  # 每组之间空一行
                f.write(f"第 {i//20 + 1} 组:\n")
            
            # 格式化每一步，包含序号、动作符号和含义
            step_str = f"  {i+1:3d}: {step:3s} - {step_meaning.get(step, '未知步骤')}\n"
            f.write(step_str)
        
        # 再写入紧凑版本，方便复制，但每10步一行
        f.write("\n\n" + "=" * 50 + "\n")
        f.write("【紧凑版本步骤 - 每行10步】\n")
        f.write("=" * 50 + "\n\n")
        
        # 每10步一行，带行号
        for i in range(0, len(valid_steps), 10):
            end = min(i + 10, len(valid_steps))
            line_steps = valid_steps[i:end]
            line_nr = i // 10 + 1
            f.write(f"{line_nr:2d}: {' '.join(line_steps)}\n")
        
        # 添加一个完全紧凑的版本，用于直接复制所有步骤
        f.write("\n\n" + "=" * 50 + "\n")
        f.write("【完整步骤 - 一次性复制】\n")
        f.write("=" * 50 + "\n\n")
        all_steps = " ".join(valid_steps)
        f.write(all_steps + "\n")
    
    print(f"解法已保存到文件: {filename}")
    return filename

# 在终端显示完整历史步骤 - 简化版
def show_full_history(steps):
    """在终端以简化形式显示完整的历史步骤"""
    if not steps:
        print("无历史步骤记录")
        return
    
    print(f"\n===== 完整历史步骤记录 =====")
    print(f"总共执行了 {len(steps)} 步操作")
    print("=" * 50)
    
    # 每行显示10个步骤
    line_width = 10
    
    # 显示步骤
    for i in range(0, len(steps), line_width):
        end = min(i + line_width, len(steps))
        line_steps = steps[i:end]
        step_line = ""
        for j, step in enumerate(line_steps):
            step_line += f"{i+j+1}:{step} "
        print(step_line)
    
    # 提供保存建议
    print("\n提示: 按P键可以保存完整历史记录到文件")
    
    # 打印当前魔方状态
    if is_init_state(faces):
        print("当前魔方已还原完成！")
    else:
        print("当前魔方尚未还原，按Enter键继续求解")
    
    print("=" * 50)

# 创建六个面，放在faces列表里，顺序为上（0），下（1），左（2），右（3），前（4），后（5）
# 初始化faces数组
def initialize_faces():
    global faces
    faces = [np.zeros((3, 3))]
    for i in range(1, 6):
        faces.append(np.ones((3, 3)) + faces[i - 1])
    return faces

# 全局变量初始化
global faces, debug_mode, step_history, total_step_count
faces = initialize_faces()
debug_mode = True  # 设置为True启用详细调试信息
step_history = []  # 存储已执行的步骤历史记录
total_step_count = 0  # 记录总步数，用于显示解魔方的进度

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


# 确保数据是numpy数组类型
def ensure_numpy_array(data):
    if isinstance(data, list):
        return np.array(data)
    return data


# 魔方顶面顺时针旋转90度（从顶面看）
def U(FACES):
    # 上面本身顺时针旋转
    FACES[0] = clockwise(ensure_numpy_array(FACES[0]))
    # 处理其它受到影响的面
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
    a, b, c, d = FACES_new[4], FACES_new[2], FACES_new[5], FACES_new[3]
    # 顺时针旋转：前→左→后→右→前（从顶面看）
    FACES[4][0], FACES[2][0], FACES[5][0], FACES[3][0] = d[0], a[0], b[0], c[0]


# 顶面逆时针旋转90度（从顶面看）
def _U(FACES):
    # 上面本身逆时针旋转
    FACES[0] = antiClockwise(ensure_numpy_array(FACES[0]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
    a, b, c, d = FACES_new[4], FACES_new[2], FACES_new[5], FACES_new[3]
    # 逆时针旋转：前→右→后→左→前（从顶面看）
    FACES[4][0], FACES[2][0], FACES[5][0], FACES[3][0] = b[0], c[0], d[0], a[0]


# 底面逆时针旋转90度（从底面看）- 按下D键触发
def D(FACES):
    # 底面逆时针旋转（从底面看）
    # 更新底面（1号面），逆时针旋转
    FACES[1] = antiClockwise(ensure_numpy_array(FACES[1]))
    
    # 存储周围面的底部行
    front_row = cp.deepcopy(FACES[4][2]) # 前面底行
    right_row = cp.deepcopy(FACES[3][2]) # 右面底行
    back_row = cp.deepcopy(FACES[5][2])  # 后面底行
    left_row = cp.deepcopy(FACES[2][2])  # 左面底行

    # 从底面逆时针方向更新周围面的底行
    # 前→左→后→右→前
    FACES[2][2] = cp.deepcopy(front_row)  # 左面底行 = 前面底行
    FACES[5][2] = cp.deepcopy(left_row)   # 后面底行 = 左面底行
    FACES[3][2] = cp.deepcopy(back_row)   # 右面底行 = 后面底行
    FACES[4][2] = cp.deepcopy(right_row)  # 前面底行 = 右面底行


# 底面顺时针旋转90度（从底面看）- 按下Shift+D键触发
def _D(FACES):
    # 底面顺时针旋转（从底面看）
    # 更新底面（1号面），顺时针旋转
    FACES[1] = clockwise(ensure_numpy_array(FACES[1]))
    
    # 存储周围面的底部行
    front_row = cp.deepcopy(FACES[4][2]) # 前面底行
    right_row = cp.deepcopy(FACES[3][2]) # 右面底行
    back_row = cp.deepcopy(FACES[5][2])  # 后面底行
    left_row = cp.deepcopy(FACES[2][2])  # 左面底行

    # 从底面顺时针方向更新周围面的底行
    # 前→右→后→左→前
    FACES[3][2] = cp.deepcopy(front_row)  # 右面底行 = 前面底行
    FACES[5][2] = cp.deepcopy(right_row)  # 后面底行 = 右面底行
    FACES[2][2] = cp.deepcopy(back_row)   # 左面底行 = 后面底行
    FACES[4][2] = cp.deepcopy(left_row)   # 前面底行 = 左面底行


# 魔方左面顺时针旋转90度（从左面看）
def L(FACES):
    # 左面本身顺时针旋转
    FACES[2] = clockwise(ensure_numpy_array(FACES[2]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
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


# 魔方左面逆时针旋转90度（从左面看）
def _L(FACES):
    # 左面本身逆时针旋转
    FACES[2] = antiClockwise(ensure_numpy_array(FACES[2]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
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


# 右面顺时针旋转90度（从右面看）
def R(FACES):
    # 右面本身顺时针旋转
    FACES[3] = clockwise(ensure_numpy_array(FACES[3]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
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


# 右面逆时针旋转90度（从右面看）
def _R(FACES):
    # 右面本身逆时针旋转
    FACES[3] = antiClockwise(ensure_numpy_array(FACES[3]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
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


# 前面顺时针旋转90度（从前面看）
def F(FACES):
    # 前面本身顺时针旋转
    FACES[4] = clockwise(ensure_numpy_array(FACES[4]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
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


# 前面逆时针旋转90度（从前面看）
def _F(FACES):
    # 前面本身逆时针旋转
    FACES[4] = antiClockwise(ensure_numpy_array(FACES[4]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
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


# 后面顺时针旋转90度（从后面看）
def B(FACES):
    # 后面本身顺时针旋转
    FACES[5] = clockwise(ensure_numpy_array(FACES[5]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
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


# 后面逆时针旋转90度（从后面看）
def _B(FACES):
    # 后面本身逆时针旋转
    FACES[5] = antiClockwise(ensure_numpy_array(FACES[5]))
    FACES_new = cp.deepcopy(FACES)
    
    # 确保所有面都是numpy数组
    for i in range(6):
        FACES_new[i] = ensure_numpy_array(FACES_new[i])
    
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
    global faces, step_history
    
    # 检查输入数据的有效性
    if len(new_faces) != 6:
        print(f"错误: 魔方应有6个面，但提供了{len(new_faces)}个面")
        return faces
        
    # 检查每个面是否是3x3的
    for i, face in enumerate(new_faces):
        if not isinstance(face, (list, np.ndarray)) or face.shape != (3, 3):
            print(f"错误: 第{i}个面不是3x3格式")
            return faces
    
    # 设置新魔方状态
    faces = new_faces
    
    # 当导入新的魔方状态时，清空历史记录
    step_history = []
    
    # 检查导入的魔方状态
    state_info = check_cube_state(faces)
    
    # 如果新导入的是已完成状态，提示用户
    if state_info["is_solved"]:
        print("导入的魔方状态是已完成状态（每个面颜色一致）")
    else:
        print("导入的魔方状态需要求解")
    
    # 检查颜色分布是否正确
    if not state_info["valid_colors"]:
        print("警告: 导入的魔方颜色分布不正确，可能无法求解")
    
    # 更新窗口显示
    toString(faces)
    window.invalid = True
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

# 创建窗口 - 使用1920x1080分辨率
window_width = 1920
window_height = 1080

# 创建窗口
window = pyglet.window.Window(
    width=window_width, height=window_height, 
    caption="3D Rubik's Cube", 
    config=config,
    resizable=True  # 允许用户调整窗口大小
)

# 获取窗口的实际尺寸，在某些系统上可能会被调整
window_width = window.width
window_height = window.height

# 添加窗口大小变化事件处理
@window.event
def on_resize(width, height):
    # 更新窗口尺寸变量
    global window_width, window_height
    window_width = width
    window_height = height
    
    # 更新透视投影
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    
    # 必须返回True以允许事件继续传播
    return True

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
    """将一个面的数值转换为字符串，确保正确映射颜色"""
    result = ""
    for row in face:
        for value in row:
            # 确保使用固定映射 - 按中心块实际位置确定面
            color_int = int(value) % 6
            result += FACE_MAP[color_int]
    return result

# 修正后的encode_cube函数，保证kociemba能正确识别魔方
def encode_cube(faces):
    """
    使用标准的kociemba颜色映射生成魔方字符串
    标准顺序：U, R, F, D, L, B (上右前下左后)
    """
    # 检查中心块，确认每个面的实际颜色
    centers = []
    for i in range(6):
        centers.append(int(faces[i][1][1]))
    
    # 调试输出
    print(f"中心块颜色值: {centers}")
    print(f"FACE_MAP: {FACE_MAP}")
    
    # 按照kociemba的顺序: U, R, F, D, L, B 组装字符串
    cube_str = ""
    # 上面
    cube_str += face_to_string(faces[0])  # U
    # 右面
    cube_str += face_to_string(faces[3])  # R
    # 前面 
    cube_str += face_to_string(faces[4])  # F
    # 下面
    cube_str += face_to_string(faces[1])  # D
    # 左面
    cube_str += face_to_string(faces[2])  # L
    # 后面
    cube_str += face_to_string(faces[5])  # B
    
    return cube_str

# 简单高效的魔方求解函数，直接使用kociemba库
def solve_cube(faces):
    """使用kociemba求解魔方，返回求解步骤列表"""
    try:
        # 获取魔方状态字符串
        cube_str = encode_cube(faces)
        print(f"求解魔方: {cube_str}")
        
        # 使用kociemba求解
        solution = kociemba.solve(cube_str)
        print(f"求解成功: {solution}")
        return solution.split()  # 返回步骤列表，如 ["R", "U'", "F2"]
    except Exception as e:
        print(f"求解出错: {str(e)}")
        print("错误详情:", repr(e))
        print("魔方状态字符串:", repr(cube_str))
        
        # 尝试使用修复后的字符串
        try:
            print("尝试修复魔方状态...")
            fixed_str = fix_cube_string(cube_str)
            print(f"修复后的字符串: {fixed_str}")
            solution = kociemba.solve(fixed_str)
            print(f"修复后求解成功: {solution}")
            return solution.split()
        except Exception as e2:
            print(f"修复尝试失败: {str(e2)}")
            return []

# 尝试修复魔方状态字符串
def fix_cube_string(cube_str):
    """尝试修复魔方状态字符串，以便kociemba可以识别"""
    # 确保字符串长度为54
    if len(cube_str) != 54:
        raise ValueError(f"魔方字符串长度必须为54，当前长度为{len(cube_str)}")
    
    # 这里用已知的有效配置替换
    # 上(U), 右(R), 前(F), 下(D), 左(L), 后(B)
    standard_centers = "URFDLB"
    
    # 创建一个映射字典，将当前字符映射到标准字符
    char_map = {}
    
    # 确定中心块位置 (这些索引是固定的)
    center_indices = [4, 13, 22, 31, 40, 49]  # U, R, F, D, L, B 的中心位置
    
    # 从字符串中获取当前中心块字符
    current_centers = [cube_str[i] for i in center_indices]
    print(f"当前中心块字符: {current_centers}")
    
    # 创建映射
    for curr, std in zip(current_centers, standard_centers):
        if curr not in char_map:
            char_map[curr] = std
    
    # 应用映射替换整个字符串
    fixed_str = ""
    for char in cube_str:
        fixed_str += char_map.get(char, char)
    
    return fixed_str

# 使用solve_cube函数开始魔方求解过程
def start_cube_solving(cube_faces):
    """开始魔方求解过程"""
    global solution_steps, step_history, is_solving
    
    # 获取解法步骤
    steps = solve_cube(cube_faces)
    
    if steps:
        # 有解法步骤，开始执行
        solution_steps = steps
        step_history = []  # 清空历史记录
        is_solving = True
        # 开始执行第一步
        pyglet.clock.schedule_once(execute_step, 0.02)
        return True
    else:
        # 没有解法步骤
        print("无法求解当前魔方状态")
        return False

# 检查是否为初始状态 
def is_init_state(faces):
    """检查魔方是否为有效的完成状态（每个面的颜色一致）"""
    # 检查每个面是否颜色一致（而不是与初始状态比较）
    for face_idx in range(6):
        face = ensure_numpy_array(faces[face_idx])
        # 获取该面的中心块颜色作为参考
        center_color = face[1][1]
        # 检查该面的所有块是否与中心块颜色相同
        for i in range(3):
            for j in range(3):
                if face[i][j] != center_color:
                    return False  # 发现不一致的颜色
    
    # 所有面的颜色都一致，表示魔方已还原（每个面都是单一颜色）
    return True

# 生成随机解法步骤
def generate_random_solution():
    """生成随机解法步骤"""
    possible_moves = ["U", "U'", "U2", "D", "D'", "D2", 
                     "L", "L'", "L2", "R", "R'", "R2",
                     "F", "F'", "F2", "B", "B'", "B2"]
    # 生成较长的随机解法(40-60步)，确保足够多的步数
    num_steps = random.randint(40, 60)
    return [random.choice(possible_moves) for _ in range(num_steps)]

# 生成基本还原序列
def generate_basic_solution():
    """生成基本还原序列，用于kociemba失败时"""
    # 生成一个包含魔方常用公式的序列
    steps = []
    
    # 基本移动序列
    basic_moves = ["U", "D", "L", "R", "F", "B", 
                  "U'", "D'", "L'", "R'", "F'", "B'",
                  "U2", "D2", "L2", "R2", "F2", "B2"]
    
    # 常用的公式
    formulas = [
        # 顶层十字
        ["F", "R", "U", "R'", "U'", "F'"],
        
        # 顶层角块
        ["R", "U", "R'", "U'"],
        ["R", "U", "R'", "U'", "R", "U", "R'", "U'"],
        
        # 第二层
        ["U", "R", "U'", "R'", "U'", "F'", "U", "F"],
        ["U'", "L'", "U", "L", "U", "F", "U'", "F'"],
        
        # 底层十字
        ["F", "R", "U", "R'", "U'", "F'"],
        ["F", "U", "R", "U'", "R'", "F'"],
        
        # 底层角块定位
        ["R", "U", "R'", "U'", "R", "U", "R'", "U'"],
        ["R", "U", "R'", "U", "R", "U2", "R'"],
        
        # PLL
        ["R", "U'", "R", "U", "R", "U", "R", "U'", "R'", "U'", "R2"],
        ["R2", "U", "R", "U", "R'", "U'", "R'", "U'", "R'", "U", "R'"]
    ]
    
    # 添加3-5个随机公式
    num_formulas = random.randint(3, 5)
    for _ in range(num_formulas):
        steps.extend(random.choice(formulas))
        
    # 添加一些随机的基本移动
    num_basic_moves = random.randint(10, 15)
    for _ in range(num_basic_moves):
        steps.append(random.choice(basic_moves))
    
    # 补充到至少40步
    while len(steps) < 40:
        steps.append(random.choice(basic_moves))
    
    return steps

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

# 添加一个检查魔方状态的函数
def check_cube_state(faces):
    """检查并返回魔方的当前状态信息"""
    result = {}
    
    # 检查是否为已完成状态（每个面颜色一致）
    result["is_solved"] = is_init_state(faces)
    
    # 检查每个面的中心块颜色
    center_colors = {}
    for face_idx, face_name in enumerate(["上", "下", "左", "右", "前", "后"]):
        center_colors[face_name] = int(faces[face_idx][1][1])
    result["centers"] = center_colors
    
    # 检查是否有重复的中心颜色
    result["unique_centers"] = len(set(center_colors.values())) == 6
    
    # 统计每种颜色的数量
    color_counts = {}
    for face in faces:
        for row in face:
            for color in row:
                color_int = int(color)
                if color_int not in color_counts:
                    color_counts[color_int] = 0
                color_counts[color_int] += 1
    result["color_counts"] = color_counts
    
    # 打印状态信息
    print("\n--- 魔方状态检查 ---")
    print(f"是否已完成（各面颜色一致）: {'是' if result['is_solved'] else '否'}")
    print(f"中心块颜色是否都不同: {'是' if result['unique_centers'] else '否'}")
    print("中心块颜色:")
    for face, color in result["centers"].items():
        print(f"  {face}面: {color}")
    print("各颜色数量:")
    for color, count in result["color_counts"].items():
        print(f"  颜色 {color}: {count} 块")
    
    # 检查颜色数量是否正确（每种颜色应有9块）
    valid_colors = True
    for color, count in result["color_counts"].items():
        if count != 9:
            valid_colors = False
            print(f"  警告: 颜色 {color} 有 {count} 块，应为9块")
    
    print(f"颜色数量是否正确: {'是' if valid_colors else '否'}")
    print("----------------------")
    
    result["valid_colors"] = valid_colors
    return result

# 修改键盘控制函数，添加状态检查功能
@window.event
def on_key_press(symbol, modifiers):
    global faces, is_solving, solution_steps, step_history, total_step_count
    
    # 如果正在执行解法，不响应键盘操作（除了ESC键中断）
    if is_solving and symbol != key.ESCAPE:
        print("正在执行解法，请等待完成或按ESC中断...")
        return
    
    # ESC键中断当前解法过程
    if symbol == key.ESCAPE and is_solving:
        print("用户中断解法执行")
        is_solving = False
        solution_steps = []
        return
    
    # N键 - 运行外部程序拍摄新魔方
    elif symbol == key.N:
        # 停止当前任何求解过程
        if is_solving:
            is_solving = False
            solution_steps = []
        
        print("\n===== 启动main.py拍摄新的魔方 =====")
        try:
            import subprocess
            import os
            
            print("正在启动main.py拍摄魔方并加载...")
            print("main.py启动后当前窗口将自动关闭")
            
            # 使用subprocess运行main.py
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
            
            if os.path.exists(script_path):
                # 以非阻塞方式启动main.py
                subprocess.Popen(["python", script_path])
                
                # 关闭当前窗口并退出
                print("main.py已启动，正在关闭当前窗口...")
                window.close()
                pyglet.app.exit()
            else:
                print(f"错误: 未找到main.py文件，请确保该文件位于: {script_path}")
        except Exception as e:
            print(f"启动main.py时出错: {str(e)}")
        
        print("===== 结束main.py调用 =====\n")
        window.invalid = True  # 重绘窗口
    elif symbol == pyglet.window.key.F:
        # 检查是否同时按下了Shift键
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _F(faces)
            step_history.append("F'")
        else:
            F(faces)
            step_history.append("F")
    elif symbol == pyglet.window.key.B:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _B(faces)
            step_history.append("B'")
        else:
            B(faces)
            step_history.append("B")
    elif symbol == pyglet.window.key.L:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _L(faces)
            step_history.append("L'")
        else:
            L(faces)
            step_history.append("L")
    elif symbol == pyglet.window.key.R:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _R(faces)
            step_history.append("R'")
        else:
            R(faces)
            step_history.append("R")
    elif symbol == pyglet.window.key.U:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _U(faces)
            step_history.append("U'")
        else:
            U(faces)
            step_history.append("U")
    elif symbol == pyglet.window.key.D:
        if modifiers & pyglet.window.key.MOD_SHIFT:
            _D(faces)
            step_history.append("D'")
        else:
            D(faces)
            step_history.append("D")
    elif symbol == key.ENTER and not is_solving:
        # 重置retry计数器，避免之前的尝试影响新的解法
        if hasattr(execute_step, 'retry_count'):
            execute_step.retry_count = 0
        
        try:
            # 获取kociemba库格式的魔方状态字符串
            cube_str = encode_cube(faces)
            print(f"求解魔方: {cube_str}")
            
            # 尝试直接使用kociemba求解
            try:
                solution = kociemba.solve(cube_str)
                print(f"求解成功: {solution}")
                
                solution_steps = solution.split()
                step_history = []  # 清空历史记录
                is_solving = True
                # 开始执行第一步，立即执行不等待
                pyglet.clock.schedule_once(execute_step, 0.01)
                
            except Exception as e:
                print(f"直接求解失败: {str(e)}")
                print("尝试使用修复后的字符串...")
                
                try:
                    # 生成标准化的魔方状态
                    fixed_str = fix_cube_string(cube_str)
                    print(f"修复后的字符串: {fixed_str}")
                    
                    solution = kociemba.solve(fixed_str)
                    print(f"修复后求解成功: {solution}")
                    
                    solution_steps = solution.split()
                    step_history = []  # 清空历史记录
                    is_solving = True
                    # 立即执行
                    pyglet.clock.schedule_once(execute_step, 0.01)
                    
                except Exception as e2:
                    print(f"修复后仍然失败: {str(e2)}")
                    print("尝试使用简单方案...")
                    
                    # 最后的备选方案：使用一系列基本操作
                    print("生成基本解法步骤...")
                    solution_steps = generate_basic_solution()
                    step_history = []
                    is_solving = True
                    # 立即执行
                    pyglet.clock.schedule_once(execute_step, 0.01)
                
        except Exception as e:
            print(f"求解过程中发生严重错误: {str(e)}")
            print("无法求解当前魔方状态")
    elif symbol == key.T:
        # 测试模式：执行一组简单的预设旋转操作，然后还原
        print("执行测试序列...")
        test_solve()
    elif symbol == key.C:
        # 重置魔方到初始状态
        reset_cube()
        # 同时清空历史记录
        step_history = []
        total_step_count = 0
    elif symbol == key.S and modifiers & pyglet.window.key.MOD_SHIFT:
        # 显示魔方状态信息
        check_cube_state(faces)
    elif symbol == key.H and step_history:
        # 显示完整的历史步骤
        print("\n===== 显示完整历史步骤 =====")
        show_full_history(step_history)
    elif symbol == key.P and step_history:
        # 手动保存当前步骤到文件
        save_solution_to_file(step_history)

    toString(faces)
    window.invalid = True  # 重绘窗口

def reset_cube():
    """重置魔方到初始状态"""
    global faces, is_solving, solution_steps, step_history
    
    # 停止任何正在进行的解法
    if is_solving:
        is_solving = False
        solution_steps = []
    
    # 清空历史记录
    step_history = []
        
    # 重置魔方状态
    faces = initialize_faces()
    print("魔方已重置到初始状态")
    
    # 更新显示
    toString(faces)
    window.invalid = True

def test_solve():
    """测试魔方旋转功能的可靠性"""
    global faces, is_solving, solution_steps
    
    # 重置魔方到初始状态
    faces = initialize_faces()
    
    # 定义一组测试操作序列（打乱和还原）
    # 这个序列设计为自我还原：正向操作然后逆向操作
    test_moves = [
        "R", "U", "F", "L", "D", "B",        # 打乱
        "B'", "D'", "L'", "F'", "U'", "R'"   # 还原（逆序执行逆操作）
    ]
    
    # 执行测试序列
    solution_steps = test_moves.copy()
    is_solving = True
    
    # 执行第一个步骤
    pyglet.clock.schedule_once(execute_step, 0.5)
    
    print("测试序列已安排执行...")

# 在终端打印漂亮的步骤信息
def print_step_info(step_number, move, remaining_steps=0):
    """在终端输出漂亮的步骤信息"""
    
    # 步骤信息描述
    step_meaning = {
        "U": "顶面顺时针",
        "U'": "顶面逆时针",
        "U2": "顶面旋转180度",
        "D": "底面逆时针", 
        "D'": "底面顺时针",
        "D2": "底面旋转180度",
        "L": "左面顺时针",
        "L'": "左面逆时针",
        "L2": "左面旋转180度",
        "R": "右面顺时针",
        "R'": "右面逆时针",
        "R2": "右面旋转180度",
        "F": "前面顺时针",
        "F'": "前面逆时针",
        "F2": "前面旋转180度",
        "B": "后面顺时针",
        "B'": "后面逆时针",
        "B2": "后面旋转180度"
    }
    
    # 为不同的步骤使用不同的颜色
    move_type = move[0] if len(move) > 0 else ""
    color_code = {
        "U": "\033[94m",  # 蓝色
        "D": "\033[93m",  # 黄色
        "L": "\033[92m",  # 绿色
        "R": "\033[91m",  # 红色
        "F": "\033[95m",  # 洋红色
        "B": "\033[96m"   # 青色
    }.get(move_type, "\033[97m")  # 默认白色
    
    # 重置颜色的代码
    reset_code = "\033[0m"
    
    # 计算进度百分比
    if remaining_steps > 0:
        total_estimated_steps = step_number + remaining_steps
        progress_percent = (step_number / total_estimated_steps) * 100
        progress_bar = generate_progress_bar(progress_percent)
    else:
        progress_percent = 100
        progress_bar = generate_progress_bar(100)
    
    # 构建漂亮的步骤显示
    header = f"\n{color_code}{'='*50}{reset_code}"
    title = f"{color_code}执行步骤 {step_number}{reset_code}"
    details = f"{color_code}动作: {move} - {step_meaning.get(move, '未知步骤')}{reset_code}"
    progress = f"进度: {progress_bar} {progress_percent:.1f}%"
    remaining = f"剩余步骤: {remaining_steps}" if remaining_steps > 0 else "最后一步"
    footer = f"{color_code}{'='*50}{reset_code}"
    
    # 打印步骤信息
    print(header)
    print(title)
    print(details)
    print(progress)
    print(remaining)
    print(footer)

# 生成进度条
def generate_progress_bar(percent, length=30):
    """生成ASCII进度条"""
    filled_length = int(length * percent / 100)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"[{bar}]"

# 执行求解步骤
def execute_step(dt):
    global faces, is_solving, solution_steps, step_history
    
    # 如果有解法步骤，执行下一步
    if solution_steps:
        move = solution_steps.pop(0)
        if move in MOVE_MAP:
            # 执行旋转操作
            MOVE_MAP[move](faces)
            step_history.append(move)
            print(f"执行: {move}")
            window.invalid = True
            # 快速执行下一步
            pyglet.clock.schedule_once(execute_step, 0.01)  # 减少延迟到0.01秒，更加流畅
        else:
            # 遇到无效步骤，跳过继续执行
            print(f"警告: 跳过无效步骤 '{move}'")
            pyglet.clock.schedule_once(execute_step, 0.01)
    else:
        # 没有更多步骤，检查魔方是否已还原
        if is_init_state(faces):
            # 魔方已还原完成
            is_solving = False
            print("\n魔方已完全还原!")
            save_solution_to_file(step_history)
        elif is_solving:
            # 魔方尚未还原，但无需等待用户确认，直接计算新的解法并继续执行
            print("\n继续求解魔方...")
            
            try:
                # 获取魔方当前状态
                cube_str = encode_cube(faces)
                
                # 尝试使用kociemba求解当前状态
                solution = kociemba.solve(cube_str)
                print(f"新解法: {solution}")
                
                # 设置新的解法步骤
                solution_steps = solution.split()
                print(f"继续执行 {len(solution_steps)} 步")
                
                # 立即执行第一步，不停顿
                pyglet.clock.schedule_once(execute_step, 0.01)
            except Exception as e:
                print(f"继续求解失败，尝试使用替代方法: {str(e)}")
                try:
                    # 尝试使用修复后的字符串
                    fixed_str = fix_cube_string(cube_str)
                    solution = kociemba.solve(fixed_str)
                    print(f"使用修复后状态求解成功")
                    solution_steps = solution.split()
                    # 立即执行，不停顿
                    pyglet.clock.schedule_once(execute_step, 0.01)
                except Exception as e2:
                    # 所有方法失败后，才停止求解
                    print(f"无法继续求解: {str(e2)}")
                    is_solving = False
        else:
            # 不在求解过程中，无需操作
            pass

# 显示3D魔方
@window.event
def on_draw():
    # 清除缓冲时添加深度缓冲清除
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # 启用深度测试
    glEnable(GL_DEPTH_TEST)

    # 设置投影矩阵
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, window_width / window_height, 0.1, 50.0)

    # 设置模型视图矩阵
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # 根据窗口大小调整视图距离，让魔方在任何窗口大小下都有合适的观察距离
    view_distance = max(5.0, window_width / 200.0)
    glTranslatef(0, 0, -view_distance)
    glRotatef(30, 1, 0, 0)  # 俯视角30度
    glRotatef(-45, 0, 1, 0)  # 水平旋转-45度

    # 绘制可见的三个面（前、右、上）
    # 根据窗口大小调整魔方尺寸
    scale_factor = min(window_width, window_height) / 800.0  # 基于800像素参考尺寸缩放
    cube_size = 0.5 * scale_factor
    
    draw_face(4, position=(0, 0, cube_size))  # 前面
    draw_face(3, position=(cube_size, 0, 0))  # 右面
    draw_face(0, position=(0, cube_size, 0))  # 上面

    # 添加操作提示 - 底部
    font_size = max(12, int(14 * scale_factor))
    help_label = pyglet.text.Label(
        "按键操作: F/B/L/R/U/D=旋转面, Shift+字母=逆向旋转, Enter=求解, C=重置魔方, N=拍摄新魔方, Esc=中断解法",
        font_size=font_size,
        x=window_width * 0.05,
        y=window_height * 0.02,
        width=window_width * 0.9,
        multiline=True,
        color=(255, 255, 255, 255),
    )
    help_label.draw()
    
    # 添加魔方faces数据显示
    draw_faces_data(scale_factor)
    
    # 显示当前步骤（如果正在执行解法）
    if is_solving and step_history:
        display_current_move(step_history[-1], scale_factor)
    elif not step_history and not is_solving:
        # 显示开始提示
        pass

# 修改绘制控制栏函数，显示更多的历史记录
def draw_faces_data(scale_factor):
    # 根据窗口大小调整起始位置和行高
    y_pos = window_height * 0.07
    x_start = window_width * 0.02
    line_height = max(16, int(18 * scale_factor))
    font_size_title = max(12, int(14 * scale_factor))
    font_size_data = max(10, int(12 * scale_factor))
    
    colors = [(255,0,0,255), (0,255,0,255), (0,0,255,255), 
              (255,255,0,255), (255,128,0,255), (255,255,255,255)]
    face_names = ["上面(0)", "下面(1)", "左面(2)", "右面(3)", "前面(4)", "后面(5)"]
    
    # 绘制标题
    title_label = pyglet.text.Label(
        "魔方状态数据（用于kociemba）:",
        font_size=font_size_title,
        x=x_start,
        y=y_pos,
        color=(255, 255, 255, 255),
        anchor_y='bottom'
    )
    title_label.draw()
    y_pos += line_height + 5
    
    # 逐个绘制每个面的数据
    for face_idx, face in enumerate(faces):
        # 面的名称
        face_label = pyglet.text.Label(
            face_names[face_idx] + ":",
            font_size=font_size_data,
            x=x_start,
            y=y_pos,
            color=colors[face_idx],
            anchor_y='bottom'
        )
        face_label.draw()
        
        # 面的数据
        data_str = ""
        for i in range(3):
            for j in range(3):
                data_str += str(int(face[i][j])) + " "
            if i < 2:  # 不是最后一行
                data_str += "| "
                
        data_label = pyglet.text.Label(
            data_str,
            font_size=font_size_data,
            x=x_start + window_width * 0.12,  # 缩进显示，根据窗口宽度调整
            y=y_pos,
            color=(200, 200, 200, 255),
            anchor_y='bottom'
        )
        data_label.draw()
        
        y_pos += line_height
    
    # 绘制历史步骤记录 - 移到更醒目的位置
    history_section_y = window_height * 0.85
    history_width = window_width * 0.96
    
    # 绘制历史背景
    history_bg = pyglet.shapes.Rectangle(
        x=window_width * 0.02, 
        y=history_section_y - window_height * 0.5,  # 增加高度，以容纳更多步骤
        width=history_width, 
        height=window_height * 0.5,
        color=(30, 30, 40)
    )
    history_bg.opacity = 180
    history_bg.draw()
    
    # 历史标题
    history_title = pyglet.text.Label(
        f"执行步骤历史记录 (共 {len(step_history)} 步) - H键查看完整历史, P键保存:",
        font_size=max(14, int(16 * scale_factor)),
        x=window_width * 0.5,
        y=history_section_y,
        color=(255, 255, 255, 255),
        anchor_x='center',
        anchor_y='bottom'
    )
    history_title.draw()
    
    # 显示说明文字
    explanation = pyglet.text.Label(
        "按键：F=前, B=后, L=左, R=右, U=上, D=下, 加Shift=逆向转动, Enter=求解魔方",
        font_size=max(10, int(12 * scale_factor)),
        x=window_width * 0.5,
        y=history_section_y - line_height,
        color=(180, 180, 180, 255),
        anchor_x='center',
        anchor_y='bottom'
    )
    explanation.draw()
    
    # 计算显示步骤的最大数量 - 基于窗口高度动态调整行数
    max_lines = max(8, min(16, int(window_height / 70)))  
    max_steps_per_line = max(12, min(20, int(window_width / 70)))
    max_display_steps = 100  # 固定显示最多100步历史记录
    
    # 显示最近的步骤
    display_steps = step_history[-max_display_steps:] if len(step_history) > max_display_steps else step_history
    if display_steps:
        # 显示步骤计数
        step_count_label = pyglet.text.Label(
            f"显示最近 {len(display_steps)} 步 " + 
            (f"(从第 {len(step_history) - len(display_steps) + 1} 步到第 {len(step_history)} 步，共 {len(step_history)} 步)" 
             if len(step_history) > max_display_steps else ""),
            font_size=max(10, int(11 * scale_factor)),
            x=window_width * 0.5,
            y=history_section_y - line_height * 2,
            color=(255, 255, 100, 255),
            anchor_x='center',
            anchor_y='bottom'
        )
        step_count_label.draw()
        
        # 将步骤分行显示
        num_lines = min(max_lines, (len(display_steps) + max_steps_per_line - 1) // max_steps_per_line)
        line_height_steps = line_height * 1.0  # 减小行间距，使显示更紧凑
        
        for line_idx in range(num_lines):
            start_idx = len(display_steps) - (num_lines - line_idx) * max_steps_per_line
            end_idx = min(start_idx + max_steps_per_line, len(display_steps))
            
            if start_idx < 0:
                start_idx = 0
                
            if start_idx >= end_idx:
                continue
                
            line_steps = display_steps[start_idx:end_idx]
            
            # 构建这一行的步骤字符串
            line_str = ""
            for i, step in enumerate(line_steps):
                step_num = len(step_history) - len(display_steps) + start_idx + i + 1
                line_str += f"{step_num}:{step} "
                if (i+1) % 10 == 0 and i < len(line_steps) - 1:  # 每10步添加一个分隔符
                    line_str += "| "
            
            # 显示这一行
            y_position = history_section_y - line_height * 3 - line_height_steps * line_idx
            history_label = pyglet.text.Label(
                line_str,
                font_size=max(20, int(12 * scale_factor)),  # 减小字体大小
                x=window_width * 0.5,
                y=y_position,
                color=(255, 215, 0, 255),  # 金黄色显示步骤
                anchor_x='center',
                anchor_y='bottom'
            )
            history_label.draw()
    else:
        # 没有历史记录
        no_history = pyglet.text.Label(
            "暂无步骤执行记录",
            font_size=max(12, int(14 * scale_factor)),
            x=window_width * 0.5,
            y=history_section_y - line_height * 3,
            color=(200, 200, 200, 255),
            anchor_x='center',
            anchor_y='bottom'
        )
        no_history.draw()
    
    # 显示当前状态信息
    status_y_pos = window_height * 0.95
    
    # 如果正在执行解法，显示当前步骤信息
    if is_solving and solution_steps:
        # 状态背景
        status_bg = pyglet.shapes.Rectangle(
            x=0, 
            y=status_y_pos - window_height * 0.07, 
            width=window_width, 
            height=window_height * 0.07,
            color=(0, 50, 0)
        )
        status_bg.opacity = 150
        status_bg.draw()
        
        # 当前执行状态
        current_step = step_history[-1] if step_history else "准备开始"
        next_step = solution_steps[0] if solution_steps else "无"
        
        status_label = pyglet.text.Label(
            f"正在快速求解魔方 (按Esc键中断)",
            font_size=max(12, int(14 * scale_factor)),
            x=window_width * 0.5,
            y=status_y_pos - window_height * 0.03,
            color=(0, 255, 0, 255),
            anchor_x='center',
            anchor_y='center'
        )
        status_label.draw()
        
        # 显示使用的算法类型提示
        algorithm_label = pyglet.text.Label(
            "正在快速求解魔方 (按Esc键中断)",
            font_size=max(10, int(12 * scale_factor)),
            x=window_width * 0.5,
            y=status_y_pos - window_height * 0.055,
            color=(200, 255, 200, 255),
            anchor_x='center',
            anchor_y='center'
        )
        algorithm_label.draw()
        
    elif is_solving and not solution_steps:
        # 正在重新计算解法
        status_bg = pyglet.shapes.Rectangle(
            x=0, 
            y=status_y_pos - window_height * 0.07, 
            width=window_width, 
            height=window_height * 0.07,
            color=(0, 0, 100)
        )
        status_bg.opacity = 150
        status_bg.draw()
        
        status_label = pyglet.text.Label(
            f"已执行 {len(step_history)} 步，魔方尚未还原，正在计算下一阶段解法...",
            font_size=max(12, int(14 * scale_factor)),
            x=window_width * 0.5,
            y=status_y_pos - window_height * 0.035,
            color=(255, 255, 0, 255),
            anchor_x='center',
            anchor_y='center'
        )
        status_label.draw()
    elif step_history:
        # 显示已完成的步骤数
        is_solved = is_init_state(faces)
        status_color = (0, 255, 0, 255) if is_solved else (255, 255, 255, 255)
        
        status_label = pyglet.text.Label(
            f"已完成 {len(step_history)} 步操作" + 
            (" - 魔方已还原!" if is_solved else " - 按Enter键求解魔方"),
            font_size=max(12, int(14 * scale_factor)),
            x=window_width * 0.5,
            y=status_y_pos - window_height * 0.035,
            color=status_color,
            anchor_x='center',
            anchor_y='center'
        )
        status_label.draw()

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

    # 计算缩放因子 - 根据窗口大小动态调整方块大小
    scale_factor = min(window_width, window_height) / 800.0
    cube_block_size = 0.15 * scale_factor  # 每个小方块的大小
    cube_spacing = 0.33 * scale_factor     # 方块之间的间距

    # 遍历3x3网格
    for i in range(3):
        for j in range(3):
            # 计算每个小格子的位置，使用缩放后的间距
            offset_x = (i - 1) * cube_spacing
            offset_y = (j - 1) * cube_spacing

            # 设置颜色
            glColor3f(*get_color(face_data[i][j]))

            # 绘制四边形
            glBegin(GL_QUADS)
            if face_idx == 4:  # 前面
                glVertex3f(x + offset_x - cube_block_size, y + offset_y - cube_block_size, z)
                glVertex3f(x + offset_x + cube_block_size, y + offset_y - cube_block_size, z)
                glVertex3f(x + offset_x + cube_block_size, y + offset_y + cube_block_size, z)
                glVertex3f(x + offset_x - cube_block_size, y + offset_y + cube_block_size, z)
            elif face_idx == 3:  # 右面
                glVertex3f(x, y + offset_y - cube_block_size, z + offset_x - cube_block_size)
                glVertex3f(x, y + offset_y - cube_block_size, z + offset_x + cube_block_size)
                glVertex3f(x, y + offset_y + cube_block_size, z + offset_x + cube_block_size)
                glVertex3f(x, y + offset_y + cube_block_size, z + offset_x - cube_block_size)
            elif face_idx == 0:  # 上面
                glVertex3f(x + offset_x - cube_block_size, y, z + offset_y - cube_block_size)
                glVertex3f(x + offset_x + cube_block_size, y, z + offset_y - cube_block_size)
                glVertex3f(x + offset_x + cube_block_size, y, z + offset_y + cube_block_size)
                glVertex3f(x + offset_x - cube_block_size, y, z + offset_y + cube_block_size)
            glEnd()

# 添加一个函数，以大字体显示当前魔方动作步骤
def display_current_move(move=None, scale_factor=1.0):
    # 如果没有指定步骤，显示帮助信息
    if not move:
        move_display = pyglet.text.Label(
            "按Enter键开始求解魔方",
            font_size=max(24, int(36 * scale_factor)),
            x=window_width * 0.5,
            y=window_height * 0.5,
            color=(255, 255, 0, 255),
            anchor_x='center',
            anchor_y='center'
        )
        move_display.draw()
        return
    
    # 显示当前步骤的大图标和说明
    move_meaning = {
        "U": "顶面顺时针",
        "U'": "顶面逆时针",
        "U2": "顶面旋转180°",
        "D": "底面逆时针", 
        "D'": "底面顺时针",
        "D2": "底面旋转180°",
        "L": "左面顺时针",
        "L'": "左面逆时针",
        "L2": "左面旋转180°",
        "R": "右面顺时针",
        "R'": "右面逆时针",
        "R2": "右面旋转180°",
        "F": "前面顺时针",
        "F'": "前面逆时针",
        "F2": "前面旋转180°",
        "B": "后面顺时针",
        "B'": "后面逆时针",
        "B2": "后面旋转180°"
    }
    
    # 根据步骤类型选择颜色
    move_type = move[0] if len(move) > 0 else ""
    color_map = {
        "U": (0, 0, 255),   # 蓝色
        "D": (255, 255, 0), # 黄色
        "L": (0, 255, 0),   # 绿色
        "R": (255, 0, 0),   # 红色
        "F": (255, 0, 255), # 洋红色
        "B": (0, 255, 255)  # 青色
    }
    bg_color = color_map.get(move_type, (100, 100, 100))
    
    # 计算适应窗口大小的UI元素尺寸
    box_width = min(300 * scale_factor, window_width * 0.4)
    box_height = min(140 * scale_factor, window_height * 0.25)
    border_width = max(2, int(3 * scale_factor))
    
    # 创建一个大一点的背景区域
    step_bg = pyglet.shapes.Rectangle(
        x=window_width * 0.5 - box_width * 0.5,
        y=window_height * 0.5 - box_height * 0.5,
        width=box_width,
        height=box_height,
        color=bg_color
    )
    step_bg.opacity = 230
    step_bg.draw()
    
    # 添加边框
    border = pyglet.shapes.BorderedRectangle(
        x=window_width * 0.5 - box_width * 0.5,
        y=window_height * 0.5 - box_height * 0.5,
        width=box_width,
        height=box_height,
        color=bg_color,
        border_color=(255, 255, 255),
        border=border_width
    )
    border.draw()
    
    # 步骤标题
    step_title = pyglet.text.Label(
        "当前步骤",
        font_size=max(14, int(20 * scale_factor)),
        x=window_width * 0.5,
        y=window_height * 0.5 + box_height * 0.35,
        color=(255, 255, 255, 255),
        anchor_x='center',
        anchor_y='center'
    )
    step_title.draw()
    
    # 步骤符号 - 更大更突出
    step_symbol = pyglet.text.Label(
        move,
        font_size=max(36, int(60 * scale_factor)),
        x=window_width * 0.5,
        y=window_height * 0.5,
        color=(255, 255, 255, 255),
        anchor_x='center',
        anchor_y='center'
    )
    step_symbol.draw()
    
    # 步骤含义
    step_meaning = pyglet.text.Label(
        move_meaning.get(move, "未知步骤"),
        font_size=max(14, int(20 * scale_factor)),
        x=window_width * 0.5,
        y=window_height * 0.5 - box_height * 0.3,
        color=(255, 255, 255, 255),
        anchor_x='center',
        anchor_y='center'
    )
    step_meaning.draw()

def main():
    # 如果脚本被直接运行，则初始化faces
    global faces
    if __name__ == "__main__":
        faces = initialize_faces()
    toString(faces)
    
    # 显示按键操作说明
    print("\n===== 魔方模拟器按键操作说明 =====")
    print("旋转操作:")
    print("  F   - 前面顺时针旋转")
    print("  F+Shift - 前面逆时针旋转")
    print("  B   - 后面顺时针旋转")
    print("  B+Shift - 后面逆时针旋转")
    print("  L   - 左面顺时针旋转")
    print("  L+Shift - 左面逆时针旋转")
    print("  R   - 右面顺时针旋转")
    print("  R+Shift - 右面逆时针旋转")
    print("  U   - 顶面顺时针旋转")
    print("  U+Shift - 顶面逆时针旋转")
    print("  D   - 底面顺时针旋转")
    print("  D+Shift - 底面逆时针旋转")
    print("\n功能键:")
    print("  Enter - 使用kociemba算法求解魔方")
    print("  Esc   - 中断正在执行的解法")
    print("  C     - 重置魔方到初始状态")
    print("  N     - 调用RLFBUD.py拍摄新的魔方并导入")
    print("  S+Shift - 检查魔方状态")
    print("  H     - 在终端显示完整历史步骤")
    print("  P     - 保存当前步骤序列到文件")
    print("  T     - 执行测试序列")
    print("\n解法说明:")
    print("  • 使用kociemba算法，步骤执行间隔0.01秒")
    print("  • 如果一次解法未完成，程序会自动继续尝试求解")
    print("  • 解法完成后会自动保存步骤到文件")
    print("  • 按N键可以在不退出程序的情况下拍摄新的魔方")
    print("===============================\n")
    
    # 只有直接运行时才启动pyglet应用
    if __name__ == "__main__":
        pyglet.app.run()

if __name__ == "__main__":
    main()

# 添加高级魔方求解算法
# 这些高级算法已被移除，改为使用简单的kociemba直接求解方式，以增加稳定性

# 从cube_data或main重新初始化魔方
def reinitialize_cube():
    """从cube_data.py或main.py重新初始化魔方数据，模拟主程序启动行为"""
    global faces, step_history, is_solving, solution_steps
    
    # 清除历史记录和状态
    step_history = []
    is_solving = False
    solution_steps = []
    
    try:
        # 1. 首先尝试从main模块获取数据
        try:
            import importlib
            import sys
            
            if 'main' in sys.modules:
                importlib.reload(sys.modules['main'])
                import main
            else:
                import main
            
            if hasattr(main, 'faces'):
                print("从main.py导入新的魔方状态...")
                faces = main.faces
                print("成功从main.py导入新魔方数据！")
                return True
        except ImportError:
            print("main.py模块不可用，尝试其他方法...")
        except Exception as e:
            print(f"从main.py导入时出错: {str(e)}")
        
        # 2. 尝试从cube_data.py导入
        try:
            if 'cube_data' in sys.modules:
                importlib.reload(sys.modules['cube_data'])
            else:
                import cube_data
            
            if hasattr(cube_data, 'faces'):
                faces = cube_data.faces
                print("成功从cube_data.py导入新魔方数据！")
                return True
            else:
                print("错误: cube_data.py中没有找到faces数据")
        except ImportError:
            print("错误: 无法导入cube_data.py")
        except Exception as e:
            print(f"从cube_data.py导入时出错: {str(e)}")
        
        # 3. 如果前两种方法都失败，重新初始化一个新的魔方
        print("无法从外部文件导入魔方数据，初始化一个新的魔方...")
        faces = initialize_faces()
        print("已初始化新的魔方")
        return True
        
    except Exception as e:
        print(f"重新初始化魔方时发生严重错误: {str(e)}")
        return False
