import cv2
import numpy as np
import os
#色表
color_names = ['orange', 'yellow', 'red', 'blue', 'green', 'white']
image_folder = r"image"

def get_hsv_range(image_path):
    image = cv2.imread(image_path)

    if image is None:

        print(f"无法读取图像：{image_path}")
        return None



    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    min_hue, min_saturation, min_value = np.min(hsv_image, axis=(0, 1))
    max_hue, max_saturation, max_value = np.max(hsv_image, axis=(0, 1))

    return {
        'min_hue': min_hue,
        'min_saturation': min_saturation,
        'min_value': min_value,
        'max_hue': max_hue,
        'max_saturation': max_saturation,
        'max_value': max_value
    }


def process_images():
    hsv_ranges = {}

    for color_name in color_names:
        image_path = os.path.join(image_folder, f"{color_name}.png")
        print(f"处理图像：{image_path}")

        hsv_range = get_hsv_range(image_path)
        if hsv_range:
            hsv_ranges[color_name] = hsv_range
    return hsv_ranges

def print_hsv_ranges(hsv_ranges):

    for color_name, hsv_range in hsv_ranges.items():
        print(f"颜色：{color_name}")
        print(f"  最小 HSV: ({hsv_range['min_hue']}, {hsv_range['min_saturation']}, {hsv_range['min_value']})")
        print(f"  最大 HSV: ({hsv_range['max_hue']}, {hsv_range['max_saturation']}, {hsv_range['max_value']})")
        print("=" * 30)
def main():
    hsv_ranges = process_images()
    print_hsv_ranges(hsv_ranges)

if __name__ == "__main__":
    main()