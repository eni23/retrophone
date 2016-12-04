# PC/Arduino protocol

## Commands

1: ring on
  send 1
  no response

2: ring off
  send 2
  no response

4: dump config
  send 4
  response: RCONFIG

5: set config:
  send 5
  wait for 13
  send RCONFIG
  wait for 222

## Sended data

start char: 23
data: key

start char: 24
data: hook status

## Ring config struct
```c
struct RCONFIG {
  uint8_t volume;
  uint16_t freq;
  uint16_t pause;
  uint16_t count;
}
```
