void setup() {
  Serial.begin(9600);
}

void loop() {
  String output = "";
  for (int i = 0; i < 6; i++) {
    output += analogRead(A0 + i);
    if (i < 5) output += ",";
  }
  Serial.println(output);
  delay(1000); //100 = 1ms, 1000 = 1s
}