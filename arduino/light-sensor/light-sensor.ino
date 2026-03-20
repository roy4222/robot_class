// 光敏電阻自動夜燈 - 多功能擴展板
// Light = A1, RGB LED = D9(R)/D10(G)/D11(B), LED1 = D13, LED2 = D12
//
// 效果：
//   環境亮 → 全部燈暗
//   環境暗 → RGB 亮起，越暗越亮
//   很暗時 → 警車燈也啟動當警報

int sensorPin = A1;
int redPin = 9;
int greenPin = 10;
int bluePin = 11;
int led1 = 13;
int led2 = 12;

int darkThreshold = 400;  // 低於這個值算很暗，啟動警報

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int lightValue = analogRead(sensorPin);

  // 光線值映射到亮度（越暗 → 越亮）
  int brightness = map(lightValue, 0, 1023, 255, 0);
  brightness = constrain(brightness, 0, 255);

  // RGB LED 隨暗度亮起（白光）
  analogWrite(redPin, brightness);
  analogWrite(greenPin, brightness);
  analogWrite(bluePin, brightness);

  // 很暗時啟動警車燈警報
  if (lightValue < darkThreshold) {
    digitalWrite(led1, HIGH);
    digitalWrite(led2, LOW);
    delay(100);
    digitalWrite(led1, LOW);
    digitalWrite(led2, HIGH);
    delay(100);
  } else {
    digitalWrite(led1, LOW);
    digitalWrite(led2, LOW);
    delay(100);
  }

  Serial.print("Light: ");
  Serial.print(lightValue);
  Serial.print("  Brightness: ");
  Serial.println(brightness);
}
