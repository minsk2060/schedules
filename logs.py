# The script makes a log of sent actions
from datetime import datetime, timedelta
from plants import plant

logs =[]

current_time = datetime.now()
#print(current_time)
#earlier_time =     (current_time).days -10



def logging(get_plant, par):
    current_time = datetime.now()
    # earlier_time = int(current_time).days - earlier_time).days
    plant_log = get_plant.replace(" ", "")
    f = open("./logging/log_scheduling.txt", "a")
    log = (current_time.strftime("%d-%m-%Y  %H:%M  "), plant[f"{plant_log}"], acting(plant_log, par))
    logs.append(log)
    # print(logs)
    #for i in logs:
     #   print(i[0][:10])

    f.write(f"{''.join(log)}\n")
    f.close()

def acting (plant_log, par):
    action = ""
    a = par[-1:]
    # If other plants
    if a == "1":   action = "  Пуск на низкой скорости"
    elif a == "2": action = "  Пуск на высокой скорости"
    elif a == "0": action = "  Cтоп"
    # If swimming pool
    if plant_log == "8388883&did=33560432":
        if a == "0":   action = "  Выключение подсветки"
        elif a == "2": action = "  Включение желтой подсветки"
        elif a == "1": action = "  Включение синей подсветки"
    # If dryers
    elif plant_log == "79691782&did=33556432" or plant_log == "79691777&did=33555432":
        if a == "5":   action = "  Стоп"
        elif a == "1": action = "  Пуск в режиме хоккей"
        elif a == "2": action = "  Пуск в режиме фигурное катание"
    return action
