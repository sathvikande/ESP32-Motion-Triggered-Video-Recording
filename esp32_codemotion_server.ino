#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "Room120";    // Your Wi-Fi SSID
const char* password = "Room@120";         // Your Wi-Fi password

WebServer server(80);

const int sensorPin = 23;  // Obstacle sensor
const int ledPin = 2;      // LED
bool motionDetected = false;
bool lastState = false;    // store previous state

void handleMotion() {
  if (motionDetected) {
    server.send(200, "text/plain", "1"); // Send 1 only when motion detected
  } else {
    server.send(200, "text/plain", "");  // Send nothing when no motion
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(sensorPin, INPUT);
  pinMode(ledPin, OUTPUT);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // Start web server
  server.on("/motion", handleMotion);
  server.begin();
}

void loop() {
  motionDetected = !digitalRead(sensorPin);  // Active LOW

  if (motionDetected && !lastState) {
    Serial.println("1");          // Print 1 only once when motion detected
    digitalWrite(ledPin, HIGH);   // Turn on LED
  } else if (!motionDetected && lastState) {
    digitalWrite(ledPin, LOW);    // Turn off LED when motion stops
  }

  lastState = motionDetected;     // Update last state
  server.handleClient();
  delay(100);
}