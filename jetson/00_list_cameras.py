"""
掃描可用的 camera index，幫你找出 C270 是哪一號。

用法：
    python3 00_list_cameras.py
"""

import cv2

for i in range(6):
    cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        cap.release()
        continue
    ok, frame = cap.read()
    if ok and frame is not None:
        h, w = frame.shape[:2]
        print(f"[{i}] OK   {w}x{h}")
    else:
        print(f"[{i}] opened but no frame")
    cap.release()
