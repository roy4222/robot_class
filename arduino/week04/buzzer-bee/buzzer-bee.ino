// 蜂鳴器演奏 + RGB 呼吸燈 + 警車燈
// 多功能擴展板腳位：
//   Buzzer = D5
//   RGB LED = D9(R), D10(G), D11(B)
//   LED1(藍) = D13, LED2(紅) = D12

int buzzer = 5;
int redPin = 9;
int greenPin = 10;
int bluePin = 11;
int led1 = 13;
int led2 = 12;

// 音階頻率
#define C4  262
#define D4  294
#define E4  330
#define F4  349
#define G4  392
#define A4  440
#define B4  494
#define C5  523
#define D5  587
#define REST 0

// ===== 小蜜蜂 =====
int beeNotes[] = {
  G4, E4, E4, REST,
  F4, D4, D4, REST,
  C4, D4, E4, F4, G4, G4, G4, REST,
  G4, E4, E4, E4,
  F4, D4, D4, D4,
  C4, E4, G4, G4, E4, REST, REST
};
int beeBeats[] = {
  4, 4, 2, 4,
  4, 4, 2, 4,
  4, 4, 4, 4, 4, 4, 2, 4,
  4, 4, 4, 4,
  4, 4, 4, 4,
  4, 4, 4, 4, 2, 4, 4
};

// ===== 生日快樂 =====
int bdayNotes[] = {
  C4, C4, D4, C4, F4, E4, REST,
  C4, C4, D4, C4, G4, F4, REST,
  C4, C4, C5, A4, F4, E4, D4, REST,
  B4, B4, A4, F4, G4, F4, REST
};
int bdayBeats[] = {
  8, 8, 4, 4, 4, 2, 4,
  8, 8, 4, 4, 4, 2, 4,
  8, 8, 4, 4, 4, 4, 2, 4,
  8, 8, 4, 4, 4, 2, 4
};

int tempo = 200;
int rgbColor = 0;  // 0=紅, 1=綠, 2=藍

void setup() {
  pinMode(buzzer, OUTPUT);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
}

void loop() {
  // 播小蜜蜂
  playSong(beeNotes, beeBeats, sizeof(beeNotes) / sizeof(beeNotes[0]));
  delay(1500);

  // 播生日快樂
  playSong(bdayNotes, bdayBeats, sizeof(bdayNotes) / sizeof(bdayNotes[0]));
  delay(1500);
}

void playSong(int notes[], int beats[], int noteCount) {
  for (int i = 0; i < noteCount; i++) {
    int duration = tempo * (4.0 / beats[i]);

    // 播音符
    if (notes[i] == REST) {
      noTone(buzzer);
    } else {
      tone(buzzer, notes[i]);
    }

    // 在音符持續期間跑燈光效果
    for (int t = 0; t < duration; t += 30) {
      updateLights();
      delay(30);
    }

    noTone(buzzer);
    delay(20);
  }
}

// RGB 呼吸 + 警車燈同時跑
int breathVal = 0;
int breathDir = 5;

void updateLights() {
  // RGB 呼吸
  int rPin = (rgbColor == 0) ? redPin : 0;
  int gPin = (rgbColor == 1) ? greenPin : 0;
  int bPin = (rgbColor == 2) ? bluePin : 0;

  analogWrite(redPin,   (rgbColor == 0) ? breathVal : 0);
  analogWrite(greenPin, (rgbColor == 1) ? breathVal : 0);
  analogWrite(bluePin,  (rgbColor == 2) ? breathVal : 0);

  breathVal += breathDir;
  if (breathVal >= 255 || breathVal <= 0) {
    breathDir = -breathDir;
    if (breathVal <= 0) {
      rgbColor = (rgbColor + 1) % 3;  // 換下一個顏色
    }
  }

  // 警車燈交替
  static bool toggle = false;
  toggle = !toggle;
  digitalWrite(led1, toggle ? HIGH : LOW);
  digitalWrite(led2, toggle ? LOW : HIGH);
}
