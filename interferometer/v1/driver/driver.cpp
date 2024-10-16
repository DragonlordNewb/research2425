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

void alert(int count, int freq, int light) {
    for (int i = 0; i < count; i++) {
        tone(PWR_BUZ, freq, 100);
    }
}

void setup() {
    Serial.begin(9600)
}