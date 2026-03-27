// RGB 呼吸燈 - 搭配多功能擴展板
// RGB LED 接在 D9(紅), D10(綠), D11(藍)
// 三色依序呼吸，同時 D13/D12 跑警車燈

// RGB LED 腳位
int redPin = 9;
int greenPin = 10;
int bluePin = 11;

// 警車燈腳位
int led1 = 13;  // 藍 LED
int led2 = 12;  // 紅 LED

int brightness = 0;
int fadeStep = 5;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
}

void loop() {
  // RGB 呼吸：紅 → 綠 → 藍 輪流
  breathe(redPin);
  breathe(greenPin);
  breathe(bluePin);
}

void breathe(int pin) {
  // 漸亮
  for (int b = 0; b <= 255; b += 5) {
    analogWrite(pin, b);
    policeFlash();  // 同時跑警車燈
  }
  // 漸暗
  for (int b = 255; b >= 0; b -= 5) {
    analogWrite(pin, b);
    policeFlash();
  }
}

// 警車燈閃一次（紅藍交替）
void policeFlash() {
  digitalWrite(led1, HIGH);
  digitalWrite(led2, LOW);
  delay(80);
  digitalWrite(led1, LOW);
  digitalWrite(led2, HIGH);
  delay(80);
}
