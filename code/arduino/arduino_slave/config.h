/* Debugging -----------------------------------------------------------------*/
//#define SERIAL_DEBUGGING

/* i2c settings --------------------------------------------------------------*/
#define SLAVE_ADDRESS 0x04

/* Sensors -------------------------------------------------------------------*/
// ultrasonic
#define SONAR_NUM       5       // number of sensors
#define MAX_DISTANCE    300     // maximum distance (in cm) to ping
#define PING_INTERVAL   35      // milliseconds between sensor pings

#define SONAR_FAR_LEFT_TRIG     11
#define SONAR_FAR_LEFT_ECHO     6

#define SONAR_LEFT_TRIG         12
#define SONAR_LEFT_ECHO         7

#define SONAR_CENTRE_TRIG       13
#define SONAR_CENTRE_ECHO       8

#define SONAR_RIGHT_TRIG        0
#define SONAR_RIGHT_ECHO        9

#define SONAR_FAR_RIGHT_TRIG    1
#define SONAR_FAR_RIGHT_ECHO    10

// LDR
#define LDR_NUM 6

#define LDR_0   A0
#define LDR_1   A1
#define LDR_2   A2
#define LDR_3   A3
#define LDR_4   A6
#define LDR_5   A7

/* Motors --------------------------------------------------------------------*/
#define LEFT_MOTOR_A    5
#define LEFT_MOTOR_B    4
#define RIGHT_MOTOR_A   3
#define RIGHT_MOTOR_B   2

/* General -------------------------------------------------------------------*/
#define MAX_SPEED   255