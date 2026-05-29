# NVIDIA Jetson Nano AI 深度學習課程 — 上課筆記

> 來源：`2026_Jetson_AI.pdf`（CAVEDU 教育團隊・郭俊廷）
> 課程：透過 Jetson Nano 開發人工智慧應用（NVIDIA DLI Self-paced Course）

---

## Ch 0｜課程簡介與課前準備（p.1–6）

### 重點
- 講師：CAVEDU 郭俊廷（NVIDIA Jetson AI Specialist 認證）。
- 本課程實作全程在 **JupyterNotebook** 上進行，不需要碰 GPIO。
- DLI 自學課程是免費的，完成後可拿 NVIDIA 數位證書。

### 課前要備齊（每組）
- Jetson Nano **4GB**（注意：不是 2GB；2GB 是 USB-C 供電、4GB 是 DC barrel 或 Micro-USB）
- DC 電源變壓器（5V 4A 為佳，跑模型時 Wi-Fi dongle 同時供電容易掉電）
- Micro-USB 線（PC 對連用）**或** RJ45 網路線 + USB 轉接
- Logitech **C270** USB 攝影機（也可用 Pi Camera V2 / CSI，但要改 code）
- SD 卡（已預先用 balenaEtcher 燒好）

### 軟體（zip 內已備）
| 軟體 | 用途 | Mac 替代 |
|---|---|---|
| balenaEtcher | 燒 SD 卡 | 同（也跨平台） |
| MobaXterm 12.3 | Win SSH/SFTP/X11 | Terminal + `scp` |
| WirelessNetworkWatcher | 掃同網段 IP | `arp -a` / `nmap -sn` |

### 坑
- SD 卡 **先插好再接電源**，不然不會開機。
- Mac 上不需要 MobaXterm，內建 Terminal 直接 `ssh` 就行。

---

## Ch 1｜NVIDIA DLI 帳號註冊與加入課程（p.7–26）

### 重點
- 課程網址：https://learn.nvidia.com/courses/course-detail?course_id=course-v1:DLI+S-RX-02+V2-TW
- 用 **個人 Gmail** 註冊，**不要用學校信箱**（畢業後可能登不進去，證書就拿不到）。
- 註冊流程：建立帳號 → Email 驗證 → 完成 Profile（First/Last name、Job Role、Organization、Industry、Location、感興趣領域最多 3 個）→ 接受兩份 Agreement。
- 中文姓名要轉羅馬拼音：https://crptransfer.moe.gov.tw/（選「不顯示聲調符號」）。
- Organization 找不到時可自行 Create，例如「CAVEDU」。
- **Event Code**：本次老師說沒有，從課程頁右側「Enroll Now」直接加入即可。
- Event Code 入口（如果以後有）：https://learn.nvidia.com/dli-event

### 流程速查
```
Register → 用 Gmail → 收驗證信 (Verify Email Address)
        → Profile → 同意條款 → Submit
        → 課程頁 → Enroll Now → My Learning 看到課程
```

### 坑
- 「我是人類」hCaptcha 偶爾會跳 Google 圖片驗證。
- 「保障我的帳戶安全」選 **現在不要**，不然要綁 2FA。
- 註冊推薦 / 訂閱信兩個 checkbox **可全不勾**。

---

## Ch 2｜Jetson Nano 連線與 JupyterLab 環境（p.27–40）

### 重點
- Jetson Nano 本質就是 **一台跑 Ubuntu 18.04 的 Linux 電腦**，差別在於它有 NVIDIA GPU 可以跑 CUDA / TensorRT。
- 介面：Linux + JupyterNotebook + Python。
- 帳號 / 密碼預設都是 `jetson`（Jupyter 密碼是 `dlinano`，**兩個不一樣**）。
- 兩種使用模式：
  1. **桌面模式**：接 HDMI 螢幕 + USB 鍵鼠 + 攝影機 + 電源 → 一般電腦
  2. **SSH 遠端模式**（本次上課用這個）：USB 線或網路線對接 PC

### Mac 上 SSH（最簡單）
```bash
# 網路線連線
ssh jetson@192.168.1.100
# 第一次會問 fingerprint，輸 yes
# 密碼: jetson  （不會顯示）

# Micro-USB 對連
ssh jetson@192.168.55.1
```

固定 IP 設定參考：https://blog.cavedu.com/2023/07/31/jetson-nano-static-ip/

### Windows 上 SSH（MobaXterm）
1. Micro-USB 接 PC，**等 60 秒**讓 Jetson 開好機，PC 會出現 `L4T-README` 磁碟代表連上了。
2. 開 MobaXterm → Session → SSH → host 填 `192.168.55.1`（USB）或 `192.168.1.100`（網路線）。
3. 帳密 `jetson` / `jetson`。

### 上課前置作業（每次開機都要做）
```bash
# 清掉前一個學員的資料（重要！）
sudo rm -r ~/nvdli-data

# 啟動 DLI Docker container（裡面有完整環境 + Jupyter）
./docker_dli_run.sh
# 密碼: jetson

# 開另一個終端，提升效能
sudo jetson_clocks    # 解鎖 GPU/CPU 最高頻
jtop                  # 即時看 CPU / GPU / 溫度 / 記憶體
```

### JupyterLab
- 瀏覽器開：`http://192.168.55.1:8888`（USB）或 `http://192.168.1.100:8888`（網路線）
- 密碼：**`dlinano`**（不是 jetson）
- 推薦瀏覽器：Chrome / Firefox

### 關機（**極重要，不關直接拔電會把 SD 卡搞壞**）
```bash
exit                    # 退出 docker
sudo shutdown -h 0      # 密碼 jetson，等 LED 熄滅再拔電
```

### 坑
- 接 USB 線**先接電源 60 秒再接 USB**，不然 PC 認不到。
- USB 連線 IP 固定 `192.168.55.1`，網路線連線是路由器發的（範例為 `192.168.1.100`）。
- Jupyter 密碼是 `dlinano`，不是 `jetson`。
- 跑模型前一定要 `sudo jetson_clocks`，不然 inference 速度差很多。

---

## Ch 3｜DLI 實作一：影像分類 Image Classification（p.41–70）

### 重點觀念
- **AI vs ML vs DL**：DL 是 ML 的子集，特色是用「具有權重的多層神經網路」+「大量帶標籤資料」+「反覆訓練」。
- **訓練三要素**：資料、標準答案（標籤）、評估準則（loss）。
- **CNN（卷積神經網路）**：透過卷積層找特徵（邊緣、形狀、顏色），全連接層做分類。
- **ResNet-18**：18 層的 CNN，用 Residual block 解決深層網路梯度消失問題；在 ImageNet 1000 類預訓練好的權重可以拿來用。
- **Transfer Learning（遷移學習）**：拿預訓練好的 ResNet-18，**只改最後一層**（例如 `(512, 1000)` → `(512, 3)`），就能用少量資料訓練自己的分類器。這是本課程能在 Jetson Nano 上短時間訓練的關鍵。
- **Inference（推論）**：用訓練好的模型對新資料做預測。

### 四個專題
| 專題 | 類別 | 用途 |
|---|---|---|
| Thumbs | thumbs_up, thumbs_down | 按讚辨識 |
| Emotions | none, happy, sad, angry | 情緒辨識 |
| Fingers | 1, 2, 3, 4, 5 | 手指數量 |
| DIY | 自訂 3 類 | 自己想題目 |

### 操作流程（Thumbs Up/Down）
1. JupyterLab 進到 `/classification/` 開 `classification_interactive.ipynb`。
2. **依序執行所有 Code Block**（Run → Run All Cells，或 Shift+Enter 一格格跑）。
3. 確認相機：`!ls -ltrh /dev/video*` 應該看到 `/dev/video0`。
   ```python
   from jetcam.usb_camera import USBCamera
   camera = USBCamera(width=224, height=224, capture_device=0)
   # 若是 CSI 相機要改用 CSICamera 並把上一行註解掉
   ```
4. 設定任務：
   ```python
   TASK = 'thumbs'                              # 或 'emotions' / 'fingers' / 'diy'
   CATEGORIES = ['thumbs_up', 'thumbs_down']    # 對應改
   DATASETS = ['A', 'B']
   ```
5. 收集資料：UI 上選 category → 對著鏡頭擺姿勢 → 按 `add`，每類至少 50 張，建議 100+。
6. 模型：`model = torchvision.models.resnet18(pretrained=True)`，再 `model.fc = torch.nn.Linear(512, len(dataset.categories))`。
7. 訓練：`epochs = 4` 起跳，看 loss 收斂、accuracy 接近 1.0。
8. 即時推論：把 state 切到 `live`，畫面右側 slider 會顯示各類信心分數。

### 改情緒 / 手指辨識
只要把上面第 4 步的 `TASK` 和 `CATEGORIES` 改掉，重跑那一格之後的所有 cell。

### 上課要交什麼
- DIY 練習：自己找想辨識的東西（例如 Cup / Tea / Other）
- 拍照、截圖或影片上傳
- 老師會問：**資料量、準確度**

### 坑
- 重跑 Camera cell 之前要先 `camera.unobserve_all()`，不然會 device busy。
- 收集資料時背景、角度、光線要多變化，泛化才會好。
- ResNet-18 第一次訓練 4 epochs 大約 1–2 分鐘，等待是正常的。

---

## Ch 4｜DLI 實作二：影像迴歸 Image Regression 與證書（p.71–82）

### 重點觀念
- **Classification vs Regression**：
  - Classification：輸出**離散**類別（thumbs_up / thumbs_down）
  - Regression：輸出**連續**數值（鼻子的 x, y 座標、機器人轉向角度）
- 從 ResNet-18 改成迴歸模型 → **改最後一層輸出維數**：每個 category 對應 2 個輸出（x, y），所以是 `(512, 2 × N)`。
- **Loss function**：分類用 cross entropy，迴歸用 MSE 之類的連續誤差。
- 一樣用 Transfer Learning 的概念。

### Face XY 專題
- 任務：偵測五官位置（這裡用鼻子），CATEGORIES 例如 `['nose']` 或 `['nose', 'left_eye', 'right_eye']`。
- 收集資料時要點擊照片上的對應位置當標籤（不是按按鈕）。
- 訓練好之後，畫面上會有綠色圓圈跟著鼻子移動。

### 評量題重點（DLI 線上會問）
- 分類與迴歸差異：分類離散、迴歸連續。✓
- `model = models.resnet18(pretrained=True)` 是什麼意思？→ 載入 ImageNet 預訓練權重的 ResNet-18。
- `model.fc = torch.nn.Linear(512, 5)` 是什麼？→ 把最後全連接層換成 5 類輸出。
- 雲端 GPU vs Jetson Nano 訓練差異：雲端快、Jetson Nano 慢但可即時部署在邊緣。
- 鼻子追蹤的模型有 **2 個輸出**（x, y）。

### 拿證書流程
1. 課程內所有 Assessment 全部通過。
2. 填課程調查問卷（SurveyMonkey）。
3. NVIDIA 頁面右上角頭像 → **My Learning** → Certificates → 找到「透過 Jetson Nano 開發人工智慧應用」。
4. 點 Download → 瀏覽器列印 → **另存為 PDF + 橫式** → 儲存。
5. 上傳到老師指定的 Google Drive：
   `https://drive.google.com/drive/folders/1Pjn6TUVro9I88gLExdLN79syAYiv-svL`

### 坑
- DLI 會記錄學習進度，可以分次做完，不用一氣呵成。
- 證書下載一定要選**橫式**，直式會被切掉。

---

## Ch 5｜AI、Deep Learning 與 Edge AI 概念補充（p.83–109）

### 主題地圖
這一段是另一門 DLI 課（**Building Video AI Applications at the Edge on Jetson Nano**）的引言 + 通用 AI 概念補充，可以當技術概論。

### 重要觀念
- **符號式 AI（專家系統）**：輸入規則 + 資料 → 輸出答案；很難跳脫人類預先寫好的邏輯。
- **機器學習**：輸入資料 + 答案 → 輸出規則（自己學出來）。
- **ANN（人工神經網路）**：模仿神經元，多個可訓練的數學單元集合。
- **DL 大爆炸三要素**：DNN（深度網路）+ Big Data + GPU。
- **訓練流程**：
  1. **Forward Propagation**：資料丟進網路產生預測
  2. **Loss Function**：預測 vs 真實答案的差距
  3. **Backward Propagation**：用梯度下降修正每層權重
  4. 重複到 loss 收斂
- **Training vs Inference**：Training 是學新能力（雲端 GPU 較適合），Inference 是用訓練好的模型對新資料預測（Edge device 即可）。
- **電腦視覺四大任務**：Classification、Classification + Localization、Object Detection、Image Segmentation。難度遞增。
- **傳統 CV vs CNN**：傳統靠人寫特徵抽取（Haar、SIFT），易錯且不易擴展；CNN 從資料學特徵，可擴展、可微調。

### 深度學習成功五要素
1. **Dataset** — 有沒有夠多帶標籤的資料
2. **Reuse** — 有沒有預訓練模型可用（Transfer Learning）
3. **Feasibility** — 任務技術上做得到嗎
4. **Payoff** — 做出來有商業/應用價值嗎
5. **Fault Tolerance** — 容錯空間多大（醫療診斷 vs 推薦商品）

### 開發策略
> Make test set → Try simple model → Try deep learning

不要一上來就 DL，先看簡單模型能不能解。

### 應用案例（投影片提到的）
- Lung Cancer Prediction（Data Science Bowl 2017）
- Optical QC、Predictive Maintenance、Self-learning Robots、Robotic Locomotion
- 跨產業：Internet Services、Medicine、Media、Security、Autonomous Machines

---

## Ch 6｜邊緣運算硬體與 Jetson 生態系（p.110–140）

### 為什麼要 Edge AI
- 1080p+ 攝影機、LIDAR、超音波、麥克風持續產生資料
- 一個系統 2–10+ 顆感測器
- 雲端來不及，需要本地推論

### Jetson 家族
| 模組 | AI 性能 | 功耗 | 售價 |
|---|---|---|---|
| Jetson Nano（2019 上市） | 0.5 TFLOPS FP16 | 5–10W | $99 / $59（2GB） |
| Jetson TX2 | 1.3 TFLOPS FP16 | 7–15W | $299–749 |
| Jetson Xavier NX | 21 TOPS | 10–15W | $399 |
| Jetson AGX Xavier | 32 TOPS | 10–30W | $1099 |
| **Jetson Orin Nano 4GB** | **20 Sparse TOPS** | 5–10W | $199 |
| **Jetson Orin Nano 8GB** | **40 Sparse TOPS** | 7–15W | $299 |
| Jetson AGX Orin 32/64GB | 200 / 275 TOPS | 15–60W | 高 |

> Orin Nano 是 Nano 的接班人，性能差距非常大（40 TOPS vs 0.5 TFLOPS）。
> 參考文章：https://blog.cavedu.com/2023/03/22/nvidia-jetson-orin-nano-devkit/

### Jetson Nano 2GB vs 4GB
| 項目 | 2GB | 4GB |
|---|---|---|
| RAM | 2 GB | 4 GB |
| CSI 攝影機 | 1 個 | 2 個 |
| 電源 | USB-C | Micro-USB / DC barrel |
| USB Port | 1×3.0 + 2×2.0 + 1×Micro | 4×3.0 + 1×Micro |
| 顯示 | 1× HDMI | 1× HDMI + 1× DisplayPort |
| 無線 | 內附 USB Wi-Fi | M.2 Key E（不含卡） |
| 售價 | $59 | $99 |

### 競品比較
- **Raspberry Pi 4B+**：1.5GHz、1/2/4GB、有 Wi-Fi/BLE，$35–55，沒 GPU 跑 DL 慢。
- **Google Coral Dev Board / USB Accelerator**：TPU 跑 INT8 quantized TFLite 超快（MobileNet 15.7ms），但模型受限 + 需 quantization aware training。
- **Movidius Neural Compute Stick 2 / Intel NCS2**：USB 加速棒。
- **M5StickV / Sipeed**：超低功耗 vision 模組。

### Jetson Nano 的優勢
- **生態系**：JetPack（CUDA + cuDNN + TensorRT + DeepStream + Ubuntu）持續更新。
- **DL Framework 支援度**：PyTorch、TensorFlow、MXNet 都好用。
- **TensorRT 加速**：FP16 / INT8 推論，MobileNet TF 276ms → TF-TRT 61.6ms（4.5×）。

### 缺點
- **沒有內建 Wi-Fi/Bluetooth**（4GB 版），要另外買 dongle。
- **耗電**：5V 4A 起跳，行動應用要好行動電源。
- **2GB / 4GB 已停產**，新專案建議直上 Orin Nano。

### 機器人案例
- **Jetbot**：NVIDIA 官方 + CAVEDU RK-Jetbot
- **MIT Duckietown 2.166**：用 Jetson Nano 跑 Duckiebot
- **AWS DeepRacer**、**MIT Racecar (TX2)**、**MUSHR (Nano)**、**F1tenth (TX2)**
- **DonkeyCar**

### 評估維度（CAVEDU 提的）
**Community / Spec / Price / Ecosystem** — 不是只看 TOPS，社群跟生態系才是長期可用性的關鍵。

---

## Ch 7｜Jetson Inference 本地實作與附錄（p.141–195）

> 這部分是另一條獨立路線：dusty-nv 的 [jetson-inference repo](https://github.com/dusty-nv/jetson-inference)，跟 DLI 的 Jupyter 互動範例**完全分開**。需要的話用 SSH 進 Jetson 直接跑 Python script。

### 開機與連線（type-C 供電的 Nano）
- 兩種模式跟前面一樣：桌面 / SSH。
- Mac/Linux 用 Terminal `ssh`，Windows 用 MobaXterm 或 PuTTY。
- 帳密 `jetson` / `jetson`。

### Linux Terminal 常用指令
```bash
# 系統
sudo shutdown -h now      # 關機
sudo reboot               # 重開機
sudo passwd               # 改密碼

# 檔案 / 目錄
ls                        # 列出目前資料夾
cd <folder>               # 進去
cd ..                     # 回上層
cd ~                      # 回 home
pwd                       # 印出絕對路徑
mkdir / rmdir             # 建立 / 刪除空目錄
clear                     # 清螢幕

# 編輯 / 執行
nano <file>               # 編輯文字檔
python3 xxx.py            # 用 Python 3 執行
man <cmd>                 # 看說明
```

### 安裝 jetson_stats（看資源用）
```bash
git clone https://github.com/rbonghi/jetson_stats.git
cd jetson_stats/
sudo ./install_jetson_stats.sh -s     # 本日已預先完成

jtop                  # 即時看 CPU / GPU / 記憶體 / 溫度
jetson_release        # 看 JetPack / CUDA / cuDNN 版本
```

### 設定 Wi-Fi（沒網路線時）
```bash
sudo nmcli device wifi connect <SSID> password <PASSWORD>
# 例：sudo nmcli device wifi connect MS_AGV_Car password 12345678
ifconfig                  # 看 wlan0 / eth0 IP
```

### Jetson Inference：操作步驟
```bash
# 一次性設定（已預先做好）
cd ~
unzip CAVEDU_jetson_inference.zip
cd CAVEDU_jetson_inference

# 也可下載官方模型
cd ~/jetson-inference/tools
./download-models.sh      # 用方向鍵 + 空白選 GoogleNet / ResNet-18 等
```

> 第一次跑 TensorRT 會花幾分鐘最佳化模型，第二次起就快。換不同模型要重新最佳化。

### 三大 CV 任務指令

#### A. 影像分類（imagenet）
```bash
# 對單張圖片
python3 imagenet-console.py ./images/black_bear.jpg class_result.jpg

# 改用 ResNet-18
python3 imagenet-console.py --network=resnet-18 \
    ./images/black_bear.jpg class_result_rt18.jpg

# 對 USB 攝影機即時串流
python3 imagenet_gvideo.py --camera=/dev/video0 --width=640 --height=480

# 對 CSI 攝影機（Pi Camera V2）
python3 imagenet_gvideo.py --camera=0 --width=640 --height=480
```

支援的網路：`alexnet, googlenet, googlenet-12, resnet-18, resnet-50, resnet-101, resnet-152, vgg-16, vgg-19, inception-v4`。

#### B. 物件偵測（detectnet）
```bash
python3 detectnet-console.py ./images/airplane_1.jpg object_result.jpg

# 換網路（預設 ssd-mobilenet-v2）
python3 detectnet-console.py --network=ssd-inception-v2 \
    ./images/airplane_1.jpg object_result_iv2.jpg

# 即時串流
python3 detectnet_gvideo.py --camera=/dev/video0 --width=640 --height=480
```

console 會印出每個偵測物件的 ClassID、Confidence、座標、寬高、面積、中心。

支援網路（COCO 資料集）：`ssd-mobilenet-v1, ssd-mobilenet-v2, ssd-inception-v2, coco-dog, coco-bottle, coco-chair, coco-airplane, pednet, multiped, facenet`。

#### C. 影像分割（segnet）
```bash
# 注意：segnet 一定要指定 --network
python3 segnet-console.py --network=fcn-resnet18-cityscapes \
    ./images/horse_0.jpg segnet_result.jpg

# 即時串流
python3 segnet_gvideo.py --camera=/dev/video0 --width=640 --height=480
```

可用模型 vs Jetson Nano FPS（節錄）：
| 模型 | 解析度 | 準確率 | Nano FPS |
|---|---|---|---|
| `fcn-resnet18-cityscapes-512x256` | 512×256 | 83.3% | 48 |
| `fcn-resnet18-cityscapes-1024x512` | 1024×512 | 87.3% | 12 |
| `fcn-resnet18-deepscene-576x320` | 576×320 | 96.4% | 26 |
| `fcn-resnet18-mhp-512x320` | 512×320 | 86.5% | 34 |
| `fcn-resnet18-voc-320x320` | 320×320 | 85.9% | 45 |

> 解析度越高 → 準確率提升、FPS 大幅下降。Nano 可即時用 512×256，再上去就要 Xavier。

### GPIO（補充）
J41 Header 跟 Raspberry Pi 相容（部分腳位）。

```python
import Jetson.GPIO as GPIO     # API 跟 RPi.GPIO 一樣
import time

LED_Pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_Pin, GPIO.OUT)

while True:
    GPIO.output(LED_Pin, GPIO.HIGH); time.sleep(2)
    GPIO.output(LED_Pin, GPIO.LOW);  time.sleep(2)
```

按鈕讀值：`value = GPIO.input(input_pin)` 後比 HIGH/LOW。

安裝：https://pypi.org/project/Jetson.GPIO/

### 其他補充題材
- **DeepStream SDK**：影片 AI pipeline，可串 Microsoft Azure 做即時 dashboard。
- **Robotics 開源項目**：Jetbot / MIT Racecar (TX2) / MUSHR (Nano) / F1tenth (TX2)。
- **Google Colab**：跑 `mnist_mlp.py` / `mnist_cnn.py` 練手感。
- **Teachable Machine + 微軟 LOBE**：瀏覽器訓練 → 匯出 tflite → 拷到 Jetson Nano 跑：
  ```bash
  cd ~/TM2
  python3 TM2_tflite.py --model model.tflite --labels labels.txt
  ```
- **Docker**：基於原生系統的獨立環境，DLI 課程用它把 PyTorch + Jupyter + 範例打包，避免把宿主機弄壞。
- **MIT App Inventor for iOS**：手機端 App 開發。

### 何時用哪種 CV 任務
- **Classification**：只想知道「是什麼」
- **Detection**：要知道「在哪裡 + 是什麼」
- **Segmentation**：要 pixel-level，例如自駕車道分割、醫療影像

> 一般來說 Detection > Classification 在準確率上更好（多了空間資訊）。

### 進階認證
- **Jetson AI Specialist** 認證：https://developer.nvidia.com/embedded/learn/jetson-ai-certification-programs
  - 需要拿到 DLI 課程證書 + 提交個人 AI 專案
  - 講師郭俊廷就是這個認證

### 社群
- CAVEDU Line 社群：QR Code 在 p.193
- 機器人王國：https://robotkingdom.com.tw/
- CAVEDU 部落格：https://blog.cavedu.com/
- CAVEDU YouTube

---

## 上課當天 Checklist

開機前：
- [ ] SD 卡先插 Jetson Nano
- [ ] 攝影機（C270）接 USB
- [ ] 接 Micro-USB 線到 PC（不要先接電源）
- [ ] 接 DC 電源變壓器（綠燈亮 → 等 60 秒）
- [ ] PC 出現 `L4T-README` 磁碟 → 表示已連線

連線：
- [ ] Mac Terminal `ssh jetson@192.168.55.1`，密碼 `jetson`
- [ ] `sudo rm -r ~/nvdli-data`
- [ ] `./docker_dli_run.sh`，密碼 `jetson`
- [ ] 另開終端 `sudo jetson_clocks` + `jtop`
- [ ] 瀏覽器 `http://192.168.55.1:8888`，密碼 `dlinano`

跑完課程：
- [ ] 完成 Classification + Regression 兩個專題
- [ ] 通過所有 Assessment
- [ ] 填問卷
- [ ] My Learning → 下載證書（橫式 PDF）
- [ ] 上傳到指定 Google Drive

關機：
- [ ] `exit`（退出 docker）
- [ ] `sudo shutdown -h 0`，密碼 `jetson`
- [ ] 看到 LED 熄滅 → 拔電源

---

## 常用連結

| 用途 | URL |
|---|---|
| DLI 課程頁 | https://learn.nvidia.com/courses/course-detail?course_id=course-v1:DLI+S-RX-02+V2-TW |
| DLI Event Code 入口 | https://learn.nvidia.com/dli-event |
| 羅馬拼音查詢 | https://crptransfer.moe.gov.tw/ |
| Jetson 固定 IP 教學 | https://blog.cavedu.com/2023/07/31/jetson-nano-static-ip/ |
| Orin Nano 開箱 | https://blog.cavedu.com/2023/03/22/nvidia-jetson-orin-nano-devkit/ |
| jetson-inference repo | https://github.com/dusty-nv/jetson-inference |
| Jetson.GPIO | https://pypi.org/project/Jetson.GPIO/ |
| 證書上傳 Drive | https://drive.google.com/drive/folders/1Pjn6TUVro9I88gLExdLN79syAYiv-svL |
