// 節拍器
// 腳位：Button A = D2, Button B = D3, Buzzer = D5, LED1(藍) = D13, LED2(紅) = D12
// Button A：BPM +50（上限 500）
// Button B：BPM -50（下限 20）

int btnA   = 2;
int btnB   = 3;
int buzzer = 5;
int led1   = 13;
int led2   = 12;

int bpm = 140;  // 40~240 的中間值

unsigned long lastBeat  = 0;
unsigned long lastPressA = 0;
unsigned long lastPressB = 0;
const int debounce = 50;  // 防彈跳時間（ms）

void setup() {
  pinMode(btnA,   INPUT_PULLUP);  // 按下 = LOW
  pinMode(btnB,   INPUT_PULLUP);
  pinMode(buzzer, OUTPUT);
  pinMode(led1,   OUTPUT);
  pinMode(led2,   OUTPUT);
}

void loop() {
  unsigned long now = millis();

  // 按鈕 A：BPM +50
  if (digitalRead(btnA) == LOW && now - lastPressA > debounce) {
    lastPressA = now;
    if (bpm < 500) {
      bpm += 50;
      lastBeat = now;  // 立即以新 BPM 重新計時
    }
  }

  // 按鈕 B：BPM -50
  if (digitalRead(btnB) == LOW && now - lastPressB > debounce) {
    lastPressB = now;
    if (bpm > 20) {
      bpm -= 50;
      lastBeat = now;  // 立即以新 BPM 重新計時
    }
  }

  // 節拍觸發
  unsigned long interval = 60000UL / bpm;
  if (now - lastBeat >= interval) {
    lastBeat = now;
    beat();
  }
}

void beat() {
  tone(buzzer, 1000, 60);   // 嗶 60ms
  digitalWrite(led1, HIGH);
  digitalWrite(led2, HIGH);
  delay(60);
  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
}
