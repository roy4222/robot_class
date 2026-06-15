# -*- coding: utf-8 -*-
import os, glob, sys, argparse
import numpy as np
import PIL.Image
import torch
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

DATASET_DIR = '/home/jetbot/jetbot_CAVEDU/road_following/dataset_xy_web'
OUT = '/home/jetbot/jetbot_CAVEDU/road_following/best_steering_model_xy_web.pth'
BATCH = 8

# Official JetBot road_following coordinate encoding:
#   filename = xy_<px>_<py>_<uuid>.jpg
#   px, py are PIXEL coordinates in [0, 223] (image is 224x224, center = 112,112).
# Normalize to [-1, 1] using the ACTUAL image dimensions:
#   x = (px - W/2) / (W/2),  y = (py - H/2) / (H/2)
# (Do NOT use the legacy 0-100 / center-50 scheme.)

def _pixels_from_name(name):
    # 'xy_PX_PY_uuid.jpg' -> (px, py) as ints; split on '_' (no fixed-offset slicing)
    tok = name.split('_')
    return int(tok[1]), int(tok[2])

def get_x(name, w):
    px, _ = _pixels_from_name(name)
    return (float(px) - w / 2.0) / (w / 2.0)

def get_y(name, h):
    _, py = _pixels_from_name(name)
    return (float(py) - h / 2.0) / (h / 2.0)

class XYDataset(torch.utils.data.Dataset):
    def __init__(self, d, hflip=True):
        self.paths = glob.glob(os.path.join(d, '*.jpg'))
        self.hflip = hflip
        self.jitter = transforms.ColorJitter(0.3, 0.3, 0.3, 0.3)
    def __len__(self): return len(self.paths)
    def __getitem__(self, i):
        p = self.paths[i]
        img = PIL.Image.open(p)
        name = os.path.basename(p)
        w, h = img.size  # PIL: (width, height)
        x = get_x(name, w); y = get_y(name, h)
        if self.hflip and float(np.random.rand(1)) > 0.5:
            img = transforms.functional.hflip(img); x = -x
        img = self.jitter(img)
        img = transforms.functional.resize(img, (224, 224))
        img = transforms.functional.to_tensor(img)
        # Keep PIL's RGB channel order through to the ImageNet normalize so that
        # training matches the demo (road_follow.py converts BGR->RGB before the
        # identical normalize). NO channel reversal here.
        img = transforms.functional.normalize(img, [0.485,0.456,0.406], [0.229,0.224,0.225])
        return img, torch.tensor([x, y]).float()


def describe_dataset(paths):
    # Returns (xs, ys) of normalized labels and prints the distribution.
    xs = []; ys = []
    for p in paths:
        name = os.path.basename(p)
        try:
            with PIL.Image.open(p) as im:
                w, h = im.size
            xs.append(get_x(name, w))
            ys.append(get_y(name, h))
        except Exception as e:
            print('  skip unreadable/unparseable file: %s (%s)' % (name, e))
    if not xs:
        return xs, ys
    xa = np.array(xs); ya = np.array(ys)
    n_left   = int(np.sum(xa < -0.15))
    n_right  = int(np.sum(xa >  0.15))
    n_center = len(xa) - n_left - n_right
    print('--- dataset distribution ---')
    print('total: %d' % len(xa))
    print('x  min %+.3f  max %+.3f  mean %+.3f' % (xa.min(), xa.max(), xa.mean()))
    print('y  min %+.3f  max %+.3f  mean %+.3f' % (ya.min(), ya.max(), ya.mean()))
    print('left (x<-0.15): %d   center: %d   right (x>0.15): %d'
          % (n_left, n_center, n_right))
    print('----------------------------')
    return xs, ys


def main():
    ap = argparse.ArgumentParser(description='Train JetBot road_following ResNet18 regressor (normalized x,y).')
    ap.add_argument('--dataset', default=DATASET_DIR,
                    help='dataset directory of xy_<px>_<py>_uuid.jpg images (0-223 pixel coords).')
    ap.add_argument('--out', default=OUT, help='output .pth path for the best model state_dict.')
    ap.add_argument('--epochs', type=int, default=50, help='number of training epochs.')
    ap.add_argument('--force', action='store_true',
                    help='train even if the data-safety checks fail (too few / one-sided data).')
    args = ap.parse_args()

    ds = XYDataset(args.dataset)
    n = len(ds)
    print('dataset dir:', args.dataset)
    print('dataset size:', n)

    # Distribution + data-safety gate (must run before training).
    xs, _ = describe_dataset(ds.paths)
    xa = np.array(xs) if xs else np.array([])
    n_left  = int(np.sum(xa < -0.15)) if xa.size else 0
    n_right = int(np.sum(xa >  0.15)) if xa.size else 0

    problems = []
    if n < 80:
        problems.append('only %d images (< 80): too few to train a reliable model.' % n)
    if n_left == 0:
        problems.append('NO left examples (x < -0.15): one-sided data, the car will not learn to turn left.')
    if n_right == 0:
        problems.append('NO right examples (x > 0.15): one-sided data, the car will not learn to turn right.')

    # Legacy-format guard: 0-223 data has center labels near 112, so the max pixel
    # coord should exceed 100. If everything is <= 100 this folder is almost certainly
    # the legacy 0-100/center-50 scheme and must NOT be trained or mixed with 0-223 data.
    raw_max = 0
    for p in ds.paths:
        try:
            px, py = _pixels_from_name(os.path.basename(p))
            raw_max = max(raw_max, px, py)
        except Exception:
            pass
    if ds.paths and raw_max <= 100:
        problems.append('looks like the LEGACY 0-100 format (all pixel coords <= 100). '
                        'Do NOT mix with 0-223 data; re-collect with the current web tool.')

    if problems:
        print('\n!!!!!!!!!!!!!!!!!!!! DATA WARNING !!!!!!!!!!!!!!!!!!!!')
        for msg in problems:
            print('  - ' + msg)
        if args.force:
            print('  --force given: training anyway (results may be poor).')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
        else:
            print('  Refusing to train. Collect more / better-balanced data, or pass --force to override.')
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
            sys.exit(1)

    n_test = max(1, int(0.1 * n))
    train_ds, test_ds = torch.utils.data.random_split(ds, [n - n_test, n_test])
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=BATCH, shuffle=True, num_workers=2)
    test_loader  = torch.utils.data.DataLoader(test_ds,  batch_size=BATCH, shuffle=False, num_workers=2)

    device = torch.device('cuda' if torch.cuda.is_available()
                           else 'mps' if torch.backends.mps.is_available()
                           else 'cpu')
    print('device:', device)
    model = torchvision.models.resnet18(pretrained=True)
    model.fc = torch.nn.Linear(512, 2)
    model = model.to(device)
    opt = optim.Adam(model.parameters())

    best = 1e9
    for epoch in range(args.epochs):
        model.train(); tr = 0.0
        for img, lbl in train_loader:
            img, lbl = img.to(device), lbl.to(device)
            opt.zero_grad()
            out = model(img)
            loss = F.mse_loss(out, lbl)
            loss.backward(); opt.step()
            tr += float(loss) * len(img)
        tr /= len(train_ds)
        model.eval(); te = 0.0
        with torch.no_grad():
            for img, lbl in test_loader:
                img, lbl = img.to(device), lbl.to(device)
                te += float(F.mse_loss(model(img), lbl)) * len(img)
        te /= len(test_ds)
        flag = ''
        if te < best:
            best = te
            torch.save(model.state_dict(), args.out,
                       _use_new_zipfile_serialization=False, pickle_protocol=2)
            flag = '  <- saved'
        print('epoch %2d/%d  train %.4f  test %.4f%s' % (epoch+1, args.epochs, tr, te, flag))

    print('done. best test loss %.4f -> %s' % (best, args.out))


if __name__ == '__main__':
    main()
