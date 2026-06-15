# -*- coding: utf-8 -*-
import argparse
import threading
import time
import os
from datetime import datetime
from uuid import uuid1
import cv2
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
import tornado.iostream

# --- Image geometry (canonical: 224x224, center 112) ---
IMG_SIZE = 224
IMG_CENTER = IMG_SIZE // 2   # 112

# --- Robot ---
from jetbot import Robot
robot = Robot(driver_board="dfrobot")
SPEED = 0.35

# --- Dataset (parameterized via --dataset; default timestamped) ---
def default_dataset_dir():
    return os.path.expanduser(
        '~/jetbot_CAVEDU/road_following/dataset_xy_' + datetime.now().strftime('%Y%m%d_%H%M'))

parser = argparse.ArgumentParser(description='JetBot road-following data collection web app')
parser.add_argument('--dataset', default=default_dataset_dir(),
                    help='dataset output dir (default: timestamped under ~/jetbot_CAVEDU/road_following/)')
parser.add_argument('--port', type=int, default=5000, help='web server port')
args = parser.parse_args()

DATASET_DIR = args.dataset
os.makedirs(DATASET_DIR, exist_ok=True)

def dataset_count():
    return len([f for f in os.listdir(DATASET_DIR) if f.endswith('.jpg')])

# --- Camera thread ---
raw_frame = None       # full 640x480 bgr
crop224 = None         # center-cropped 224x224 bgr
frame_lock = threading.Lock()

def camera_thread():
    global raw_frame, crop224
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            d = (w - h) // 2
            crop = frame[0:h, d:d+h]
            c224 = cv2.resize(crop, (224, 224), interpolation=cv2.INTER_CUBIC)
            with frame_lock:
                raw_frame = frame
                crop224 = c224
        time.sleep(0.033)

threading.Thread(target=camera_thread, daemon=True).start()

# --- Motor control ---
def set_motors(keys):
    w = 'w' in keys; s = 's' in keys
    a = 'a' in keys; d = 'd' in keys
    if not any([w, s, a, d]):
        robot.stop()
        return
    left = right = 0.0
    if w:
        left, right = SPEED, SPEED
    elif s:
        left, right = -SPEED, -SPEED
    if a:
        if w or s:
            left *= 0.3
        else:
            left, right = -SPEED * 0.5, SPEED * 0.5
    if d:
        if w or s:
            right *= 0.3
        else:
            left, right = SPEED * 0.5, -SPEED * 0.5
    robot.left_motor.value  = max(min(left,  1.0), -1.0)
    robot.right_motor.value = max(min(right, 1.0), -1.0)

def encode_jpeg(bgr, quality=80):
    _, buf = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buf.tobytes()

# --- Pending snapshot (frame + coord captured at CLICK time) ---
# The browser POSTs to /click the moment the user clicks a target. We snapshot
# the CURRENT clean crop224 here, together with the pixel coord, so a later SAVE
# persists exactly the frame shown at the labeling instant (no stale frame).
pending_lock = threading.Lock()
pending = None   # dict {img: bgr 224x224, px: int, py: int} or None

def clear_pending():
    global pending
    with pending_lock:
        pending = None

# --- Pulse move (for repositioning during collection) ---
PULSE_SPEED = 0.4
PULSE_TIME = 0.4

def pulse_move(direction):
    s = PULSE_SPEED
    if direction == 'forward':
        robot.set_motors(s, s)
    elif direction == 'backward':
        robot.set_motors(-s, -s)
    elif direction == 'left':
        robot.set_motors(-s, s)
    elif direction == 'right':
        robot.set_motors(s, -s)
    else:
        return
    # The body just moved: the previously-clicked target no longer matches the
    # new view, so invalidate the pending snapshot and force a fresh click.
    clear_pending()
    threading.Timer(PULSE_TIME, robot.stop).start()

# --- MJPEG streams ---
class _StreamBase(tornado.web.RequestHandler):
    crop = False
    async def get(self):
        self.set_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
        self.set_header('Cache-Control', 'no-cache')
        while True:
            if self.request.connection.stream.closed():
                break
            with frame_lock:
                src = crop224 if self.crop else raw_frame
            if src is not None:
                try:
                    self.write(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                               + encode_jpeg(src, 70) + b'\r\n')
                    await self.flush()
                except tornado.iostream.StreamClosedError:
                    break
            await tornado.gen.sleep(0.05)

class VideoHandler(_StreamBase):
    crop = False

class Video224Handler(_StreamBase):
    crop = True

# --- Click: snapshot the frame at the labeling instant ---
class ClickHandler(tornado.web.RequestHandler):
    def post(self):
        global pending
        # px, py are PIXEL coords in [0, 223] (origin top-left, center 112).
        px = int(round(max(0, min(IMG_SIZE - 1, float(self.get_argument('px'))))))
        py = int(round(max(0, min(IMG_SIZE - 1, float(self.get_argument('py'))))))
        # Capture the CURRENT clean crop224 (no overlay) at this instant.
        with frame_lock:
            img = None if crop224 is None else crop224.copy()
        if img is None:
            self.set_status(503); self.write('no frame'); return
        with pending_lock:
            pending = {'img': img, 'px': px, 'py': py}
        self.write({'ok': True, 'px': px, 'py': py})

# --- Save snapshot (persists the frame captured at click time) ---
class SaveHandler(tornado.web.RequestHandler):
    def post(self):
        # Persist the frame+coord snapshotted at click time, never a fresh frame.
        with pending_lock:
            snap = pending
        if snap is None:
            self.set_status(409); self.write('no pending target'); return
        px, py = snap['px'], snap['py']
        img = snap['img']   # clean 224x224 BGR; cv2.imwrite -> true-color JPEG
        fname = 'xy_%03d_%03d_%s.jpg' % (px, py, uuid1())
        path = os.path.join(DATASET_DIR, fname)
        cv2.imwrite(path, img)
        clear_pending()   # consumed; require a fresh click before the next save
        n = dataset_count()
        nx = (px - IMG_CENTER) / float(IMG_CENTER)
        ny = (py - IMG_CENTER) / float(IMG_CENTER)
        print('saved %s px=(%d,%d) norm=(%.3f,%.3f) count=%d'
              % (fname, px, py, nx, ny, n))
        self.write({'count': n, 'fname': fname})

class CountHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'count': dataset_count(), 'dir': DATASET_DIR})

# --- WebSocket (teleop) ---
class WSHandler(tornado.websocket.WebSocketHandler):
    pressed = set()
    def check_origin(self, origin):
        return True
    def on_message(self, msg):
        global SPEED
        if msg.startswith('speed:'):
            SPEED = float(msg[6:]); return
        if msg.startswith('pulse:'):
            pulse_move(msg[6:]); return
        if msg.startswith('down:'):
            WSHandler.pressed.add(msg[5:])
        elif msg.startswith('up:'):
            WSHandler.pressed.discard(msg[3:])
        elif msg == 'stop':
            WSHandler.pressed.clear()
        set_motors(WSHandler.pressed)
    def on_close(self):
        WSHandler.pressed.clear()
        robot.stop()

# --- HTML ---
HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JetBot Control</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#111; color:#eee; font-family:monospace;
       display:flex; flex-direction:column; align-items:center; padding:16px; gap:14px; }
h1 { font-size:1.3rem; letter-spacing:2px; color:#0af; }
.tabs { display:flex; gap:8px; }
.tab { padding:8px 20px; border:2px solid #444; border-radius:6px; cursor:pointer;
       color:#888; background:#1a1a1a; user-select:none; }
.tab.active { color:#000; background:#0af; border-color:#0af; }
.panel { display:none; flex-direction:column; align-items:center; gap:14px; }
.panel.active { display:flex; }
#status { font-size:.8rem; }
#status.ok { color:#0f0; } #status.err { color:#f44; }
.video-box { border:2px solid #333; border-radius:8px; overflow:hidden; position:relative; }
img { display:block; }
#feed { width:640px; max-width:92vw; }
#feed224 { width:448px; max-width:92vw; cursor:crosshair; display:block; }
#overlay { position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; }
.key { width:64px; height:64px; border:2px solid #444; border-radius:8px;
       display:flex; align-items:center; justify-content:center; font-size:1.5rem;
       font-weight:bold; color:#666; background:#1a1a1a; transition:all .08s;
       cursor:pointer; user-select:none; }
.key.active { background:#0af; color:#000; border-color:#0af; box-shadow:0 0 14px #0af; }
.row { display:flex; gap:8px; justify-content:center; }
#speed-row { display:flex; align-items:center; gap:12px; }
#speed-row label { color:#888; font-size:.85rem; }
input[type=range] { accent-color:#0af; width:160px; }
#speed-val { color:#0af; min-width:36px; }
.info { font-size:.74rem; color:#666; text-align:center; line-height:1.9; }
#count-box { font-size:1.1rem; color:#0af; }
#count-box b { font-size:1.6rem; }
.hint { color:#0f0; font-size:.85rem; }
</style>
</head>
<body>
<h1>JETBOT CONTROL</h1>
<div id="status" class="err">connecting...</div>

<div class="tabs">
  <div class="tab active" data-p="teleop">遙控 TELEOP</div>
  <div class="tab" data-p="collect">收資料 COLLECT</div>
</div>

<!-- TELEOP -->
<div class="panel active" id="p-teleop">
  <div class="video-box"><img id="feed" src="/video"></div>
  <div class="row"><div class="key" id="k-w">W</div></div>
  <div class="row">
    <div class="key" id="k-a">A</div>
    <div class="key" id="k-s">S</div>
    <div class="key" id="k-d">D</div>
  </div>
  <div id="speed-row">
    <label>SPEED</label>
    <input type="range" id="speed-slider" min="10" max="80" value="35">
    <span id="speed-val">0.35</span>
  </div>
  <div class="info">W 前進 &nbsp; S 後退 &nbsp; A 左 &nbsp; D 右 &nbsp; SPACE 停</div>
</div>

<!-- COLLECT -->
<div class="panel" id="p-collect">
  <div class="hint">點「車子該前往的目標點」放綠點 → 按 SAVE（或按 S 鍵）存檔</div>
  <div class="video-box">
    <img id="feed224" src="/video224">
    <svg id="overlay" viewBox="0 0 224 224" preserveAspectRatio="none">
      <line   id="ov-line" x1="112" y1="224" x2="112" y2="112" stroke="#08f" stroke-width="3" style="display:none"/>
      <circle id="ov-anchor" cx="112" cy="220" r="7" fill="none" stroke="#f00" stroke-width="3"/>
      <circle id="ov-dot" cx="112" cy="112" r="8" fill="rgba(0,255,0,.4)" stroke="#0f0" stroke-width="3" style="display:none"/>
    </svg>
  </div>
  <div class="row" style="gap:14px;align-items:center">
    <div class="key" id="save-btn" style="width:120px;background:#0a4;color:#000;border-color:#0a4">SAVE</div>
    <div id="count-box">已收集 <b id="count">0</b> 張</div>
  </div>
  <div class="hint" style="color:#888">微調車身位置（移動後重新標註）</div>
  <div class="row"><div class="key step" data-dir="forward">↑</div></div>
  <div class="row">
    <div class="key step" data-dir="left">←</div>
    <div class="key step" data-dir="backward">↓</div>
    <div class="key step" data-dir="right">→</div>
  </div>
  <div class="info" id="dir-info"></div>
</div>

<script>
const ws = new WebSocket('ws://' + location.host + '/ws');
const status = document.getElementById('status');
const keyList = ['w','a','s','d'];
const pressed = new Set();
ws.onopen  = () => { status.textContent='● connected'; status.className='ok'; };
ws.onclose = () => { status.textContent='✕ disconnected'; status.className='err';
                     keyList.forEach(k=>highlight(k,false)); };
function highlight(k,on){ const e=document.getElementById('k-'+k); if(e) e.classList.toggle('active',on); }
function send(m){ if(ws.readyState===1) ws.send(m); }

// tabs
let activePanel='teleop';
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    activePanel=t.dataset.p;
    document.getElementById('p-'+activePanel).classList.add('active');
    if(activePanel!=='teleop'){ pressed.clear(); keyList.forEach(k=>highlight(k,false)); send('stop'); }
  });
});

// teleop keys (only when teleop tab active)
document.addEventListener('keydown',e=>{
  if(activePanel!=='teleop') return;
  const k=e.key.toLowerCase();
  if(k===' '){ e.preventDefault(); pressed.clear(); keyList.forEach(k=>highlight(k,false)); send('stop'); return; }
  if(!keyList.includes(k)||pressed.has(k)) return;
  e.preventDefault(); pressed.add(k); highlight(k,true); send('down:'+k);
});
document.addEventListener('keyup',e=>{
  const k=e.key.toLowerCase();
  if(!keyList.includes(k)) return;
  pressed.delete(k); highlight(k,false); send('up:'+k);
});
keyList.forEach(k=>{
  const el=document.getElementById('k-'+k);
  el.addEventListener('pointerdown',e=>{e.preventDefault();pressed.add(k);highlight(k,true);send('down:'+k);});
  ['pointerup','pointerleave','pointercancel'].forEach(ev=>
    el.addEventListener(ev,e=>{e.preventDefault();pressed.delete(k);highlight(k,false);send('up:'+k);}));
});
document.getElementById('speed-slider').addEventListener('input',function(){
  const v=(this.value/100).toFixed(2);
  document.getElementById('speed-val').textContent=v; send('speed:'+v);
});

// collect: click to place green target dot (carrot-on-a-stick overlay).
// The click SNAPSHOTS the current frame on the server (POST /click); SAVE then
// persists that exact frame, so the saved image matches the labeling instant.
const feed224=document.getElementById('feed224');
const ovDot=document.getElementById('ov-dot');
const ovLine=document.getElementById('ov-line');
let target={px:0,py:0,set:false};   // PIXEL coords 0~223 (center 112)

function clearTarget(){
  target.set=false;
  ovDot.style.display='none';
  ovLine.style.display='none';
}

feed224.addEventListener('click',e=>{
  const r=feed224.getBoundingClientRect();
  let px=Math.round((e.clientX-r.left)/r.width*223);   // -> 0~223 pixel coords
  let py=Math.round((e.clientY-r.top)/r.height*223);
  px=Math.max(0,Math.min(223,px)); py=Math.max(0,Math.min(223,py));
  // overlay is drawn in the 0..224 viewBox (DISPLAY-ONLY, never saved)
  ovDot.setAttribute('cx',px); ovDot.setAttribute('cy',py); ovDot.style.display='block';
  ovLine.setAttribute('x2',px); ovLine.setAttribute('y2',py); ovLine.style.display='block';
  target={px:px,py:py,set:true};
  // snapshot the frame NOW on the server
  fetch('/click',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
    body:'px='+px+'&py='+py})
    .then(r=>{ if(!r.ok){ clearTarget(); flashHint('沒有影像'); } });
});

function saveSnapshot(){
  if(!target.set){ flashHint('先點一個目標點'); return; }
  fetch('/save',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:''})
    .then(r=>{
      if(!r.ok){ flashHint('請重新點一個目標點'); clearTarget(); return null; }
      return r.json();
    }).then(d=>{
      if(!d) return;
      document.getElementById('count').textContent=d.count;
      const b=document.getElementById('save-btn');
      b.style.background='#0f0'; setTimeout(()=>b.style.background='#0a4',150);
      clearTarget();   // consumed: force a fresh click before the next save
    });
}
const dirInfo=document.getElementById('dir-info');
function flashHint(t){ dirInfo.textContent=t; setTimeout(()=>dirInfo.textContent=collectDir,1200); }

document.getElementById('save-btn').addEventListener('click',saveSnapshot);
// press S to save (only on collect tab)
document.addEventListener('keydown',e=>{
  if(activePanel==='collect' && e.key.toLowerCase()==='s'){ e.preventDefault(); saveSnapshot(); }
});

// step movement buttons (pulse). After a jog the body moves, so clear the
// target marker (server also drops its pending snapshot) -> require a fresh click.
document.querySelectorAll('.step').forEach(el=>{
  el.addEventListener('click',()=>{
    send('pulse:'+el.dataset.dir);
    clearTarget();
    flashHint('車身已移動，請重新標註目標點');
  });
});

let collectDir='';
fetch('/count').then(r=>r.json()).then(d=>{
  document.getElementById('count').textContent=d.count;
  collectDir=d.dir; dirInfo.textContent=collectDir;
});
</script>
</body>
</html>
"""

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/html; charset=utf-8')
        self.write(HTML)

app = tornado.web.Application([
    (r'/',        MainHandler),
    (r'/video',   VideoHandler),
    (r'/video224', Video224Handler),
    (r'/ws',      WSHandler),
    (r'/click',   ClickHandler),
    (r'/save',    SaveHandler),
    (r'/count',   CountHandler),
])

if __name__ == '__main__':
    os.system("echo jetbot | sudo -S nvpmodel -m0 2>/dev/null")
    os.system("echo jetbot | sudo -S sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm' 2>/dev/null")
    app.listen(args.port)
    print("JetBot Web Control:")
    print("  http://192.168.55.1:%d  (USB)" % args.port)
    print("  Dataset dir:", DATASET_DIR, "| existing:", dataset_count())
    print("Ctrl+C to stop")
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        robot.stop()
        os.system("echo jetbot | sudo -S sh -c 'echo 0 > /sys/devices/pwm-fan/target_pwm' 2>/dev/null")
        print("\nStopped.")
