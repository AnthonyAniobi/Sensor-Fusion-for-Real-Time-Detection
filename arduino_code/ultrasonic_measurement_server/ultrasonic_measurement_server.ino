#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

#ifndef STASSID
#define STASSID "Airtel_X25A_5ED8"
#define STAPSK "54AE72CD"
#endif

#define TRIG_PIN 12  // GPIO 12 for trigger. D6
#define ECHO_PIN 14 // GPIO 14 for echo.  D5

const char* ssid = STASSID;
const char* password = STAPSK;

ESP8266WebServer server(80);

const int led = 13;
float distance_cm = 0;


void handleDistance() {
  // delay(50);
  Serial.println("Starting server");
  Serial.print("Distance: ");
  Serial.println(distance_cm);
  String result;
  result += "  {";
  result += "\"distance_cm\": " + String(distance_cm) ;
  result += "}";
  server.sendHeader("Cache-Control", "no-cache");
  server.send(200, "text/javascript; charset=utf-8", result);
  Serial.println("ending server");
}

void setup(void) {
  pinMode(led, OUTPUT);
  digitalWrite(led, 0);
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  if (MDNS.begin("esp8266")) { Serial.println("MDNS responder started"); }

  server.on("/", handleDistance);

  server.begin();
  Serial.println("HTTP server started");
}

void loop(void) {
  server.handleClient();
  MDNS.update();
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  distance_cm = pulseIn(ECHO_PIN, HIGH)/58.0;
}



  