/* Debugging -----------------------------------------------------------------*/
#define SERIAL_DEBUGGING

// I2C Settings
#define SLAVE_ADDRESS           0x04

/* Sensors -------------------------------------------------------------------*/
// active sensors
#define _SONAR
// #define _LDR
#define _ENCODER

// ultrasonic
#define SONAR_NUM               3       // number of sensors
#define MAX_DISTANCE            200     // maximum distance (in cm) to ping
#define PING_INTERVAL           35      // milliseconds between sensor pings

#define SONAR_LEFT_TRIG         10
#define SONAR_LEFT_ECHO         11

#define SONAR_CENTRE_TRIG       A0
#define SONAR_CENTRE_ECHO       A1

#define SONAR_RIGHT_TRIG        A2
#define SONAR_RIGHT_ECHO        A3

#define ENCODER_NUM 2

#define ENCODER_LEFT_A          2
#define ENCODER_LEFT_B          8
#define ENCODER_RIGHT_A         3
#define ENCODER_RIGHT_B         9

#define DIST_PER_TICK           0.003745   // (in cm)

#define LDR_NUM                 0

/* Motors --------------------------------------------------------------------*/
#define LEFT_MOTOR_A            5
#define LEFT_MOTOR_B            4
#define RIGHT_MOTOR_A           6
#define RIGHT_MOTOR_B           7

/* General -------------------------------------------------------------------*/
#define MAX_SPEED               255
