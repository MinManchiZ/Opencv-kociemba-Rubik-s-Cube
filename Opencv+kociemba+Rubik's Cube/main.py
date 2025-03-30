from RLFBUD import capture_faces, main as get_cube_data
import numpy as np
import subprocess
import sys
import os

# 颜色映射：从RLFBUD提供的字母颜色转为cube.py中使用的数字
# cube.py中的颜色: [0:红色, 1:绿色, 2:蓝色, 3:黄色, 4:橙色, 5:白色]
COLOR_TO_NUMBER = {
    'R': 0,  # 红色
    'G': 1,  # 绿色
    'B': 2,  # 蓝色
    'Y': 3,  # 黄色
    'O': 4,  # 橙色
    'W': 5,  # 白色
    'U': 0   # 未知颜色默认为红色
}

def convert_face_data(cube_list):
    """将列表格式的数据转换为字典格式
    cube_list: 从RLFBUD.py获取的54个颜色值列表
    返回: 按面分组的字典
    """
    if not cube_list or len(cube_list) != 54:
        raise ValueError("无效的魔方数据")

    return {
        'F': cube_list[0:9],    # 第1个拍摄的面
        'R': cube_list[9:18],   # 第2个拍摄的面
        'B': cube_list[18:27],  # 第3个拍摄的面
        'L': cube_list[27:36],  # 第4个拍摄的面
        'U': cube_list[36:45],  # 第5个拍摄的面
        'D': cube_list[45:54]   # 第6个拍摄的面
    }

def create_faces_array(cube_dict):
    """
    将字典格式的魔方数据转换为cube.py使用的数据格式
    输入: 按面分组的字典，颜色用字母表示 (RGBWOY)
    输出: 6个3x3的numpy数组，颜色用数字表示 (0-5)
    """
    # 创建6个面的数组，按照cube.py中的顺序: 上(0), 下(1), 左(2), 右(3), 前(4), 后(5)
    faces = []
    
    # 按照cube.py中的顺序映射面
    face_order = {
        'U': 0,  # 上
        'D': 1,  # 下
        'L': 2,  # 左
        'R': 3,  # 右
        'F': 4,  # 前
        'B': 5   # 后
    }
    
    # 创建6个空白面
    for i in range(6):
        faces.append(np.zeros((3, 3)))
    
    # 填充数据
    for face_name, colors in cube_dict.items():
        idx = face_order[face_name]
        face_array = np.zeros((3, 3))
        
        for i in range(3):
            for j in range(3):
                # 将字母颜色转换为数字
                color_letter = colors[i*3 + j]
                color_number = COLOR_TO_NUMBER[color_letter]
                face_array[i][j] = color_number
        
        faces[idx] = face_array
    
    return faces

def run_cube_solver(faces_data):
    """
    运行cube.py的3D渲染和求解功能
    """
    import cube
    
    # 使用cube.py中的set_faces函数设置魔方数据
    cube.set_faces(faces_data)
    
    # 显示初始状态
    cube.toString(cube.faces)
    
    # 启动3D渲染（直接调用pyglet的运行）
    cube.pyglet.app.run()

def main():
    # 1. 从RLFBUD.py获取魔方数据
    cube_data = get_cube_data()
    if not cube_data:
        print("未能获取魔方数据")
        return

    # 2. 转换数据格式
    cube_dict = convert_face_data(cube_data)
    
    # 打印转换前的数据（字母格式）
    print("原始魔方数据:")
    for face, colors in cube_dict.items():
        print(f"{face}: {colors}")
    
    # 3. 转换为cube.py使用的格式
    faces = create_faces_array(cube_dict)
    
    # 打印转换后的数据（数字格式）
    print("\n转换后的魔方数据:")
    for i, face in enumerate(['上(U)', '下(D)', '左(L)', '右(R)', '前(F)', '后(B)']):
        print(f"{face}面:\n{faces[i]}")
    
    # 4. 运行cube.py的3D渲染
    try:
        run_cube_solver(faces)
    except Exception as e:
        print(f"3D显示错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 