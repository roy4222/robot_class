# 🤖 智能機器人學與應用

> **輔仁大學 資訊工程學系** ｜ 114 學年度 第二學期
> 課程目標：補硬體短板，為機器人 side project 打地基。

![NVIDIA Jetson Nano](https://img.shields.io/badge/NVIDIA-Jetson%20Nano-76B900?logo=nvidia&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-Arduino-00979D?logo=arduino&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-ResNet18-EE4C2C?logo=pytorch&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)

---

## ✨ 成果亮點

| 專案 | 內容 | 連結 |
|------|------|------|
| 🏎️ **JetBot 道路跟隨** | Jetson Nano 自駕車。**自製** 收資料 → 訓練（Mac M1 MPS）→ demo pipeline，ResNet18 影像迴歸循跡 | [`jetson/road_following/`](jetson/road_following/README.md) |
| 📱 **ESP32 WiFi 遙控車** | ESP32 架 AP + 網頁，WASD／手機遙控雙馬達小車 | [`arduino/esp32-wifi-car/`](arduino/esp32-wifi-car/) |
| 🔢 **Week08 影像辨識** | PIC 手寫數字分類 + 成果報告 | [`reports/`](reports/) |
| 🎮 **APP Inventor** | 手機控制 App | [`app-inventor/`](app-inventor/) |

> 🌟 期末主軸是 **JetBot 道路跟隨** —— 完整操作手冊與 debug 記錄在
> **[`jetson/road_following/README.md`](jetson/road_following/README.md)**。

---

## 📌 課程資訊

| | |
|---|---|
| 🕒 時間 | 週五 15:40 – 18:30 |
| 📍 地點 | SF648 |
| 👨‍🏫 授課教師 | 范姜永益、王福堂 |

**評分**：期末專題 demo `40%` ｜ 期中專題 demo `25%` ｜ 點名 `25%` ｜ NVIDIA 證照 `15%` ｜ 期末心得 `10%`

---

## 🗓️ 課程進度

| 週 | 日期 | 主題 | 狀態 |
|:--:|:--:|------|:--:|
| 1 | 02/27 | 停課（228 紀念日） | — |
| 2 | 03/06 | 課程說明（分組） | ✅ |
| 3 | 03/13 | 3D 建模與 3D 列印 | ✅ |
| 4 | 03/20 | 控制器介紹與實作（ESP32） | ✅ |
| 5 | 03/27 | ESP32 + 手機遙控 (1)：APP Inventor + Image Classifier | ✅ |
| 6 | 04/03 | 停課（春假） | — |
| 7 | 04/10 | ESP32 + 手機遙控 (2) | ✅ |
| 8 | 04/17 | ESP32 + 手機遙控 (3) | ✅ |
| 9 | 04/24 | **期中專題 demo** | ✅ |
| 10 | 05/01 | 停課（勞動節） | — |
| 11 | 05/08 | NVIDIA Jetson Nano 證照研習 (1) | ✅ |
| 12 | 05/15 | NVIDIA Jetson Nano 證照研習 (2) | ✅ |
| 13 | 05/22 | JetBot AI 自駕車實作 (1) | ✅ |
| 14 | 05/29 | JetBot AI 自駕車實作 (2) | ✅ |
| 15 | 06/05 | JetBot AI 自駕車實作 (3) | ✅ |
| 16 | 06/12 | **期末專題 demo** | 🔄 進行中 |
| 17 | 06/19 | 停課（端午節） | — |
| 18 | 06/26 | **期末專題 demo（補）／期末心得繳交** | ⏳ 待繳 |

---

## 🎯 學習目標

這門課的目的是**補硬體短板**，為機器人 side project 打基礎。

### 課程 → Side Project 技能對照

| 課程內容 | 學到的硬體能力 | 用在哪個 Side Project |
|---------|--------------|---------------------|
| ESP32 GPIO / 接線 | 數位／類比 I/O、麵包板 | SO-101 馬達接線、感測器整合 |
| ESP32 馬達控制 | PWM、Servo 驅動 | SO-101 伺服馬達設定與校正 |
| ESP32 + 藍牙／WiFi | 無線通訊協定 | BMO 與手機／電腦的連線控制 |
| APP Inventor | 快速做控制 App | 期中專題、BMO 的 UI 概念 |
| Jetson Nano + 視覺 | 模型部署、攝影機 pipeline | BMO 的視覺、PawAI 畢專 |
| JetBot 自駕車 | 避障、路線跟隨 | Open Duck Mini locomotion |
| NVIDIA 證照 | Jetson 上跑 AI 的標準流程 | 履歷加分 |

- **前半學期（ESP32）**：電路基礎（電阻／分壓／接地）、Servo 馬達控制、I2C／SPI／UART 概念。
- **後半學期（Jetson）**：拿 NVIDIA 證照、期末專題做超出基本要求的東西當作品集。

---

## 🛣️ 機器人 Side Project 路線圖

以這門課補硬體能力，支撐以下 side project：

| 優先度 | 專案 | 定位 | 預算 |
|:--:|------|------|:--:|
| `P0` | [SO-101](https://huggingface.co/docs/lerobot/so101) | LeRobot 機械手臂，第一個完成型專案 | 中 |
| `P1` | [BMO / be-more-agent](https://github.com/brenpoly/be-more-agent) | Raspberry Pi 本地 AI agent 角色機器人 | 低 |
| `P2` | [Open Duck Mini](https://github.com/apirrone/Open_Duck_Mini) | 低成本雙足，locomotion 探索 | ~$400 |
| `P3` | [ToddlerBot](https://makerworld.com/cs/models/1733983-toddlerbot-release-v2-0-2xc) | 30 DoF humanoid，長期目標 | ~$6000 |

<details>
<summary>📋 執行階段</summary>

- **Phase 0 — 軟體工程實習（現在）**：投實習，建立收入與設備預算。
- **Phase 1 — SO-101 起手式（1–2 個月）**：組裝、馬達設定校正、跑通 teleop，產出文章與 demo 影片。
- **Phase 2 — BMO 本地 AI Agent（2–4 個月）**：在 Raspberry Pi 5 上跑通 wake word → STT → LLM → TTS → vision。
- **Phase 3 — 雙足探索（之後）**：Open Duck Mini 或其他低成本雙足平台，進入 locomotion。

</details>

---

## 📁 目錄結構

```
.
├── arduino/            # ESP32 / Arduino 程式（週數結構 + esp32-wifi-car 遙控車）
├── app-inventor/       # APP Inventor 手機 App 專案
├── jetson/             # Jetson Nano 程式
│   ├── road_following/ #   ⭐ JetBot 道路跟隨自製 pipeline（收資料 / 訓練 / demo）
│   └── *.py            #   相機 / 人臉偵測測試
├── jetson-nano/        # NVIDIA Jetson AI 證照課程素材 + 上課筆記
├── jetbot(1)/          # JetBot 官方教材 + 進度紀錄
├── notes/              # 每週上課筆記
├── reports/            # 成果報告（Week08 影像辨識）
├── scripts/            # 報告產生工具（md → odt 等）
├── midterm/            # 期中專題
└── final/              # 期末專題
```

---

## 📚 參考教材

1. IoT 物聯網應用 — 使用 ESP32 開發板與 Arduino C 程式語言（尤濬哲）
2. Vision x Voice 影像辨識聲控：雙 V AI 自駕車（施威銘研究室）
3. Raspberry Pi 機器人自造專案（Richard Grimmett）
4. 初學 Jetson Nano 不說 No（曾吉弘、郭俊廷）
5. Raspberry Pi 最佳入門與實戰應用（柯博文）
6. Python 初學特訓班（鄧文淵）
