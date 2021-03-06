#include <Servo.h>


Servo leftX;
Servo leftY;
Servo rightX;
Servo rightY;
//================================================================
// Hardware definitions. You will need to customize this for your specific hardware.
const int LEFTX_SERVO_PIN = 9;
const int LEFTY_SERVO_PIN = 8;
const int RIGHTX_SERVO_PIN = 7;
const int RIGHTY_SERVO_PIN = 6;

//================================================================

// Define the starting and ending angles for the servos

// Left eye
int startAngleLeftX = 0;
int endAngleLeftX = 0;
int startAngleLeftY = 0;
int endAngleLeftY = 0;

// Right eye
int startAngleRightX = 0;
int endAngleRightX = 0;
int startAngleRightY = 0;
int endAngleRightY = 0;

// Set the serial port transmission rate. The baud rate is the number of bits
// per second.
const long BAUD_RATE = 115200;    

//================================================================
// This function is called once after reset to initialize the program.
void setup()
{
  leftX.attach(LEFTX_SERVO_PIN);
  leftY.attach(LEFTY_SERVO_PIN);
  rightX.attach(RIGHTX_SERVO_PIN);
  rightY.attach(RIGHTY_SERVO_PIN);
  
  // Initialize the Serial port for host communication.
  Serial.begin(BAUD_RATE);
}

//================================================================
// This function is called repeatedly to handle all I/O and periodic processing.
// This loop should never be allowed to stall or block so that all tasks can be
// constantly serviced.
void loop()
{
  serial_input_poll();
}

//================================================================
// Polling function to process messages received over the serial port from the
// remote Arduino.  Each message is a line of text containing a single integer
// as text.

void serial_input_poll(void)
{
  while (Serial.available()) {
  
    // When serial data is available, process and interpret the available text.
    // This may be customized for your particular hardware.

    // The default implementation assumes the line contains a single integer
    // which controls the built-in LED state.
    int eyeIntRepresentation = Serial.parseInt(); 
    float xvalue = Serial.parseInt();
    float yvalue = Serial.parseInt();

    // Working with left eye
    if(eyeIntRepresentation == 0){
      moveLeftEye(xvalue, yvalue);
    } else { // Working with right eye
      moveRightEye(xvalue, yvalue);
    }

    // Drive the LED to indicate the value.
    if (xvalue > 5.0)     digitalWrite(LED_BUILTIN, HIGH);
    else           digitalWrite(LED_BUILTIN, LOW);

    // Once all expected values are processed, flush any remaining characters
    // until the line end.  Note that when using the Arduino IDE Serial Monitor,
    // you may need to set the line ending selector to Newline.
    Serial.find('\n');
  }
}

void moveLeftEye(int xAngle, int yAngle){
  Serial.print("Moving left eye\n");
  // Update x angle
  startAngleLeftX = endAngleLeftX;
  endAngleLeftX = xAngle;
  
  // Update y angle
  startAngleLeftY = endAngleLeftY;
  endAngleLeftY = yAngle;

  // make servo move
  linearMove(leftX, startAngleLeftX, endAngleLeftX, 400);
  //linearMove(leftY, startAngleLeftY, endAngleLeftY, 400);
}

void moveRightEye(int xAngle, int yAngle){
  Serial.print("Moving right eye\n");
  // Update x angle
  startAngleRightX = endAngleRightX;
  endAngleRightX = xAngle;

  // Update y angle
  startAngleRightY = endAngleRightY;
  endAngleRightY = yAngle;

  // make servo move
  //linearMove(rightX, startAngleRightX, endAngleRightX, 400);
  //linearMove(rightY, startAngleRightY, endAngleRightY, 400);
}


void linearMove(Servo svo, int start, int end, int duration){
   if(start < end){
       for(int angle = start; angle < end; angle += 1){
           svo.write(angle);
           delay(15);                                
       }
   } else {
      for(int angle = start; angle > end; angle -= 1){
           svo.write(angle);
           delay(15);                                
       }
   }
}
