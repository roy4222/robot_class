# 智能機器人學與應用

輔仁大學資訊工程學系 114 學年度第二學期

## 課程資訊

- **時間**: 週五 15:40 - 18:30
- **地點**: SF648
- **授課教師**: 范姜永益、王福堂

## 評分方式

| 項目 | 比重 |
|------|------|
| 期中專題 demo | 25% |
| 期末專題 demo | 40% |
| 點名 | 25% |
| NVIDIA 證照 | 15% |
| 期末心得 | 10% |

## 課程進度

| 週次 | 日期 | 主題 | 狀態 |
|------|------|------|------|
| 1 | 02/27 | 停課（228 紀念日） | - |
| 2 | 03/06 | 課程說明（分組） | done |
| 3 | 03/13 | 3D 建模與 3D 列印教學 | done |
| 4 | 03/20 | 控制器介紹與實作練習（ESP32） | done |
| 5 | 03/27 | ESP32 + 手機遙控教學 (1)：APP Inventor + Personal Image Classifier | |
| 6 | 04/03 | 停課（春假） | - |
| 7 | 04/10 | ESP32 + 手機遙控教學 (2) | |
| 8 | 04/17 | ESP32 + 手機遙控教學 (3) | |
| 9 | 04/24 | **期中專題 demo** | |
| 10 | 05/01 | 停課（勞動節） | - |
| 11 | 05/08 | NVIDIA Jetson Nano 證照研習 (1) | |
| 12 | 05/15 | NVIDIA Jetson Nano 證照研習 (2) | |
| 13 | 05/22 | JetBot AI 自駕車實作 (1) | |
| 14 | 05/29 | JetBot AI 自駕車實作 (2) | |
| 15 | 06/05 | JetBot AI 自駕車實作 (3) | |
| 16 | 06/12 | **期末專題 demo** | |
| 17 | 06/19 | 停課（端午節） | - |
| 18 | 06/26 | **期末專題 demo（補）／期末心得報告繳交** | |

## 我的學習目標

這門課的目的是**補硬體短板**，為機器人 side project 打基礎。

### 課程 → Side Project 技能對照

| 課程內容 | 學到的硬體能力 | 用在哪個 Side Project |
|---------|--------------|---------------------|
| ESP32 GPIO / 接線 | 數位/類比 I/O、麵包板 | SO-101 馬達接線、感測器整合 |
| ESP32 馬達控制 | PWM、Servo 驅動 | SO-101 伺服馬達設定與校正 |
| ESP32 + 藍牙/WiFi | 無線通訊協定 | BMO 與手機/電腦的連線控制 |
| APP Inventor | 快速做控制 App | 期中專題、BMO 的 UI 概念 |
| Jetson Nano + 視覺 | 模型部署、攝影機 pipeline | BMO 的視覺、PawAI 畢專 |
| JetBot 自駕車 | 避障、路線跟隨 | Open Duck Mini locomotion |
| NVIDIA 證照 | Jetson 上跑 AI 的標準流程 | 履歷加分 |

### 前半學期重點（ESP32）

- 搞懂電路基礎：電阻、分壓、接地
- Servo 馬達控制練熟（SO-101 全部都是 Servo）
- I2C / SPI / UART 通訊協定概念

### 後半學期重點（Jetson）

- 拿 NVIDIA 證照（免費 15 分）
- 期末專題做超出基本要求的東西，當作品集

## 機器人 Side Project 路線圖

以這門課補硬體能力，支撐以下 side project：

| 優先度 | 專案 | 定位 | 預算 |
|--------|------|------|------|
| P0 | [SO-101](https://huggingface.co/docs/lerobot/so101) | LeRobot 機械手臂，第一個完成型專案 | 中 |
| P1 | [BMO / be-more-agent](https://github.com/brenpoly/be-more-agent) | Raspberry Pi 本地 AI agent 角色機器人 | 低 |
| P2 | [Open Duck Mini](https://github.com/apirrone/Open_Duck_Mini) | 低成本雙足，locomotion 探索 | ~$400 |
| P3 | [ToddlerBot](https://makerworld.com/cs/models/1733983-toddlerbot-release-v2-0-2xc) | 30 DoF humanoid，長期目標 | ~$6000 |

### Phase 0：軟體工程實習（現在）

投軟體工程師實習，建立收入與設備預算。

### Phase 1：SO-101 起手式（1-2 個月）

完成組裝、馬達設定、校正，跑通 teleop，產出文章與 demo 影片。

### Phase 2：BMO 本地 AI Agent（2-4 個月）

在 Raspberry Pi 5 上跑通 wake word → STT → LLM → TTS → vision，做出角色機器人。

### Phase 3：雙足探索（之後）

Open Duck Mini 或其他低成本雙足平台，進入 locomotion 領域。

## 參考教材

1. IoT 物聯網應用 - 使用 ESP32 開發版與 Arduino C 程式語言（尤濬哲）
2. Vision x Voice 影像辨識聲控：雙 V AI 自駕車（施威銘研究室）
3. Raspberry Pi 機器人自造專案（Richard Grimmett）
4. 初學 Jetson Nano 不說 No（曾吉弘、郭俊廷）
5. Raspberry Pi 最佳入門與實戰應用（柯博文）
6. Python 初學特訓班（鄧文淵）

## 目錄結構

```
├── arduino/       # Arduino / ESP32 練習程式碼
├── app-inventor/  # APP Inventor 專案檔
├── jetson/        # Jetson Nano 相關程式碼
├── midterm/       # 期中專題
└── final/         # 期末專題
```
