from client import is_pressed, turn_right, turn_left, forward, turn_towards, get_position, interact, attack, equip, unequip, set_skin, get_map, stop_actions

set_skin('CCCfC\nBBkBB\n.L TS')

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
        interact('put:Sylvanite')
    elif is_pressed('z'):
        print(interact('show'))
    elif is_pressed('x'):
        interact('take:Sylvanite')
    elif is_pressed('c'):
        interact('put:recipe_light_boots_tier_1')
    elif is_pressed('r'):
        interact('craft:light_boots_tier_1')
    elif is_pressed('f'):
        equip('light_boots_tier_1', 'feet')
    elif is_pressed('g'):
        unequip('feet')
    elif is_pressed('p'):
        set_skin('CDdCvfC\nBBk')
    elif is_pressed('o'):
        set_skin('SLCfC\nBLkBa')
    elif is_pressed('m'):
        print(get_map())
    elif is_pressed('s'):
        stop_actions()
