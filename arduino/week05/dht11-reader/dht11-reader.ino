// DHT11 溫濕度讀取
// 腳位：DHT11 Data = D4

#include <DHT.h>

#define DHTPIN  4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  Serial.println("DHT11 啟動中...");
}

void loop() {
  delay(2000);  // DHT11 最快每 2 秒讀一次

  float humidity    = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("讀取失敗，請確認接線");
    return;
  }

  Serial.print("溫度: ");
  Serial.print(temperature);
  Serial.print(" °C    濕度: ");
  Serial.print(humidity);
  Serial.println(" %");
}
