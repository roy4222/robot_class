// 模擬警車燈 - Police Light
// 藍燈和紅燈交替閃爍，模擬警車燈號效果
//
// 多功能擴展板腳位：
//   LED1（藍）= D13
//   LED2（紅）= D12

int led1 = 13;  // 藍燈 (板子上 LED1)
int led2 = 12;  // 紅燈 (板子上 LED2)

void setup() {
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
}

void loop() {
  // 藍燈閃2次
  digitalWrite(led1, HIGH);
  delay(100);
  digitalWrite(led1, LOW);
  delay(100);
  digitalWrite(led1, HIGH);
  delay(100);
  digitalWrite(led1, LOW);
  delay(100);

  // 紅燈閃2次
  digitalWrite(led2, HIGH);
  delay(100);
  digitalWrite(led2, LOW);
  delay(100);
  digitalWrite(led2, HIGH);
  delay(100);
  digitalWrite(led2, LOW);
  delay(100);
}
