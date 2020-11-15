// RemoteUserInterface.ino : demonstrate communication across the Internet using a
// Python-based MQTT bridge and MQTT server.

// This example implements a networked user interface by sending sensor data
// over the host serial port.  These can be forwarded to a remote MQTT server
// using the arduino_mqtt_bridge.py Python application on an attached computer.
// The messages are broadcast to all clients subscribed to the message stream.
// The details of remote connection are managed by the bridge application; all
// this Arduino sketch needs to manage is sending and receiving lines of text
// over the serial port.

// This example is configured to provide for up to five channels of output, each
// ranging from 0 to 100 inclusive.  If this is used in conjunction with the
// qt_mqtt_plotter.py utility, the data will be interpreted as "X Y R G B",
// where X and Y are point coordinates and R, G, and B define a color.

// This example also supports receiving messages from the network.  The default
// implementation turns the on-board LED on or off based on an integer input,
// but could be extended, e.g. to produce sounds.

//================================================================
// Hardware definitions. You will need to customize this for your specific hardware.
//const int tiltSwitchPin   = 6;    // Specify a pin for a tilt switch user input.
//const int sonarTriggerPin = 7;    // Specify a pin for a sonar trigger output.
//const int sonarEchoPin    = 8;    // Specify a pin for a sonar echo input.
//const int photoInput      = A0;   // Specify the analog channel for a photoreflector input.

//================================================================
// Current state of the five output channels.  Each may range from 0 to 100,
// inclusive.  Illegal values will be clamped to this range on send.  The
// specific relationship between your sensor inputs and these values will need
// to be customized for your hardware.

//int x_value = 50;  // Initial position is the center of the plot (50, 50).
//int y_value = 50;
//int r_value = 0;   // Initial color is pure black (0,0,0).
//int g_value = 0;
//int b_value = 0;

// Set the serial port transmission rate. The baud rate is the number of bits
// per second.
const long BAUD_RATE = 115200;    

//================================================================
// This function is called once after reset to initialize the program.
void setup()
{
  // Initialize the Serial port for host communication.
  Serial.begin(BAUD_RATE);

  // Initialize the digital input/output pins.  You will need to customize this
  // for your specific hardware.
  pinMode(LED_BUILTIN, OUTPUT);
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
    float value = Serial.parseFloat();

    // Drive the LED to indicate the value.
    if (value > 5.0)     digitalWrite(LED_BUILTIN, HIGH);
    else           digitalWrite(LED_BUILTIN, LOW);

    // Once all expected values are processed, flush any remaining characters
    // until the line end.  Note that when using the Arduino IDE Serial Monitor,
    // you may need to set the line ending selector to Newline.
    Serial.find('\n');
  }
}
