# EV3 AI with Python

## Envoriment

ev3dev-stretch // rt

python@3.5.3

python-ev3dev2 // library

## Design

Two module

- server
work on main PC

- ev
work on EV

### Server

- collect running data from ev
- expect the shape of course and send its data for ev

### EV

class `EV` to operate indirectly
