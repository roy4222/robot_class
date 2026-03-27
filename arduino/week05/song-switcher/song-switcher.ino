// 換歌播放器
// 腳位：Button A = D2, Button B = D3, Buzzer = D5
// Button A：播小蜜蜂（按下立即切換）
// Button B：播生日快樂（按下立即切換）

int btnA   = 2;
int btnB   = 3;
int buzzer = 5;

// 音階頻率
#define C4   262
#define D4   294
#define E4   330
#define F4   349
#define G4   392
#define A4   440
#define B4   494
#define C5   523
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
int beeLen = sizeof(beeNotes) / sizeof(beeNotes[0]);

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
int bdayLen = sizeof(bdayNotes) / sizeof(bdayNotes[0]);

int tempo = 200;

// 播放狀態
int  currentSong  = -1;  // -1=停止, 0=小蜜蜂, 1=生日快樂
int  noteIndex    = 0;
unsigned long lastNoteTime = 0;
unsigned long noteDuration = 0;

unsigned long lastPressA = 0;
unsigned long lastPressB = 0;
const int debounce = 50;

void setup() {
  pinMode(btnA,   INPUT_PULLUP);
  pinMode(btnB,   INPUT_PULLUP);
  pinMode(buzzer, OUTPUT);
}

void switchSong(int song) {
  noTone(buzzer);
  currentSong  = song;
  noteIndex    = 0;
  noteDuration = 0;       // 讓下一個 loop 立即播第一個音
  lastNoteTime = millis();
}

void loop() {
  unsigned long now = millis();

  // 按鈕 A：小蜜蜂
  if (digitalRead(btnA) == LOW && now - lastPressA > debounce) {
    lastPressA = now;
    switchSong(0);
  }

  // 按鈕 B：生日快樂
  if (digitalRead(btnB) == LOW && now - lastPressB > debounce) {
    lastPressB = now;
    switchSong(1);
  }

  // 播放邏輯（非阻塞）
  if (currentSong >= 0 && now - lastNoteTime >= noteDuration) {
    int* notes = (currentSong == 0) ? beeNotes : bdayNotes;
    int* beats = (currentSong == 0) ? beeBeats : bdayBeats;
    int  len   = (currentSong == 0) ? beeLen   : bdayLen;

    if (noteIndex >= len) {
      noTone(buzzer);
      currentSong = -1;  // 播完停止
      return;
    }

    noTone(buzzer);
    if (notes[noteIndex] != REST) {
      tone(buzzer, notes[noteIndex]);
    }

    noteDuration = (unsigned long)(tempo * (4.0 / beats[noteIndex]));
    lastNoteTime = now;
    noteIndex++;
  }
}
