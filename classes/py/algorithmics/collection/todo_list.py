def print_missions(todo_lst):
    """Returns True and prints the missions if they exist, otherwise returns False"""
    if todo_lst:
        print('\nindex | status  | mission ')

        for i, mission in enumerate(todo_lst):
            is_done = 'Done' if mission[1] else 'waiting'
            print(f'{i}     | {is_done:7} | {mission[0]}')
        return True
    
    print('\nThere are no missions on the list')
    return False


def get_valid_index(todo_lst, action_desc):
    """Returns a valid index"""
    while True:
        try:
            ind = int(input(f'\nEnter the index of the mission you want to {action_desc}: '))
            if ind < 0 or ind >= len(todo_lst):
                raise IndexError
            return ind
        except ValueError:
            print('\nPlease enter a number')
        except IndexError:
            print('\nMission does not exist')

todo = []

while True:
    print('\nTo add a new mission enter 1,\nTo remove a mission enter 2,\nTo mark a mission as done enter 3,\nTo print all missions enter 4,\nTo exit enter 5')
    
    while True:
        try:
            command = int(input('\nEnter a command: '))
            break
        except ValueError:
            print('\nPlease enter a number')

    if command == 1:
        new_mission = [input('\nEnter a new mission: '), False]
        todo.append(new_mission)
        print(f'\n"{new_mission[0]}" has been added successfully')

    elif command == 2:
        if not print_missions(todo):
            continue

        action = 'remove'
        mission_ind = get_valid_index(todo, action)
        mission = todo.pop(mission_ind)
        print(f'\nThe mission "{mission[0]}" has been removed.')


    elif command == 3:
        if not print_missions(todo):
            continue
        
        action = 'mark as done'
        mission_ind = get_valid_index(todo, action)
        todo[mission_ind][1] = True
        print(f'\nThe mission "{todo[mission_ind][0]}" has been marked as done')

    elif command == 4:
        print_missions(todo)
    elif command == 5:
        print('\nHave a nice day! 😘')
        break
    else:
        print('\nPlease enter a valid number (1-5)')