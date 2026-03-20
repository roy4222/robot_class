# 光敏電阻自動夜燈

## 接線圖

```
        光敏電阻（分壓電路）
5V ──→ [光敏電阻] ──┬── A0
                     │
                  [10kΩ]
                     │
                    GND

        LED
Pin 9 ──→ LED (+) ──→ 220Ω ──→ GND
```

在 Tinkercad 上：
1. 搜尋 "Photoresistor" 放一個光敏電阻
2. 光敏電阻一腳接 5V，另一腳接 A0
3. A0 同時透過 10kΩ 電阻接 GND（這就是分壓）
4. LED 接 Pin 9 + 220Ω

## 核心觀念：分壓電路

光敏電阻不能直接接 A0，需要搭一個固定電阻組成**分壓電路**：

```
5V ──→ R_光敏 ──┬── R_固定 ──→ GND
                │
               A0（量這裡的電壓）
```

A0 讀到的電壓 = 5V × R_固定 / (R_光敏 + R_固定)

- **亮** → R_光敏 變小 → A0 電壓高 → `analogRead` 值大
- **暗** → R_光敏 變大 → A0 電壓低 → `analogRead` 值小

### 為什麼需要分壓？

Arduino 的 `analogRead()` 是量**電壓**，不是量電阻。
光敏電阻的阻值會變，但 Arduino 看不到阻值，只能看電壓。
分壓電路就是把「阻值變化」轉成「電壓變化」讓 Arduino 讀。

## 新函數

| 函數 | 作用 |
|------|------|
| `analogRead(pin)` | 讀類比值，回傳 0~1023 |
| `map(value, fromLow, fromHigh, toLow, toHigh)` | 數值範圍映射 |
| `constrain(value, min, max)` | 限制值在範圍內 |
| `Serial.begin(9600)` | 開啟序列通訊 |
| `Serial.print()` | 印值到 Serial Monitor |

## Tinkercad 操作提示

模擬跑起來後，**點光敏電阻**會出現一個滑桿可以調整光線強度，
就能看到 LED 亮度跟著變。同時打開 Serial Monitor 看數值變化。

## 進階挑戰

- [ ] 加蜂鳴器，太暗時發出警報聲
- [ ] 用多顆 LED 做光線等級指示（像手機訊號格）
- [ ] 搭配之前的呼吸燈，暗的時候才啟動呼吸效果
