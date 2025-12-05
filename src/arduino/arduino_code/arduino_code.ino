
int vib_pins[5] = {3,5,6,9,10};



void setup() {
  for (int i=0; i < 5; i++){ 
    pinMode(vib_pins[i],OUTPUT);
    analogWrite(vib_pins[i],0);
  }
  // Initialize serial communication
  Serial.begin(9600);
  Serial.flush();
}

void loop() {
  // Check if there is any data available to read
  if (Serial.available() > 0) {
    // Read the incoming string
    String inputString = Serial.readStringUntil('\n');

    // Parse the string into individual values
    char inputArray[200];
    inputString.toCharArray(inputArray, 100);
    char *token = strtok(inputArray, ",");
    
    int values[5];
    int count = 0;
    // Loop through the tokens and store them in the array
    while (token != NULL) {
      if (count < 5) {
        values[count] = atoi(token); // Convert the token to an integer
        count++;
      }
      token = strtok(NULL, ",");
    }
    // Check if exactly 5 values were received
    if (count == 5) {
      for (int i = 0; i < 5; i++) {
        Serial.print("Received value ");
        Serial.print(i + 1);
        Serial.print(": ");
        Serial.println(values[i]);
        analogWrite(vib_pins[i], values[i]);
      }
    } else {
      Serial.println("Error: Exactly 5 values are required.");
    }
  }
}
