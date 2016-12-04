#ifndef __CONFIG_H
  #define __CONFIG_H

  #define SERIAL_BAUD                   19200

  #define ENCODER_PIN_NOTIFY            2
  #define ENCODER_PIN_TICK              3

  // WARNING: changing those values can make number detection unreliable
  #define ENCODER_NOTIFY_DEBOUNCE_TIME  8
  #define ENCODER_TICK_DEBOUNCE_TIME    8

  #define RINGER_COIL_1                 9
  #define RINGER_COIL_2                 10

#endif
