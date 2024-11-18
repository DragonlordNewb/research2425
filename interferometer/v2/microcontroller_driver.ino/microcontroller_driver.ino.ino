#define CONTROL_SENSOR_DATA A0    // Analog pin where control sensor data comes in
#define TEST_SENSOR_DATA A1       // Analog pin where test sensor data comes in
#define LASER_POWER 2             // Digital pin where voltage is provided for laser

#define RED_LED_POWER 3           // Pin for red LED    - Red LED on: fatal error/system failure - Red LED blink: minor error/weak signal
#define GREEN_LED_POWER 4         // Pin for green LED  - Green LED blink: success
#define YELLOW_LED_POWER 5        // Pin for yellow LED - Yellow LED on: system calibration in process - Yellow LED blink: activation warning

#define TRIGGER_VOLTAGE_LEVEL 512 // Analog read input (ranging 0-1023) for measurement trigger
#define MEASUREMENT_COUNT 1     // Number of measurements per data point
#define LASER_COOLDOWN_DELAY 50   // Laser cooldown delay, in milliseconds, between measurements 
#define WEAK_SIGNAL_THRESHOLD 10  // Tick threshold below which the signal is considered weak
#define USE_CONTROL_SENSOR false   // true: check for time delay between control and test triggers - false: check for time delay between laser volting and test trigger
#define DO_CALIBRATION false       // true: run calibration - false: don't run calibration

long currentMeasurement = 0;
long measurements[MEASUREMENT_COUNT];
long dataPoint = 0.0;

void setupPins() {
  pinMode(LASER_POWER, OUTPUT);
  pinMode(RED_LED_POWER, OUTPUT);
  pinMode(GREEN_LED_POWER, OUTPUT);
  pinMode(YELLOW_LED_POWER, OUTPUT);
}

void blinkLED(int pin) {
  for (int i = 0; i < 3; i++) {
    digitalWrite(pin, HIGH);
    delay(100);
    digitalWrite(pin, LOW);
    delay(100);
  }
}

void calibrate() {
  if (!DO_CALIBRATION) { 
    return; 
  }
  bool ok;
  digitalWrite(YELLOW_LED_POWER, HIGH);
  while (true) {
    ok = true;
    // Check if both sensors read zero for ten data point's worth of time
    for (int i = 0; i < LASER_COOLDOWN_DELAY * MEASUREMENT_COUNT; i++) {
      if (analogRead(CONTROL_SENSOR_DATA) < TRIGGER_VOLTAGE_LEVEL || analogRead(TEST_SENSOR_DATA) < TRIGGER_VOLTAGE_LEVEL) {
        ok = false;
        blinkLED(RED_LED_POWER);
        delay(LASER_COOLDOWN_DELAY);
        break;
      }
    }
    if (ok) {
      break;
    }
  }
  blinkLED(GREEN_LED_POWER);
  digitalWrite(LASER_POWER, HIGH);
  delay(100);
  while (true) {
    ok = true;
    // Check if both sensors read zero for ten data point's worth of time
    for (int i = 0; i < LASER_COOLDOWN_DELAY * MEASUREMENT_COUNT; i++) {
      if (analogRead(CONTROL_SENSOR_DATA) > TRIGGER_VOLTAGE_LEVEL || analogRead(TEST_SENSOR_DATA) > TRIGGER_VOLTAGE_LEVEL) {
        ok = false;
        blinkLED(RED_LED_POWER);
        delay(LASER_COOLDOWN_DELAY);
        break;
      }
    }
    if (ok) {
      break;
    }
  }
  blinkLED(GREEN_LED_POWER);
  long start = micros();
  long count = 0;
  while (micros() < start + 1000000) { count++; }
  Serial.print("Calibrated ticks per second: ");
  Serial.print(count);
  Serial.print("... ");
  digitalWrite(YELLOW_LED_POWER, LOW);
}

void recordDataPoint() {
  for (int i = 0; i < MEASUREMENT_COUNT; i++) {
    if (USE_CONTROL_SENSOR) {
      currentMeasurement = micros();
      digitalWrite(LASER_POWER, HIGH);
      while (analogRead(CONTROL_SENSOR_DATA) > TRIGGER_VOLTAGE_LEVEL);
      while (analogRead(TEST_SENSOR_DATA) > TRIGGER_VOLTAGE_LEVEL);
      currentMeasurement = micros() - currentMeasurement;
      // Serial.println(currentMeasurement);
      digitalWrite(LASER_POWER, LOW);
      measurements[i] = currentMeasurement;
      delay(LASER_COOLDOWN_DELAY);
    } else {
      currentMeasurement = micros();
      digitalWrite(LASER_POWER, HIGH);
      while (analogRead(TEST_SENSOR_DATA) > TRIGGER_VOLTAGE_LEVEL);
      currentMeasurement = micros() - currentMeasurement;
      // Serial.println(currentMeasurement);
      digitalWrite(LASER_POWER, LOW);
      measurements[i] = currentMeasurement;
      delay(LASER_COOLDOWN_DELAY);
    }
  }

  dataPoint = 0;
  for (int i = 0; i < MEASUREMENT_COUNT; i++) {
    dataPoint += measurements[i];
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println("Setting up ...");
  Serial.print("  Setting up pins ...");
  setupPins();
  Serial.print("Done.\n\r  Calibrating ...");
  calibrate();
  Serial.println("Done.\n\rSetup complete.");
  Serial.println("START");
  blinkLED(YELLOW_LED_POWER);
}

void loop() {
  recordDataPoint();
  if (dataPoint == 0) {
    Serial.println("FAIL 0");
    blinkLED(RED_LED_POWER);
  } else if (dataPoint < WEAK_SIGNAL_THRESHOLD) {
    blinkLED(YELLOW_LED_POWER);
    Serial.write("WEAK ");
    Serial.println(dataPoint);
  } else {
    Serial.write("GOOD ");
    Serial.println(dataPoint);
  }
}