
"""
Приветственное сообщение
"""
def welcome():
    while True:
        print('<command> exit - выйти из программы')
        print('<command> help - справочная информация')
        command = input('Введите команду: ')

        if command == 'exit':
            break

        elif command == 'help':
            continue
        
        else:
            print(f"Неизвестная команда: {command}")