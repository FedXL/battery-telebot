

def valid_battery_code(battery_code: str) -> bool | tuple[bool, str] | tuple[dict[str, str], bool]:
    """
    Validate a 12-digit battery code based on the given criteria.
    Args:
        battery_code (str): The battery code to validate.
    Returns:
        bool: True if the battery code is valid, False otherwise.
    """
    battery_code = battery_code.strip(" ").replace('_','').replace("-", "").replace(" ", "").replace('.','').replace(',','').upper()
    return_battery_number = battery_code
    len_battery = len(battery_code)



    if  len_battery not in [11,12]:
        print(f'Не верная длинна кода {len_battery}')
        return False

    if len_battery == 12:
        first_pref = battery_code[0]
        if first_pref not in ('E','C','С','Е'):
            print(f'Первый символ не E или C {first_pref}')
            return False , 'Первый символ не E или C'

        else:
            battery_code = battery_code[1:]
    else:
        first_pref = None
    capacity = battery_code[0:2]
    day = battery_code[2:5]
    year = battery_code[5]
    team = battery_code[6:8]
    battery_number = battery_code[8:12]
    print(capacity, day, year, team, battery_number, sep="|")
    assert len(capacity + day + year + team + battery_number) == 11, ('Накосячил ты с кодом')
    valid_two_digit_numbers = {'42', '50', '55', '60', '62', '64', '65', '66', '70', '75', '77', '90', '95', '00', '32',
                               '40', '90', '10', '30'}
    if capacity not in valid_two_digit_numbers:
        print('Не валидная ёмкость аккумулятора')
        return False , 'Не валидная ёмкость аккумулятора'
    if not (1 <= int(day) <= 365):
        print(day,'Не валидный день')
        return False , 'Не валидный день'
    if year not in ['3', '4', '5']:
        print(year,'Неправильный год')
        return False , 'Неправильный год'
    if not (1 <= int(team) <= 31):
        print(team,'Неправильный номер бригады')
        return False, 'Неправильный номер бригады'
    if not (1 <= int(battery_number) <= 999):
        print(battery_number,"Неправильный номер")
        return False, 'Неправильный номер'
    return {'capacity': capacity, 'day': day, 'year': year, 'team': team, 'number': battery_number,'serial':return_battery_number}, False



if __name__ == '__main__':
    print('1')
    assert valid_battery_code('С42-001-3-01-001')[0] == {'capacity': '42', 'day': '001', 'year': '3', 'team': '01', 'number': '001'}
    print('2')
    assert valid_battery_code('Е42-001-3-01-001')[0] == {'capacity': '42', 'day': '001', 'year': '3', 'team': '01', 'number': '001'}
    print('3')
    assert  valid_battery_code('С42-001-2-4-001')[0] == False
    print('4')
    assert valid_battery_code('42-001-3-01-1001')[0] == False
    print('5')
    assert valid_battery_code('60-011-3-01-100')[0]
