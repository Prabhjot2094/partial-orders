#include <Wire.h>
#include <Motor.h>
#include <NewPing.h>
#include "config.h"

#define HIGHBYTE(word) (word >> 8)
#define LOWBYTE(word) (word & 0x00FF)

int speedLeft = 0;
int speedRight = 0;
unsigned int cmd;

motor motorLeft, motorRight;

unsigned long pingTimer[SONAR_NUM];     // when each pings
unsigned int sonarData[SONAR_NUM];      // where the ping distances are stored
unsigned int ldrData[LDR_NUM];
uint8_t sensorDataInBytes[(SONAR_NUM + LDR_NUM) * 2];
uint8_t currentSensor = 0; // Which sensor is active.

NewPing sonar[SONAR_NUM] = {        // sensor object array
    NewPing(SONAR_FAR_LEFT_TRIG, SONAR_FAR_LEFT_ECHO, MAX_DISTANCE),   // each sensor's trigger pin, echo pin, and max distance to ping
    NewPing(SONAR_LEFT_TRIG, SONAR_LEFT_ECHO, MAX_DISTANCE),
    NewPing(SONAR_CENTRE_TRIG, SONAR_CENTRE_ECHO, MAX_DISTANCE),
    NewPing(SONAR_RIGHT_TRIG, SONAR_RIGHT_ECHO, MAX_DISTANCE),
    NewPing(SONAR_FAR_RIGHT_TRIG, SONAR_FAR_RIGHT_ECHO, MAX_DISTANCE)
};

inline int getWord(short lowByte, short highByte)
{
    return ((highByte << 8) | lowByte);
}

void setup()
{
    #ifdef SERIAL_DEBUGGING
    Serial.begin(9600);
    #endif
    // initialize i2c as slave
    Wire.begin(SLAVE_ADDRESS);

    // define callbacks for i2c communication
    Wire.onReceive(receiveData);
    Wire.onRequest(sendData);

    // motor setup
    motorLeft.setPins(LEFT_MOTOR_A, LEFT_MOTOR_B);
    motorRight.setPins(RIGHT_MOTOR_A, RIGHT_MOTOR_B);

    motorLeft.setMaxSpeed(MAX_SPEED);
    motorRight.setMaxSpeed(MAX_SPEED);

    motorLeft.initialise();
    motorRight.initialise();

    // LDR setup
    pinMode(LDR_0, INPUT);
    pinMode(LDR_1, INPUT);
    pinMode(LDR_2, INPUT);
    pinMode(LDR_3, INPUT);
    pinMode(LDR_4, INPUT);
    pinMode(LDR_5, INPUT);

    // ultrasonic setup
    pingTimer[0] = millis() + 75; // First ping start in ms.
    for (uint8_t i = 1; i < SONAR_NUM; i++)
        pingTimer[i] = pingTimer[i - 1] + PING_INTERVAL;
}

void loop()
{
    for (uint8_t i = 0; i < SONAR_NUM; i++)
    {
        if (millis() >= pingTimer[i])
        {
            pingTimer[i] += PING_INTERVAL * SONAR_NUM;
            
            if (i == 0 && currentSensor == SONAR_NUM - 1)
                oneSensorCycle(); // Do something with results.

            sonar[currentSensor].timer_stop();
            currentSensor = i;
            sonarData[currentSensor] = 0;
            sonar[currentSensor].ping_timer(echoCheck);
        }
    }
}

void echoCheck() // If ping echo, set distance to array.
{ 
  if (sonar[currentSensor].check_timer())
    sonarData[currentSensor] = sonar[currentSensor].ping_result / US_ROUNDTRIP_CM;
}

void oneSensorCycle() // split all sonar data into bytes
{ 
    for (uint8_t sensorIndex = 0; sensorIndex < SONAR_NUM; sensorIndex++)
    {
        sensorDataInBytes[sensorIndex*2 + 0] = HIGHBYTE(sonarData[sensorIndex]);
        sensorDataInBytes[sensorIndex*2 + 1] = LOWBYTE(sonarData[sensorIndex]);
    }
}

void fetchLDRData()
{
    // fetch LDR values
    ldrData[0] = analogRead(LDR_0);
    ldrData[1] = analogRead(LDR_1);
    ldrData[2] = analogRead(LDR_2);
    ldrData[3] = analogRead(LDR_3);
    ldrData[4] = analogRead(LDR_4);
    ldrData[5] = analogRead(LDR_5);

    for (uint8_t sensorIndex = 0; sensorIndex < LDR_NUM; sensorIndex++)
    {
        sensorDataInBytes[(SONAR_NUM + sensorIndex)*2 + 0] = HIGHBYTE(ldrData[sensorIndex]);
        sensorDataInBytes[(SONAR_NUM + sensorIndex)*2 + 1] = LOWBYTE(ldrData[sensorIndex]);
    }
}

// callback for received data
void receiveData(int byteCount)
{
    if (byteCount == 6)         // one command, one no-of-bytes, 4 bytes
    {
        while(Wire.available())
        {
            cmd = Wire.read();

            if (cmd == 0)       // cmd = 0 for motor speeds
            {
                int dataByteCount = Wire.read();

                if (dataByteCount == 4)     // two speeds split into two bytes each
                {
                    speedLeft = getWord(Wire.read(), Wire.read());      // remember C++ order of evaluation
                    speedRight = getWord(Wire.read(), Wire.read());

                    motorLeft.write(speedLeft);
                    motorRight.write(speedRight);

                    #ifdef SERIAL_DEBUGGING
                    
                    Serial.print(speedLeft);
                    Srial.print(" ");
                    Serial.println(speedRight);
                    
                    #endif
                }
            }
        }
    }

    else        // lifesaver - this removes all erroneous data from the i2c buffer
    {
        while (Wire.available())
        {
            Wire.read();
        }
    }
}

// callback for sending data
void sendData()
{
    fetchLDRData();
    Wire.write(sensorDataInBytes, (SONAR_NUM + LDR_NUM)*2);
}