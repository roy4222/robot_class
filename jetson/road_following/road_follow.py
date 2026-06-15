import os
import sys
import time
import signal
import threading
import argparse
import numpy as np
import cv2
import torch
import torchvision
import torchvision.transforms as transforms
import PIL.Image

# --- args ---
parser = argparse.ArgumentParser()
parser.add_argument('--speed',    type=float, default=0.20,  help='forward speed (0~1)')
parser.add_argument('--kp',       type=float, default=0.20,  help='steering proportional gain')
parser.add_argument('--kd',       type=float, default=0.0,   help='steering derivative gain')
parser.add_argument('--bias',     type=float, default=0.0,   help='steering bias (-0.3~0.3)')
parser.add_argument('--min-motor',type=float, default=0.0,   help='floor: bump any nonzero wheel cmd below this up to it (beats start dead-zone, e.g. 0.18). 0=off')
parser.add_argument('--model',    type=str, required=True,
    help='path to the newly trained road-following .pth model')
args = parser.parse_args()

# --- system setup ---
os.system("echo jetbot | sudo -S nvpmodel -m0 2>/dev/null")
os.system("echo jetbot | sudo -S sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm' 2>/dev/null")

# --- model ---
print(f"Loading model: {args.model}")
device = torch.device('cuda')
model = torchvision.models.resnet18(pretrained=False)
model.fc = torch.nn.Linear(512, 2)
model.load_state_dict(torch.load(args.model))
model = model.to(device).eval().half()
print("Model loaded to GPU")

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda().half()
std  = torch.Tensor([0.229, 0.224, 0.225]).cuda().half()

def preprocess(frame_bgr):
    # frame_bgr is a native cv2 (BGR) ndarray. Convert BGR->RGB so the model sees the
    # SAME channel order as training: train_rf.py opens images with PIL (RGB) and
    # ImageNet-normalizes with NO channel reversal, so train and demo must both be RGB.
    img = PIL.Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    t = transforms.functional.to_tensor(img).to(device).half()
    t.sub_(mean[:, None, None]).div_(std[:, None, None])
    return t[None, ...]

# --- robot ---
from jetbot import Robot
robot = Robot(driver_board="dfrobot")

# --- state ---
running = True
angle_last = 0.0

def shutdown(sig=None, frame=None):
    global running
    running = False

signal.signal(signal.SIGINT,  shutdown)
signal.signal(signal.SIGTERM, shutdown)

# --- main loop ---
print(f"\nStarting  speed={args.speed}  kp={args.kp}  kd={args.kd}  bias={args.bias}")
print("Press Ctrl+C to stop\n")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("ERROR: cannot open /dev/video0")
    sys.exit(1)

try:
    while running:
        ret, frame = cap.read()
        if not ret:
            print("Camera read failed, retrying...")
            time.sleep(0.05)
            continue

        # crop center square, resize to 224x224
        h, w = frame.shape[:2]
        d = (w - h) // 2
        crop = frame[0:h, d:d+h]
        img224 = cv2.resize(crop, (224, 224), interpolation=cv2.INTER_CUBIC)
        # img224 is BGR (cv2); preprocess() converts BGR->RGB to match train_rf.py
        # (trained on PIL RGB, no channel reversal). Channel order is now consistent.

        # inference
        with torch.no_grad():
            xy = model(preprocess(img224)).detach().float().cpu().numpy().flatten()
        x = float(xy[0])
        y = float((0.5 - xy[1]) / 2.0)

        # PD steering
        angle = float(np.arctan2(x, y))
        pid   = angle * args.kp + (angle - angle_last) * args.kd
        angle_last = angle
        steering = pid + args.bias

        left  = max(min(args.speed + steering, 1.0), 0.0)
        right = max(min(args.speed - steering, 1.0), 0.0)
        # motor start dead-zone: a nonzero command below the start threshold just
        # stalls the wheel (esp. the inner wheel mid-turn) -> stutter. Bump it up.
        mm = args.min_motor
        if mm > 0.0:
            if 0.0 < left  < mm: left  = mm
            if 0.0 < right < mm: right = mm
        robot.left_motor.value  = left
        robot.right_motor.value = right

        print(f"\rx={x:+.3f} y={y:+.3f} angle={angle:+.3f} steer={steering:+.3f} L={left:.2f} R={right:.2f}  ",
              end='', flush=True)

finally:
    print("\nStopping...")
    robot.stop()
    cap.release()
    os.system("echo jetbot | sudo -S sh -c 'echo 0 > /sys/devices/pwm-fan/target_pwm' 2>/dev/null")
    print("Done.")
