# 呼吸燈 Breathing LED

## 接線圖

```
Arduino Pin 9 ──→ LED (+長腳) ──→ LED (-短腳) ──→ 220Ω ──→ GND
```

在 Tinkercad 上：
1. 放一個 Arduino Uno
2. 放一個 LED 和一個 220Ω 電阻
3. Pin 9 → LED 陽極（長腳）
4. LED 陰極（短腳）→ 電阻 → GND

## 核心觀念：PWM

`digitalWrite()` 只能開（HIGH）或關（LOW），沒辦法控制亮度。

`analogWrite(pin, value)` 用 **PWM（脈衝寬度調變）** 模擬中間值：
- `value = 0` → 全暗（0% duty cycle）
- `value = 127` → 半亮（50% duty cycle）
- `value = 255` → 全亮（100% duty cycle）

本質上是快速開關，人眼看起來就像在調亮度。

## 可以改的參數

| 參數 | 預設值 | 效果 |
|------|--------|------|
| `fadeStep` | 5 | 改小（如 1）更滑順，改大跳更快 |
| `delayTime` | 30 | 改小呼吸更快，改大更慢更悠閒 |
| `ledPin` | 9 | 換其他 PWM 腳位（3, 5, 6, 10, 11） |

## 進階挑戰

- [ ] 用 `sin()` 函數做更自然的呼吸曲線
- [ ] 接 3 顆 RGB LED，做彩色呼吸
- [ ] 用可變電阻（旋鈕）即時調整呼吸速度
