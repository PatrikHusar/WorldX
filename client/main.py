from client import is_pressed, turn_right, turn_left, forward, turn_towards, get_position, interact

while True:
    if is_pressed('w'):
        forward()
    elif is_pressed('d'):
        turn_right()
    elif is_pressed('a'):
        turn_left()
    elif is_pressed('e'):
        interact()
