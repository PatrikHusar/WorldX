from client import is_pressed, turn_right, turn_left, forward, turn_towards, get_position, interact, attack, equip, unequip

while True:
    if is_pressed('w'):
        forward()
    elif is_pressed('d'):
        turn_right()
    elif is_pressed('a'):
        turn_left()
    elif is_pressed('e'):
        interact('open')
    elif is_pressed(' '):
        attack()
    elif is_pressed('q'):
        interact('put:')
    elif is_pressed('z'):
        print(interact('show'))
    elif is_pressed('x'):
        interact('take:')
    elif is_pressed('c'):
        interact('put:')
    elif is_pressed('r'):
        interact('craft:')
    elif is_pressed('f'):
        equip('', '')
    elif is_pressed('g'):
        unequip('')
