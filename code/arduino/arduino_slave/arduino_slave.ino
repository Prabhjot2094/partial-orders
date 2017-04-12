#include <Wire.h>
#include <Motor.h>
#include <NewPing.h>
#include "config.h"

int speedLeft = 0;
int speedRight = 0;
int sensorIndex = 0;
unsigned int cmd;

motor motorLeft, motorRight;

unsigned int sensorValues[SONAR_NUM + LDR_NUM];     // where the ping distances are stored

NewPing sonar[SONAR_NUM] = {        // sensor object array
    NewPing(SONAR_FAR_LEFT_TRIG, SONAR_FAR_LEFT_ECHO, MAX_DISTANCE),   // each sensor's trigger pin, echo pin, and max distance to ping
    NewPing(SONAR_LEFT_TRIG, SONAR_LEFT_ECHO, MAX_DISTANCE),
    NewPing(SONAR_CENTRE_TRIG, SONAR_CENTRE_ECHO, MAX_DISTANCE),
    NewPing(SONAR_RIGHT_TRIG, SONAR_RIGHT_ECHO, MAX_DISTANCE),
    NewPing(SONAR_FAR_RIGHT_TRIG, SONAR_FAR_RIGHT_ECHO, MAX_DISTANCE)
};

void setup()
{
    Serial.begin(9600);
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
}

void loop()
{
    // fetch ultrasonic values
    for(sensorIndex = 0; sensorIndex < SONAR_NUM; sensorIndex++)
    {
        sensorValues[sensorIndex] = sonar[sensorIndex].ping_cm();
        delay(PING_INTERVAL);
    }

    // fetch LDR values
    sensorValues[sensorIndex++] = analogRead(LDR_0);
    sensorValues[sensorIndex++] = analogRead(LDR_1);
    sensorValues[sensorIndex++] = analogRead(LDR_2);
    sensorValues[sensorIndex++] = analogRead(LDR_3);
    sensorValues[sensorIndex++] = analogRead(LDR_4);
    sensorValues[sensorIndex++] = analogRead(LDR_5);
}

// callback for received data
void receiveData(int byteCount)
{
    if (byteCount == 3)
    {
        while(Wire.available())
        {
            cmd = Wire.read();

            if (cmd == 0)
            {
                speedLeft = Wire.read();
                speedLeft += ((unsigned int)Wire.read() << 8);
            }

            else if (cmd == 1)
            {
                speedRight = Wire.read();
                speedRight += ((unsigned int)Wire.read() << 8);
            }
        }

        if (cmd == 1)
        {
            motorLeft.write(speedLeft);
            motorRight.write(speedRight);
        }
    }
}

// callback for sending data
void sendData()
{
    Wire.write(speedLeft);
}