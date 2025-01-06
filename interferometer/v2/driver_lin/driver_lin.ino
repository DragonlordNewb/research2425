#define LASER_POWER 32
#define SENSOR_POWER 30
#define SENSOR_DATA 28

#define SIGNAL_POSITIVE 0
#define SIGNAL_NEGATIVE 1
#define MEASUREMENT_COUNT 10

#define LASER_COOLDOWN 10

unsigned int currentMeasurement = 0;
int measurementIndex = 0;
unsigned int measurements[MEASUREMENT_COUNT];
unsigned int rawData;
double averageData;

void configurePins() {
  pinMode(LASER_POWER, OUTPUT);
  pinMode(SENSOR_POWER, OUTPUT);
  pinMode(SENSOR_DATA, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void takeMeasurement() {
  currentMeasurement = ARM_DWT_CYCCNT;
  digitalWrite(LASER_POWER, HIGH);
  while (digitalRead(SENSOR_DATA) == SIGNAL_NEGATIVE);
  digitalWrite(LASER_POWER, LOW);
  currentMeasurement = ARM_DWT_CYCCNT - currentMeasurement;
  measurements[measurementIndex] = currentMeasurement;
  measurementIndex++;
  delay(LASER_COOLDOWN);
}

void collectData() {
  rawData = 0.0;
  measurementIndex = 0;
  for (int i = 0; i < MEASUREMENT_COUNT; i++) {
    takeMeasurement();
    rawData += measurements[measurementIndex];
  }
  averageData = (double)(rawData) / MEASUREMENT_COUNT;
}

void setup() {
  Serial.begin(9600);
  configurePins();
  Serial.println("- Pins set up");
  digitalWrite(SENSOR_POWER, HIGH);
  delay(100); // this processor is fast and don't want to overdo it
  Serial.println("- Sensor powered on");
  digitalWrite(LED_BUILTIN, HIGH);
}

void loop() {
  collectData();
  Serial.println(averageData);
}