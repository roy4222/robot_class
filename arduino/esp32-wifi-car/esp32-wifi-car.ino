// ESP32 + L298N 手機 WiFi 遙控車
// 連線方式：手機 WiFi 選 "ESP32-Car"，密碼 12345678
//          開瀏覽器到 http://192.168.4.1
//
// 接線（L298N → ESP32）：
//   IN1 → GPIO 33   IN2 → GPIO 14   (左馬達方向)
//   IN3 → GPIO 27   IN4 → GPIO 26   (右馬達方向)
//   ENA → GPIO 13   ENB → GPIO 25   (PWM 調速)
//   L298N 的 VCC 接電池正極、GND 與 ESP32 GND 共地
//   ESP32 不要從 L298N 的 5V 供電，自己用 USB 或獨立電源

#include <WiFi.h>
#include <WebServer.h>

const char* AP_SSID = "ESP32-Car";
const char* AP_PASS = "12345678";

// 馬達腳位
const int IN1 = 33, IN2 = 14;   // 左
const int IN3 = 27, IN4 = 26;   // 右
const int ENA = 13, ENB = 25;   // PWM

// PWM 設定（ESP32 Arduino Core 3.x 新 API）
const int PWM_FREQ = 1000, PWM_RES = 8;   // 8-bit: 0~255
int motorSpeed = 200;                      // 預設速度

WebServer server(80);

void setMotor(int in1, int in2, int enPin, int speed) {
  int a, b, pwm;
  if (speed > 0) {
    a = HIGH; b = LOW; pwm = speed;
  } else if (speed < 0) {
    a = LOW;  b = HIGH; pwm = -speed;
  } else {
    a = LOW;  b = LOW;  pwm = 0;
  }
  digitalWrite(in1, a);
  digitalWrite(in2, b);
  ledcWrite(enPin, pwm);
  Serial.printf("  motor IN(%d)=%d IN(%d)=%d EN(%d)=%d\n", in1, a, in2, b, enPin, pwm);
}

void forward()  { setMotor(IN1,IN2,ENA, motorSpeed); setMotor(IN3,IN4,ENB, motorSpeed); }
void backward() { setMotor(IN1,IN2,ENA,-motorSpeed); setMotor(IN3,IN4,ENB,-motorSpeed); }
void turnLeft() { setMotor(IN1,IN2,ENA,-motorSpeed); setMotor(IN3,IN4,ENB, motorSpeed); }
void turnRight(){ setMotor(IN1,IN2,ENA, motorSpeed); setMotor(IN3,IN4,ENB,-motorSpeed); }
void stopAll()  { setMotor(IN1,IN2,ENA,0);           setMotor(IN3,IN4,ENB,0); }

const char PAGE[] PROGMEM = R"HTML(
<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>ESP32 遙控車</title>
<style>
  body{font-family:sans-serif;text-align:center;background:#111;color:#eee;margin:0;padding:20px}
  h2{margin:10px 0 20px}
  .grid{display:grid;grid-template-columns:repeat(3,90px);grid-gap:10px;justify-content:center}
  button{height:90px;font-size:24px;border:0;border-radius:14px;background:#2a7;color:#fff;
         touch-action:manipulation;user-select:none}
  button:active{background:#1c5}
  .stop{background:#c33}.stop:active{background:#911}
  .row{margin-top:20px}
  input[type=range]{width:80%}
</style></head><body>
<h2>ESP32 遙控車</h2>
<div class="grid">
  <div></div>
  <button data-cmd="F">▲</button>
  <div></div>
  <button data-cmd="L">◀</button>
  <button class="stop" data-cmd="S" data-tap="1">■</button>
  <button data-cmd="R">▶</button>
  <div></div>
  <button data-cmd="B">▼</button>
  <div></div>
</div>
<div class="row">速度：<span id="sv">200</span><br>
  <input type="range" min="80" max="255" value="200" oninput="spd(this.value)">
</div>
<script>
  function cmd(c){fetch('/m?c='+c)}
  function spd(v){document.getElementById('sv').innerText=v;fetch('/s?v='+v)}
  document.querySelectorAll('button[data-cmd]').forEach(btn=>{
    const c = btn.dataset.cmd;
    if(btn.dataset.tap){
      btn.addEventListener('click', e=>{e.preventDefault(); cmd(c);});
      return;
    }
    const down = e=>{e.preventDefault(); cmd(c);};
    const up   = e=>{e.preventDefault(); cmd('S');};
    btn.addEventListener('pointerdown', down);
    btn.addEventListener('pointerup',   up);
    btn.addEventListener('pointercancel', up);
    btn.addEventListener('pointerleave', up);
  });
</script></body></html>
)HTML";

void handleRoot() { server.send_P(200, "text/html", PAGE); }

void handleMove() {
  String c = server.arg("c");
  IPAddress ip = server.client().remoteIP();
  Serial.printf("[%lums] <- HTTP /m?c=%s from %s  speed=%d heap=%u\n",
                millis(), c.c_str(), ip.toString().c_str(), motorSpeed, ESP.getFreeHeap());
  if      (c=="F") { Serial.println("  → forward()");  forward();  }
  else if (c=="B") { Serial.println("  → backward()"); backward(); }
  else if (c=="L") { Serial.println("  → turnLeft()"); turnLeft(); }
  else if (c=="R") { Serial.println("  → turnRight()");turnRight();}
  else             { Serial.println("  → stopAll()");  stopAll();  }
  server.send(200, "text/plain", "ok");
}

void handleSpeed() {
  motorSpeed = server.arg("v").toInt();
  server.send(200, "text/plain", "ok");
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println();
  Serial.println("==================================================");
  Serial.println("ESP32-Car booting...");
  Serial.printf("Reset reason: %d\n", (int)esp_reset_reason());
  Serial.printf("Pins: IN1=%d IN2=%d IN3=%d IN4=%d ENA=%d ENB=%d\n",
                IN1,IN2,IN3,IN4,ENA,ENB);

  pinMode(IN1,OUTPUT); pinMode(IN2,OUTPUT); pinMode(IN3,OUTPUT); pinMode(IN4,OUTPUT);
  ledcAttach(ENA, PWM_FREQ, PWM_RES);
  ledcAttach(ENB, PWM_FREQ, PWM_RES);
  stopAll();

  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.print("AP SSID: "); Serial.println(AP_SSID);
  Serial.print("AP IP:   "); Serial.println(WiFi.softAPIP());

  server.on("/", handleRoot);
  server.on("/m", handleMove);
  server.on("/s", handleSpeed);
  server.begin();
  Serial.println("HTTP server started on port 80");
  Serial.println("==================================================");
}

unsigned long lastHeartbeat = 0;
void loop() {
  server.handleClient();
  // 每 5 秒心跳：印 uptime + WiFi 客戶端數 + heap，方便確認 ESP32 還活著
  if (millis() - lastHeartbeat > 5000) {
    lastHeartbeat = millis();
    Serial.printf("[heartbeat] up=%lus clients=%d heap=%u\n",
                  millis()/1000, WiFi.softAPgetStationNum(), ESP.getFreeHeap());
  }
}
