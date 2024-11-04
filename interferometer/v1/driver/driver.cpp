#define PWR_CTL 2
#define PWR_TST 3
#define PWR_LAS 4
#define DAT_CTL 5
#define DAT_TST 6

#define PWR_GRN 7
#define PWR_YLO 8
#define PWR_RED 9

#define PWR_BUZ 10
#define TONE1 660
#define TONE2 440
#define TONE3 250

#define OK 1
#define WORKING 2
#define ERROR 3

char status = 0;

long compoundMeasurement




void setStatus(char newStatus) {
    digitalWrite(PWR_GRN, LOW);
    digitalWrite(PWR_YLO, LOW);
    digitalWrite(PWR_RED, LOW);
    if (newStatus == OK) {
        digitalWrite(PWR_GRN, HIGH);
        if (status != new_status) {
            tone(PWR_BUZ, TONE1, 100);
        }
    } else if (newStatus == WORKING) {
        digitalWrite(PWR_YLO, HIGH);
        if (status != new_status) {
            tone(PWR_BUZ, TONE2, 100);
            delay(200);
            tone(PWR_BUZ, TONE2, 100);
            delay(200);
        }
    } else if (newStatus == ERROR) {
        digitalWrite(PWR_RED, HIGH);
        if (status != new_status) {
            tone(PWR_BUZ, TONE3, 100);
            delay(200);
            tone(PWR_BUZ, TONE3, 100);
            delay(200);
            tone(PWR_BUZ, TONE3, 100);
            delay(200);
        }
    }
    status = newStatus;
}

void initializePins() {
    pinMode(PWR_CTL, OUTPUT);
    pinMode(PWR_TST, OUTPUT);
    pinMode(PWR_LAS, OUTPUT);
    pinMode(DAT_CTL, INPUT);
    pinMode(DAT_TST, INPUT);
    pinMode(PWR_GRN, OUTPUT);
    pinMode(PWR_YLO, OUTPUT);
    pinMode(PWR_RED, OUTPUT);
    pinMode(PWR_BUZ, OUTPUT);
}

void setup() {
    Serial.begin(9600)
    initializePins()
    collectCompoundMeasurement()
}