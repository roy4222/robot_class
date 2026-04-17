"""
Camera test — 開 webcam、即時顯示畫面 + FPS

用法：
    python3 01_camera_test.py            # 預設用 index 0
    python3 01_camera_test.py 2          # 指定 index（C270 通常是 2）

鍵盤：
    q / ESC  離開
    s        存一張快照到 snapshots/
"""

import sys
import time
from pathlib import Path

import cv2

WINDOW = "Camera Test (q=quit, s=snapshot)"


def open_camera(index: int) -> cv2.VideoCapture:
    # macOS 用 AVFoundation backend 最穩
    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        raise RuntimeError(f"開不起鏡頭 index={index}，換一個編號試試")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap


def main() -> None:
    index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    cap = open_camera(index)

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[ok] camera index={index}  {w}x{h}")
    print("按 q 或 ESC 離開；按 s 存快照")

    snap_dir = Path(__file__).parent / "snapshots"
    snap_dir.mkdir(exist_ok=True)

    prev = time.time()
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("[warn] 讀不到影格")
            break

        now = time.time()
        dt = now - prev
        prev = now
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt)  # 平滑一下

        cv2.putText(
            frame,
            f"FPS: {fps:5.1f}   {w}x{h}   idx={index}",
            (12, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow(WINDOW, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord("s"):
            path = snap_dir / f"snap_{int(time.time())}.jpg"
            cv2.imwrite(str(path), frame)
            print(f"[saved] {path}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
