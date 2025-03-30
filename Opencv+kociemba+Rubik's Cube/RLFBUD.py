import cv2
import numpy as np

# 颜色范围阈值（按HSV）
color_ranges = {
    'O': {'min': (9, 100, 100), 'max': (25, 255, 255)},  # 橙色
    'Y': {'min': (20, 70, 55), 'max': (45, 255, 255)},   # 黄色（稍微扩大黄色范围）
    'R': {'min': (0, 130, 100), 'max': (10, 255, 255)},  # 红色低范围
    'R2': {'min': (170, 130, 100), 'max': (180, 255, 255)},  # 红色高范围
    'B': {'min': (100, 100, 100), 'max': (140, 255, 255)},  # 蓝色
    'G': {'min': (35, 40, 40), 'max': (85, 255, 255)},  # 绿色
    'W': {'min': (0, 0, 200), 'max': (180, 30, 255)}  # 白色
}

DETECTION_RADIUS = 150  # 默认检测区域半径
LINE_THICKNESS = 3  # 网格线粗细
CIRCLE_RADIUS = 8  # 检测点圆圈半径
TEXT_FONT_SCALE = 0.8  # 文字大小


def is_color_in_range(pixel_hsv, color):
    """检查颜色是否在给定范围内"""
    min_h, min_s, min_v = color_ranges[color]['min']
    max_h, max_s, max_v = color_ranges[color]['max']
    return (min_h <= pixel_hsv[0] <= max_h and
            min_s <= pixel_hsv[1] <= max_s and
            min_v <= pixel_hsv[2] <= max_v)


def get_closest_color(pixel_hsv):
    """根据HSV值获取最接近的颜色"""
    for color in ['O', 'Y', 'R', 'R2', 'B', 'G', 'W']:
        if is_color_in_range(pixel_hsv, color):
            # 统一将R2变成R
            if color == 'R2':
                return 'R'
            return color
    return 'U'  # 默认返回未知



def draw_detection_zone(frame, center, radius):
    """绘制检测区域，显示网格和9个检测点"""
    # 绘制圆形检测区域
    cv2.circle(frame, center, radius, (0, 255, 0), LINE_THICKNESS)

    # 绘制3x3网格线
    step = 2 * radius // 3
    for i in range(1, 3):
        # 水平线
        cv2.line(frame,
                 (center[0] - radius, center[1] - radius + i * step),
                 (center[0] + radius, center[1] - radius + i * step),
                 (0, 255, 0), LINE_THICKNESS)
        # 垂直线
        cv2.line(frame,
                 (center[0] - radius + i * step, center[1] - radius),
                 (center[0] - radius + i * step, center[1] + radius),
                 (0, 255, 0), LINE_THICKNESS)

    # 计算并绘制9个检测点（精确到每个小格中心）
    points = []
    for i in range(3):
        for j in range(3):
            # 计算每个小格的中心坐标
            x = center[0] - radius + (j + 0.5) * step
            y = center[1] - radius + (i + 0.5) * step
            points.append((int(x), int(y)))
            # 绘制红色检测点（先覆盖原点）
            cv2.circle(frame, (int(x), int(y)), CIRCLE_RADIUS, (0, 0, 255), -1)
    return points


def draw_color_feedback(frame, center, radius, colors):
    """绘制检测到的颜色信息到图像上"""
    # 获取检测点坐标
    step = 2 * radius // 3
    points = []
    for i in range(3):
        for j in range(3):
            x = center[0] - radius + (j + 0.5) * step
            y = center[1] - radius + (i + 0.5) * step
            points.append((int(x), int(y)))

    color_map = {
        'O': (0, 165, 255),
        'Y': (0, 255, 255),
        'R': (0, 0, 255),
        'R2': (0, 0, 255),  # 红色高范围显示为红色
        'B': (255, 0, 0),
        'G': (0, 255, 0),
        'W': (255, 255, 255),
        'U': (128, 128, 128)
    }

    for idx, (x, y) in enumerate(points):
        color = colors[idx]
        # 填充检测到的颜色
        cv2.circle(frame, (x, y), CIRCLE_RADIUS, color_map[color], -1)
        # 白色边框
        cv2.circle(frame, (x, y), CIRCLE_RADIUS + 2, (255, 255, 255), 1)

        # 显示颜色缩写
        text = color
        font = cv2.FONT_HERSHEY_DUPLEX
        text_size = cv2.getTextSize(text, font, TEXT_FONT_SCALE, 2)[0]
        text_x = int(x - text_size[0] / 2)
        text_y = int(y + text_size[1] / 2)
        cv2.putText(frame, text, (text_x, text_y), font, TEXT_FONT_SCALE,
                    (0, 0, 0), 2)


def capture_faces(cap):
    """捕捉魔方每个面颜色
    拍摄顺序：
    1. Front面
    2. Right面（从Front右转）
    3. Back面（从Right右转）
    4. Left面（从Back右转）
    5. Up面（从Front上翻）
    6. Down面（从Front下翻）
    """
    global DETECTION_RADIUS  # 明确使用全局变量
    cube = []
    faces = ['F', 'R', 'B', 'L', 'U', 'D']  # 修改为正确的拍摄顺序

    for face in faces:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("摄像头错误！")
                return None

            h, w = frame.shape[:2]
            center = (w // 2, h // 2)
            radius = DETECTION_RADIUS

            # 获取检测点坐标
            points = draw_detection_zone(frame.copy(), center, radius)

            # 提取颜色信息
            colors = []
            for x, y in points:
                if 0 <= x < w and 0 <= y < h:
                    pixel_bgr = frame[y, x]
                    pixel_hsv = cv2.cvtColor(
                        np.uint8([[pixel_bgr]]), cv2.COLOR_BGR2HSV
                    )[0][0]
                    color = get_closest_color(pixel_hsv)
                    colors.append(color)
                else:
                    colors.append('U')
            print(f"\r{face}面颜色：{colors}", end='')

            # 绘制完整画面
            frame_copy = frame.copy()
            draw_color_feedback(frame_copy, center, radius, colors)

            # 添加界面提示
            if face == 'F':
                instruction = "Camera Front!"
            elif face == 'R':
                instruction = "Front--->Right"
            elif face == 'B':
                instruction = "Right--->Back"
            elif face == 'L':
                instruction = "Back--->Left"
            elif face == 'U':
                instruction = "Front--->Up"
            else:  # D面
                instruction = "Front--->Down"

            cv2.putText(frame_copy,
                        f"Facelab:<{face}> {instruction}, Space!",
                        (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 0, 255), 3)
            cv2.putText(frame_copy,
                        f"Look<{radius}>",
                        (20, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (255, 255, 255), 2)

            # 显示画面
            cv2.imshow("Cube Detector", frame_copy)
            key = cv2.waitKey(1)
            if key == ord(' '):
                cube += colors
                break
            elif key == 27:
                exit()
            elif key == ord('+'):
                DETECTION_RADIUS += 10
            elif key == ord('-'):
                DETECTION_RADIUS = max(DETECTION_RADIUS - 10, 50)

    return cube

def main():
    cap = cv2.VideoCapture(1)  # 优先尝试默认摄像头
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("无法打开摄像头！")
            return None
    
    cube_data = capture_faces(cap)
    cap.release()
    
    if not cube_data or len(cube_data) != 54:
        print("未能获取完整的魔方数据")
        return None

    return cube_data

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已安全退出")
    except Exception as e:
        print(f"程序遇到错误: {str(e)}")
