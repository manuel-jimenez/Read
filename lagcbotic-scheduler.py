import schedule, time, datetime, os

var_months = {
    'january':'1',
    'february':'2',
    'march':'3',
    'april':'4',
    'may':'5',
    'june':'6',
    'july':'7',
    'august':'8',
    'september':'9',
    'october':'10',
    'november':'11',
    'december':'12'
}

def ProcessScheduleJob(metadata, current_date='', flagCtrl=False):
    if metadata:
        #Recuperando parametros de metadatos.
        #data = json.loads(metadata)
        #identifier = data['identifier']
        #Validando canal del mensaje.
        queueName = metadata[:metadata.find(";")]
        if queueName == 'DELETE':
            #schedule.clear(identifier)
            #app.logger.info(f"Tarea de calendarizado eliminada: {identifier}")
            pass
        else:
            message = ""
            current = metadata[metadata.find(";")+1:metadata.find(":")]
            periodicity = metadata[metadata.find(";") + 1:]
            identifier = os.urandom(10)
            
            current_year = current_date[0].split('-')[0]
            current_month = current_date[0].split('-')[1]
            current_day = current_date[0].split('-')[2]
            current_hour = current_date[1].split(':')[0]
            current_minute = current_date[1].split(':')[1]

            # Listas y funciones para le fecha.
            date = periodicity[periodicity.find(';')+1 : periodicity.find('/')].split(':')[1:3] # ['2020-12-01', '2021-04-05']
            # Lista de los Años.
            date_years = [str(i) for i in range(int(date[0].split('-')[0]), int(date[1].split('-')[0])+1)] \
                if len([str(i) for i in range(int(date[0].split('-')[0]), int(date[1].split('-')[0]))]) > 0 \
                else (date[0].split('-')[0] \
                    if date[0].split('-')[0] == date[1].split('-')[0] \
                    else None)

            # Lista de los Meses.
            if int(date[0].split('-')[0]) < int(date[1].split('-')[0]): # Esta condición indica si el proceso se hace en años diferentes.
                date_months = [str(i) for i in range(int(date[0].split('-')[1]), 13)]+[str(i) for i in range(1, int(date[1].split('-')[1])+1)] \
                    if len([str(i) for i in range(int(date[0].split('-')[1]), 13)]+[str(i) for i in range(1, int(date[1].split('-')[1])+1)]) > 0  and len(date_years) < 2 \
                    else (date[0].split('-')[1] \
                        if date[0].split('-')[1] == date[1].split('-')[1]
                        else [str(i) for i in range(1, 13)])
            else:
                date_months = [str(i) for i in range(int(date[0].split('-')[1]), int(date[1].split('-')[1]))] \
                    if len([str(i) for i in range(int(date[0].split('-')[1]), int(date[1].split('-')[1]))]) > 0 \
                    else (date[0].split('-')[1] \
                        if date[0].split('-')[1] == date[1].split('-')[1] \
                        else None)
                    
            # Lista de los días.
            if (int(date[0].split('-')[0]) < int(date[1].split('-')[0]) or int(date[0].split('-')[0]) == int(date[1].split('-')[0])) \
                and int(date[0].split('-')[1]) == int(date[1].split('-')[1]) \
                and int(date[0].split('-')[2]) > int(date[1].split('-')[2]): # Esta condición indica si el proceso se hace en años y meses diferentes.
                    date_days = [str(i) for i in range(int(date[0].split('-')[2]), 32)]+[str(i) for i in range(1, int(date[1].split('-')[2])+1)] \
                        if len([str(i) for i in range(int(date[0].split('-')[2]), 32)]+[str(i) for i in range(1, int(date[1].split('-')[2])+1)]) > 0 \
                        else (date[0].split('-')[2] \
                            if date[0].split('-')[2] == date[1].split('-')[2] \
                            else None)

            elif int(date[0].split('-')[0]) == int(date[1].split('-')[0]) \
                and int(date[0].split('-')[1]) == int(date[1].split('-')[1]) \
                and int(date[0].split('-')[2]) < int(date[1].split('-')[2]):
                    date_days = [str(i) for i in range(int(date[0].split('-')[2]), int(date[1].split('-')[2])+1)]
            else:
                date_days = [str(i) for i in range(1, 32)]

            # ----------------------------------------------------------------------------------------------------
            # Listas y funciones para el tiempo.
            data_time = periodicity[periodicity.find('/')+1:].split('/') # ['23:03', '00:05']
            # Lista de las Horas.
            time_hours = [str(i) for i in range(int(data_time[0].split(':')[0]), int(data_time[1].split(':')[0])+1)] \
                        if len([str(i) for i in range(int(data_time[0].split(':')[0]), int(data_time[1].split(':')[0]))]) > 0 \
                        else ([str(i) for i in range(int(data_time[0].split(':')[0]), 24)]+[str(i) for i in range(0, int(data_time[1].split(':')[0]))] \
                            if int(data_time[0].split(':')[0]) > int(data_time[1].split(':')[0]) \
                            else (data_time[0].split(':')[0] \
                                if data_time[0].split(':')[0] == data_time[1].split(':')[0] \
                                else None)) # ['13', '14', '15']

            after_minute = str(int(data_time[0].split(':')[1])-1) \
                if len(str(int(data_time[0].split(':')[1])-1)) > 1 and (int(data_time[0].split(':')[1])-1) > 0 \
                else ('0'+str(int(data_time[0].split(':')[1])-1)
                    if (int(data_time[0].split(':')[1])-1) >= 0
                    else str(60+(int(data_time[0].split(':')[1])-1))) # Minute
            after_hour = str()
            if (int(data_time[0].split(':')[1])-1) < 0:
                after_hour = str(int(data_time[0].split(':')[0])-1) \
                if len(str(int(data_time[0].split(':')[0])-1)) > 1 and (int(data_time[0].split(':')[1])-1) > 0 \
                else ('0'+str(int(data_time[0].split(':')[0])-1)
                    if (int(data_time[0].split(':')[0])-1) > 0
                    else str(24+(int(data_time[0].split(':')[0])-1))) # Hour
            else: after_hour = data_time[0].split(':')[0]

            current_after_minute = str(int(current_minute)-1) \
                if len(str(int(current_minute)-1)) > 1 and (int(current_minute)-1) > 0 \
                else ('0'+str(int(current_minute)-1)
                    if (int(current_minute)-1) >= 0
                    else str(60+(int(current_minute)-1))) # Current_Minute
            current_after_hour = str()
            if (int(current_minute)-1) < 0:
                current_after_hour = str(int(current_hour)-1) \
                if len(str(int(current_hour)-1)) > 1 and (int(current_minute)-1) > 0 \
                else ('0'+str(int(current_hour)-1)
                    if (int(current_hour)-1) >= 0
                    else str(24+(int(current_hour)-1))) # Current_Hour
            else: current_after_hour = current_hour

            if queueName == 'MINUTE':
                #print(current_hour+':'+current_minute, data_time[1])
                if str(int(current_year)) in date_years \
                    and str(int(current_month)) in date_months \
                    and str(int(current_day)) in date_days \
                    and str(int(current_hour)) in time_hours \
                    and current_hour+':'+current_minute == data_time[0]: # Mientras se encuentre dentro de la fecha de ejecución, la tarea se resgistra.
                        schedule.every(int(current)).minutes.at(':00').do(executeTask).tag(identifier)
                if current_hour+':'+current_minute == data_time[1]: # Cuando la hora actual coincida con la hora fin, la tarea se limpia.
                    schedule.clear(identifier)
            
            if queueName == 'HOUR':
                #print(current_after_hour+':'+current_after_minute, after_hour+':'+after_minute)
                if str(int(current_year)) in date_years \
                    and str(int(current_month)) in date_months \
                    and str(int(current_day)) in date_days \
                    and str(int(current_hour)) in time_hours \
                    and (current_after_hour+':'+current_after_minute == after_hour+':'+after_minute
                        or current_hour+':'+current_minute == data_time[0] \
                        or current_hour+':'+current_minute == after_hour+':'+after_minute): # Mientras se encuentre dentro de la fecha de ejecución, la tarea se resgistra.
                        schedule.every(int(current)).hours.at(':'+(str(int(data_time[0].split(':')[1])+1) if len(str(int(data_time[0].split(':')[1])+1)) > 1 and int(data_time[0].split(':')[1])+1 > 0 else '0'+str(int(data_time[0].split(':')[1])+1))).do(executeTask).tag(identifier) # Se ejecuta cada "current" hora en el minuto "data_time"
                if current_hour+':'+current_minute == data_time[1]: # Cuando la hora actual coincida con la hora fin, la tarea se limpia.
                    if int(current) > 1: time.sleep(int(current)*3600)
                    schedule.clear(identifier)
            
            if queueName == 'DAY':
                print(current_hour+':'+current_minute, data_time[0])
                if str(int(current_year)) in date_years \
                    and str(int(current_month)) in date_months \
                    and str(int(current_day)) in date_days \
                    and str(int(current_hour)) in time_hours \
                    and (current_after_hour+':'+current_after_minute == after_hour+':'+after_minute
                        or current_hour+':'+current_minute == data_time[0] \
                        or current_hour+':'+current_minute == after_hour+':'+after_minute): # Mientras se encuentre dentro de la fecha de ejecución, la tarea se resgistra.
                        schedule.every(int(current)).days.at(data_time[0].split(':')[0]+':'+(str(int(data_time[0].split(':')[1])+1) if len(str(int(data_time[0].split(':')[1])+1)) > 1 and int(data_time[0].split(':')[1])+1 > 0 else '0'+str(int(data_time[0].split(':')[1])+1))).do(job,tag=identifier, data=data).tag(identifier)
                if current_hour+':'+current_minute == data_time[1]: # Cuando la hora actual coincida con la hora fin, la tarea se limpia.
                    schedule.clear(identifier)

            if queueName == 'WEEK':
                print(current_hour+':'+current_minute, data_time[0])
                days = current.split(';')[0].lower()
                current = current.split(';')[1]
                if str(int(current_year)) in date_years \
                    and str(int(current_month)) in date_months \
                    and str(int(current_day)) in date_days \
                    and str(int(current_hour)) in time_hours \
                    and (current_after_hour+':'+current_after_minute == after_hour+':'+after_minute
                        or current_hour+':'+current_minute == data_time[0] \
                        or current_hour+':'+current_minute == after_hour+':'+after_minute): # Mientras se encuentre dentro de la fecha de ejecución, la tarea se resgistra.
                        if("monday" in days):
                            schedule.every(int(current)).weeks.day.monday.at(data_time[0]).do(job,tag=identifier, data=data).tag(identifier)
                        if("tuesday" in days):
                            schedule.every(int(current)).weeks.day.tuesday.at(data_time[0]).do(job,tag=identifier, data=data).tag(identifier)
                        if("wednesday" in days):
                            schedule.every(int(current)).weeks.day.wednesday.at(data_time[0]).do(job,tag=identifier, data=data).tag(identifier)
                        if("thursday" in days):
                            schedule.every(int(current)).weeks.day.thursday.at(data_time[0]).do(job,tag=identifier, data=data).tag(identifier)
                        if("friday" in days):
                            schedule.every(int(current)).weeks.day.friday.at(data_time[0]).do(job,tag=identifier, data=data).tag(identifier)
                        if("saturday" in days):
                            schedule.every(int(current)).weeks.day.saturday.at(data_time[0]).do(job,tag=identifier, data=data).tag(identifier)
                        if("sunday" in days):
                            schedule.every(int(current)).weeks.day.sunday.at(data_time[0]).do(job,tag=identifier, data=data).tag(identifier)

                if current_hour+':'+current_minute == data_time[1]: # Cuando la hora actual coincida con la hora fin, la tarea se limpia.
                    schedule.clear(identifier)

            if queueName == 'MONTHLY':
                print(current_hour+':'+current_minute, data_time[0])
                if str(int(current_year)) in date_years \
                    and str(int(current_month)) in date_months \
                    and str(int(current_day)) == current \
                    and str(int(current_hour)) in time_hours \
                    and (current_after_hour+':'+current_after_minute == after_hour+':'+after_minute
                        or current_hour+':'+current_minute == data_time[0] \
                        or current_hour+':'+current_minute == after_hour+':'+after_minute): # Mientras se encuentre dentro de la fecha de ejecución, la tarea se resgistra.
                        schedule.every().minute.at(':00').do(executeTask).tag(identifier)
                        message = f"Nueva tarea mensual calendarizada: {identifier} periodo: {current}"
                if current_hour+':'+current_minute == data_time[1]: # Cuando la hora actual coincida con la hora fin, la tarea se limpia.
                    schedule.clear(identifier)

            if queueName == 'YEARLY':
                print(current_hour+':'+current_minute, data_time[0])
                month = var_months[current.split(';')[0].lower()]
                current = current.split(';')[1]
                print(month, current)
                if str(int(current_year)) in date_years \
                    and str(int(current_month)) == month \
                    and str(int(current_day)) == current \
                    and str(int(current_hour)) in time_hours \
                    and (current_after_hour+':'+current_after_minute == after_hour+':'+after_minute
                        or current_hour+':'+current_minute == data_time[0] \
                        or current_hour+':'+current_minute == after_hour+':'+after_minute): # Mientras se encuentre dentro de la fecha de ejecución, la tarea se resgistra.
                        schedule.every().minute.at(':00').do(executeTask).tag(identifier)
                        message = f"Nueva tarea anual calendarizada: {identifier} periodo: {current}"
                if current_hour+':'+current_minute == data_time[1]: # Cuando la hora actual coincida con la hora fin, la tarea se limpia.
                    schedule.clear(identifier)

            '''if message != "":
                app.logger.info(message)
            else:
                app.logger.info(f"Nueva tarea calendarizada:{periodicity} {data}")'''

def executeTask():
    time = datetime.datetime.now().time()
    print(f'Ejecutando tarea a las {time}...')

def job(tag, data):
    if tag:
        print('Resgitrando tarea por minuto...')
        schedule.every(1).minutes.do(executeTask,data).tag(tag)

def processScheduleJob(metadata, flagCtrl=False):
    if metadata:
        #Recuperando parametros de metadatos.
        data = json.loads(metadata)
        identifier = data['identifier']
        #Validando canal del mensaje.
        if data['queueName'] == 'DELETE':
            schedule.clear(identifier)
            app.logger.info(f"Tarea de calendarizado eliminada: {identifier}")
        else:
            message = ""
            periodicity=data['periodicity'] # = '1:2020-12-03:2020-12-30/20:23/00:23' or 'April;1:2020-12-03:2020-12-30/20:23/00:23'
            # Ejemplo de dato a evaluar: x = 'April;20:2021-04-20:2022-04-20/10:00/00:00'
            #Validando tipo de ejecucion
            # Posible formula para separar los tiempos en una lista: time = x[x.find('/')+1:].split('/')
            # Posible formula para seprara las fechas en una lista, las posiciones son 1 y 2: date = x[x.find(';')+1 : x.find('/')].split(':')
            if data['queueName'] == 'MINUTE':
                schedule.every(int(periodicity)).minutes.do(executeTask,data).tag(identifier)
            elif data['queueName'] == 'HOUR':
                schedule.every().hour.at(f":{periodicity}").do(executeTask,data).tag(identifier)
            elif data['queueName'] == 'DAY':
                schedule.every().day.at(periodicity).do(executeTask,data).tag(identifier)
            elif data['queueName'] == 'WEEK':
                splitPeriod = periodicity.lower().split(";")
                days = splitPeriod[0]
                periodicity = splitPeriod[1]
                if("monday" in days):
                    schedule.every().day.monday.at(periodicity).do(executeTask,data).tag(identifier)
                if("tuesday" in days):
                    schedule.every().day.tuesday.at(periodicity).do(executeTask,data).tag(identifier)
                if("wednesday" in days):
                    schedule.every().day.wednesday.at(periodicity).do(executeTask,data).tag(identifier)
                if("thursday" in days):
                    schedule.every().day.thursday.at(periodicity).do(executeTask,data).tag(identifier)
                if("friday" in days):
                    schedule.every().day.friday.at(periodicity).do(executeTask,data).tag(identifier)
                if("saturday" in days):
                    schedule.every().day.saturday.at(periodicity).do(executeTask,data).tag(identifier)
                if("sunday" in days):
                    schedule.every().day.sunday.at(periodicity).do(executeTask,data).tag(identifier)
            elif data['queueName'] == 'MONTHLY':
                splitPeriod = periodicity.lower().split(";")
                day = splitPeriod[0]
                hour = splitPeriod[1]
                currentDate = datetime.now()
                inputDate = datetime.strptime(day + "T" + hour, "%dT%H:%M") 

                if int(day) == currentDate.day and flagCtrl == False:
                    if(datetime.strptime(currentDate.strftime("%dT%H:%M"),"%dT%H:%M") < inputDate):
                        schedule.every().day.at(hour).do(executeTask,data).tag(identifier)
                        message = f"Nueva tarea mensual calendarizada: {identifier} periodo: {hour}"
                    else:
                        message = "La tarea mensual será programada en otro momento."
                elif int(day) == currentDate.day + 1 and flagCtrl == True:
                    schedule.every().day.at(hour).do(executeTask,data).tag(identifier)
                    message = f"Nueva tarea mensual calendarizada: {identifier} periodo: {hour}"
                else:
                    message = "La tarea mensual será programada en otro momento."
            elif data['queueName'] == 'YEARLY':
                splitPeriod = periodicity.lower().split(";")
                day = splitPeriod[0]
                month = splitPeriod[1]
                hour = splitPeriod[2]
                currentDate = datetime.now()
                currentDateFormat = datetime.strptime(currentDate.strftime("%d/%mT%H:%M"),"%d/%mT%H:%M")
                inputDate = datetime.strptime(day + "/" + month + "T" + hour, "%d/%mT%H:%M") 
                if(int(month) == currentDate.month):
                    if int(day) == currentDate.day and flagCtrl == False:
                        if(currentDateFormat < inputDate):
                            schedule.every().day.at(hour).do(executeTask,data).tag(identifier)
                            message = f"Nueva tarea anual calendarizada: {identifier} periodo: {hour}"
                        else:
                            message = "La tarea anual será programada en otro momento."
                    elif int(day) == currentDate.day + 1 and flagCtrl == True:
                        schedule.every().day.at(hour).do(executeTask,data).tag(identifier)
                        message = f"Nueva tarea anual calendarizada: {identifier} periodo: {hour}"
                    else:
                        message = "La tarea anual será programada en otro momento."
                else:
                    message = "La tarea anual será programada en otro momento."
            if message != "":
                app.logger.info(message)
            else:
                app.logger.info(f"Nueva tarea calendarizada:{periodicity} {data}")

    else:
        app.logger.error("La tarea no puede ser programada.", exc_info=sys.exc_info())