
#一个测试HSV颜色的函数
#红色与橙色的掩码叠加，检查是否有红色或橙色
import cv2
import numpy as np
def test_hsv():
    cap = cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_red = cv2.inRange(hsv, np.array([0, 130, 100]), np.array([8, 255, 255]))
        mask_orange = cv2.inRange(hsv, np.array([9, 100, 100]), np.array([20, 255, 255]))


        combined = np.zeros_like(frame)
        combined[mask_red > 0] = (0, 0, 255)
        combined[mask_orange > 0] = (0, 128, 255)
        cv2.imshow("Color Test", combined)

        if cv2.waitKey(1) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()