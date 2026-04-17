"""
人臉偵測 — MediaPipe Face Detection

用法：
    python3 02_face_detection.py            # C270 (index 0)
    python3 02_face_detection.py 3

鍵盤：
    q / ESC  離開
    s        存快照
"""

import sys
import time
from pathlib import Path

import cv2
import mediapipe as mp

WINDOW = "Face Detection (q=quit, s=snapshot)"


def main() -> None:
    index = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    if not cap.isOpened():
        raise RuntimeError(f"開不起鏡頭 index={index}")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    snap_dir = Path(__file__).parent / "snapshots"
    snap_dir.mkdir(exist_ok=True)

    # model_selection: 0=近距離 2m 內最準, 1=遠距離 5m 內
    # min_detection_confidence: 偵測信心門檻，調低更敏感但可能誤判
    detector = mp.solutions.face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0.5
    )
    draw = mp.solutions.drawing_utils

    prev = time.time()
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # MediaPipe 要 RGB，OpenCV 預設是 BGR
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = detector.process(rgb)

        face_count = 0
        if result.detections:
            face_count = len(result.detections)
            for det in result.detections:
                draw.draw_detection(frame, det)
                # 額外把信心值印在框旁邊
                score = det.score[0] if det.score else 0
                box = det.location_data.relative_bounding_box
                h, w = frame.shape[:2]
                x = int(box.xmin * w)
                y = int(box.ymin * h) - 8
                cv2.putText(
                    frame, f"{score:.2f}", (x, max(y, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA,
                )

        now = time.time()
        dt = now - prev
        prev = now
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt)

        cv2.putText(
            frame, f"FPS: {fps:5.1f}  faces: {face_count}",
            (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            (0, 255, 0), 2, cv2.LINE_AA,
        )

        cv2.imshow(WINDOW, frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord("s"):
            path = snap_dir / f"face_{int(time.time())}.jpg"
            cv2.imwrite(str(path), frame)
            print(f"[saved] {path}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
