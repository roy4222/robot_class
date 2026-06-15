# JetBot 道路跟隨（Road Following）— 自製 pipeline

在白紙 + 粉紅線自製賽道上，讓 JetBot（Jetson Nano 4GB + DFRobot 馬達板 + Logitech C270）
用自己收的資料學會循跡。**不用官方 Jupyter notebook**，改成一套可重複、可版本控管的腳本。

## 成果（2026-06-15）
- 端到端跑通：**收資料 → 訓練 → demo**，車能在賽道上自走、跟線。
- 走走停停（stutter）已解決；循跡精準度靠補平衡資料持續改善中。
- 目前最佳模型：277 張平衡資料（左 73 / 中 34 / 右 170 + 水平翻轉）訓練，test loss ~0.023。

## 三支腳本 + Mac 訓練
| 檔案 | 跑在哪 | 作用 |
|------|--------|------|
| `jetbot_web.py` | Jetson | 網頁：WASD 遙控 + 點擊標註收資料（tornado :5000、MJPEG）|
| `train_rf.py` | **Mac (MPS) 或 Jetson (CUDA)** | ResNet18 迴歸訓練（device 自動偵測）|
| `road_follow.py` | Jetson | live demo：載入模型 → 推論 → 控馬達 |

> 資料集與模型（`data/`）不進 git（太大）。本地放 `data/`，Jetson 放
> `~/jetbot_CAVEDU/road_following/`（資料）與 `~/`（部署的腳本與模型）。

## 核心不變量（改任何一支都要守，否則 silent bug 會回來）
- **座標**：檔名 `xy_<px>_<py>_uuid.jpg`，px/py = 0–223 像素（中心 112）。
  收→存、訓練→`(px-112)/112` 解析。**不可混用舊 0–100 / center-50**。
- **顏色**：模型在 train 和 demo **都吃 RGB**（train 用 PIL 不反轉；demo cv2 BGR→`cvtColor`→RGB）。
- **增強**：train 水平翻轉時 `x = -x`（自動左右平衡 + 2 倍資料）。
- **存檔**：乾淨 224×224 原圖（綠點/藍線只在瀏覽器疊加）；點擊「當下那一幀」才存；jog 後重新點。

## 完整流程
**1. 收資料（Jetson）**
```bash
ssh jetbot@192.168.55.1
python3 ~/jetbot_web.py          # 瀏覽器開 http://192.168.55.1:5000 → COLLECT 分頁
```
重點：車擺各種偏位 / 斜角，**綠點一律指車道中心**；左 / 右 / 直都要、彎道多收。
目標 100–250 張、左右平衡。

**2. 訓練（Mac，快）**
```bash
# 從 Jetson 拉資料到 Mac
scp "jetbot@192.168.55.1:~/jetbot_CAVEDU/road_following/dataset_xy_XXXX/*.jpg" data/myset/
# MPS 訓練（device 自動選 mps）
python3 train_rf.py --dataset data/myset --out data/model.pth --epochs 50
# 送回 Jetson
scp data/model.pth jetbot@192.168.55.1:~/model.pth
```
> 訓練前會印資料分布 + 防呆：**< 80 張 / 缺左或右 / 舊 0–100 格式 → 拒訓**（要硬跑加 `--force`）。

**3. demo（Jetson）**
```bash
# 先 Ctrl+C 停掉 jetbot_web.py 放開攝影機；車放賽道上
python3 ~/road_follow.py --model ~/model.pth --speed 0.35 --kp 0.15
```
調參：抖 → `--kp 0.1`；轉不夠 → `--kp 0.3`；彎道一頓一頓 → `--min-motor 0.18`；太快衝出 → 降 `--speed`。

## 今天解掉的坑（debug 記錄）
1. **座標格式**：收資料原本存 0–100 / center-50（非官方）→ 改回官方 0–223 / center-112。
2. **BGR/RGB 不一致**：舊 train 偷偷 `[::-1]` 成 BGR、demo 卻是 RGB → 通道反了模型學不好。統一成 RGB。
3. **走走停停**：(a) `jetbot_stats.service` crash-loop 吃滿 CPU、餓死推論 loop → `systemctl disable`；
   (b) 轉彎時內側輪掉到馬達啟動門檻以下停轉 → `road_follow.py --min-motor 0.18` 補底。
4. **torch 存檔格式**：Mac torch 2.11 存的新 zip 格式 Jetson 舊 torch 讀不了 →
   `train_rf.py` 改存 legacy 格式（`_use_new_zipfile_serialization=False, pickle_protocol=2`）。

## 環境備忘
- **連線**：USB `ssh jetbot@192.168.55.1`（最穩）；無線 `ssh jetbot-wifi`（IP 隨 iPhone 熱點變動）。
- **相機**：C270 USB `/dev/video0`。**馬達板**：DFRobot I2C `0x10`。
- **馬達**：DC 馬達啟動門檻 ~0.18；demo `--speed` 要高於它（實測 0.35 OK）。
- **`jetbot_stats.service` 已 disable**（會搶 CPU 造成卡頓，別再開）。
- Jetson 系統時鐘不準（顯示 2023），資料夾時間戳會錯，不影響功能。
