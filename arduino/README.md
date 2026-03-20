# Arduino 練習專案

使用多功能擴展板（Multi-function Shield）+ Arduino UNO

## 板子腳位對照

| 元件 | 腳位 | 類型 |
|------|------|------|
| LED1（藍） | D13 | 數位輸出 |
| LED2（紅） | D12 | 數位輸出 |
| RGB LED | D9(R) / D10(G) / D11(B) | PWM 輸出 |
| SW1（按鈕） | D2 | 數位輸入 |
| SW2（按鈕） | D3 | 數位輸入 |
| DHT11（溫濕度） | D4 | 數位 |
| Buzzer（蜂鳴器） | D5 | 數位輸出 |
| IR Receiver（紅外線） | D6 | 數位輸入 |
| Rotation（可變電阻） | A0 | 類比輸入 |
| Light（光敏電阻） | A1 | 類比輸入 |
| LM35（溫度感測器） | A2 | 類比輸入 |
| I2C | SDA / SCL | 通訊 |

## 專案列表

| # | 專案 | 用到的觀念 | 用到的元件 |
|---|------|-----------|-----------|
| 1 | [police-light](police-light/) | `digitalWrite`、數位輸出、交替控制 | LED1(D13)、LED2(D12) |
| 2 | [breathing-led](breathing-led/) | `analogWrite`、PWM、呼吸效果 | RGB LED(D9-11)、LED1/2 |
| 3 | [buzzer-bee](buzzer-bee/) | `tone`、頻率與音階、陣列應用 | Buzzer(D5)、RGB LED、LED1/2 |
| 4 | [light-sensor](light-sensor/) | `analogRead`、分壓電路、`map` 映射 | Light(A1)、RGB LED、LED1/2 |

## 學到的核心觀念

```
數位輸出 digitalWrite()     → 開/關（HIGH/LOW）
PWM 輸出 analogWrite()      → 0~255 模擬亮度/轉速
類比輸入 analogRead()        → 讀感測器 0~1023
頻率輸出 tone() / noTone()   → 蜂鳴器發聲
序列通訊 Serial.print()      → 除錯、觀察數值
```

## 編譯與上傳

```bash
# 編譯
arduino-cli compile --fqbn arduino:avr:uno <資料夾>/<檔名>.ino

# 上傳（先確認板子連接埠）
arduino-cli board list
arduino-cli upload -p /dev/cu.usbmodem* --fqbn arduino:avr:uno <資料夾>/<檔名>.ino

# 看 Serial Monitor
arduino-cli monitor -p /dev/cu.usbmodem*
```

## 還沒玩到的板上元件

- [ ] SW1 / SW2 按鈕（D2 / D3）— 數位輸入、中斷
- [ ] DHT11 溫濕度感測器（D4）— 需要函式庫
- [ ] Rotation 可變電阻（A0）— 類比輸入控制
- [ ] LM35 溫度感測器（A2）— 類比讀溫度
- [ ] IR Receiver 紅外線（D6）— 遙控器控制
- [ ] I2C 裝置 — LCD 螢幕等
