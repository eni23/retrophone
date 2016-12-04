/***********************************************
 *
 * retroPhone
 *
 *
 ***********************************************/

#include "Arduino.h"
#include <SimpleTimer.h>

#include "config.h"
#include "debouncer.cpp"



/***********************************************
 * Global definitions
 ***********************************************/

Debouncer enc_notify_debounce(ENCODER_NOTIFY_DEBOUNCE_TIME);
Debouncer enc_tick_debounce(ENCODER_TICK_DEBOUNCE_TIME);
SimpleTimer timer;

uint8_t number = 0;
bool rotary_turning = false;

struct RCONFIG {
  uint8_t volume;
  uint16_t freq;
  uint16_t pause;
  uint16_t count;
} ringer_config = {
  240,
  30,
  250,
  22
};




/***********************************************
 * Rotary decoder
 ***********************************************/

uint8_t solve_number(uint8_t num){
  uint8_t     res = 1;
  if (num>2)  res = 2;
  if (num>3)  res = 3;
  if (num>5)  res = 4;
  if (num>8)  res = 5;
  if (num>10) res = 6;
  if (num>12) res = 7;
  if (num>14) res = 8;
  if (num>16) res = 9;
  if (num>18) res = 0;
  return res;
}


void encoder_notify(){
  if (!enc_notify_debounce.check()){
    return;
  }
  if (!rotary_turning){
    number = 0;
    rotary_turning = true;
  }
  else {
    uint8_t result = solve_number(number);
    rotary_turning = false;
    //Serial.write(23);
    Serial.print(result);
  }
}


void encoder_tick(){
  if (!enc_tick_debounce.check()){
    return;
  }
  number++;
}


/***********************************************
 * Ringer
 ***********************************************/

bool ringer_pos;
bool ringer_is_enabled = false;
int ringer_timer_id;
int ringer_counter = 0;
void ringer_on();
void ringer_off();


void ringer_tick(){
  if (ringer_counter > (ringer_config.count-1)){
    ringer_off();
    ringer_timer_id = timer.setTimeout(ringer_config.pause, ringer_on);
    return;
  }
  if (ringer_pos){
    ringer_pos = false;
    analogWrite(RINGER_COIL_1, ringer_config.volume);
    digitalWrite(RINGER_COIL_2, 0);
  }
  else {
    ringer_pos = true;
    analogWrite(RINGER_COIL_2, ringer_config.volume);
    digitalWrite(RINGER_COIL_1, 0);
  }
  ringer_counter++;
}

void update_ringer_config(){
  if (ringer_is_enabled){
    timer.deleteTimer(ringer_timer_id);
    ringer_timer_id = timer.setInterval(ringer_config.freq, ringer_tick);
  }
}


void ringer_on(){
  ringer_is_enabled = true;
  ringer_timer_id = timer.setInterval(ringer_config.freq, ringer_tick);
  ringer_counter = 0;
}

void ringer_off(){
  ringer_is_enabled = false;
  timer.deleteTimer(ringer_timer_id);
  digitalWrite(RINGER_COIL_1, 0);
  digitalWrite(RINGER_COIL_2, 0);
}


/***********************************************
 * Serial helpers
 ***********************************************/

uint16_t unpack_serial_int( uint8_t ch1, uint8_t ch2 ){
  uint16_t u16;
  u16 = ( (uint16_t) ch2 << 8) | ch1;
  return u16;
}


void dump_config(){
  uint8_t freq[2] = { ringer_config.freq & 0xff, ringer_config.freq >> 8 };
  uint8_t pause[2] = { ringer_config.pause & 0xff, ringer_config.pause >> 8 };
  uint8_t count[2] = { ringer_config.count & 0xff, ringer_config.count >> 8 };
  Serial.write(ringer_config.volume);
  Serial.write(freq[0]);
  Serial.write(freq[1]);
  Serial.write(pause[0]);
  Serial.write(pause[1]);
  Serial.write(count[0]);
  Serial.write(count[1]);
}

void read_config(){
  Serial.write(13);
  delay(15);
  digitalWrite(13, HIGH);
  uint8_t data[7];
  uint8_t c=0;
  while (c<7){
    if (Serial.available()){
      data[c] = Serial.read();
      c++;
    }
  }
  ringer_config.volume = data[0];
  ringer_config.freq = unpack_serial_int(data[1], data[2]);
  ringer_config.pause = unpack_serial_int(data[3], data[4]);
  ringer_config.count = unpack_serial_int(data[5], data[6]);
  Serial.write(222);
  update_ringer_config();
  digitalWrite(13, LOW);
}


/***********************************************
 * setup and main loop functions
 ***********************************************/
/*
void init_int_interrupt(){
   cli();
   PCICR =0x02;
   PCMSK1 = 0b00000111;
   sei();
}

ISR(PCINT1_vect) {
   Serial.print("I");
}*/


void setup() {
  Serial.begin(SERIAL_BAUD);

  pinMode(ENCODER_PIN_NOTIFY, INPUT_PULLUP);
  pinMode(ENCODER_PIN_TICK, INPUT_PULLUP);

  pinMode(RINGER_COIL_1, OUTPUT);
  pinMode(RINGER_COIL_2, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_NOTIFY), encoder_notify, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_PIN_TICK), encoder_tick, CHANGE);
  enc_notify_debounce.check();
  enc_tick_debounce.check();
}


uint8_t serial_command;

void loop() {
  if (Serial.available()) {
    serial_command = Serial.read();
    switch (serial_command) {

      // on
      case 1:
        ringer_on();
        break;

      // off
      case 2:
        ringer_off();
        break;

      // dump
      case 4:
        dump_config();
        break;

      // config
      case 5:
        read_config();
        break;

      default:
        Serial.write(220);
        break;
    }
  }
  timer.run();
}
