# 模擬警車燈 Police Light

## 接線圖

![接線圖](circuit.png)

```
Pin 8 ──→ 藍色 LED (+) ──→ 220Ω ──→ GND
Pin 9 ──→ 紅色 LED (+) ──→ 220Ω ──→ GND
```

## 效果

藍燈快閃 2 次 → 紅燈快閃 2 次 → 循環，模擬警車燈號。

## 學到的觀念

- `digitalWrite()` 控制 LED 開關
- 用 `delay()` 控制閃爍節奏
- 多顆 LED 的交替控制邏輯
