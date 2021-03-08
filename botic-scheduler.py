import sys
import schedule
from datetime import date, datetime
import time
import json
from app import create_app, db
from models import BotJob, BotScheduledJob, Bot, TaskVersion, Task, Status, ScheduledJobStatus, BotJobType

app = create_app()
app.app_context().push()
current_date = str(datetime.datetime.now()).split()

def checkChannelsForNews():
    try:
        message = p.get_message()
        if message and type(message['data']) != int:
            return message['data']
    except:
        app.logger.error("Error retrieving messages", exc_info=sys.exc_info())
    return

def scheduleYearMonth():
    qMonth = app.redis.hgetall("MONTHLY")
    qYear = app.redis.hgetall("YEARLY")

    if qMonth:
        for queue in qMonth:
            processScheduleJob(qMonth[queue],True, current_date=str(datetime.datetime.now()).split())
    if qYear:
        for queue in qYear:
            processScheduleJob(qYear[queue],True, current_date=str(datetime.datetime.now()).split())
    return

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

# Función a analizar y donde se va a trabajar.
def processScheduleJob(metadata, current_date='', flagCtrl=False):
    print('Ejecutando processScheduleJob...')
    if metadata:
        print('Metadata identificado...')
        # Fecha Actual
        current_year = current_date[0].split('-')[0]
        current_month = current_date[0].split('-')[1]
        current_day = current_date[0].split('-')[2]
        # Hora Actual
        current_hour = current_date[1].split(':')[0]
        current_minute = current_date[1].split(':')[1]
        #Recuperando parametros de metadatos.
        data = json.loads(metadata)
        identifier = data['identifier']
        #Validando canal del mensaje.
        queueName = data['queueName']
        if queueName == 'DELETE':
            schedule.clear(identifier)
            app.logger.info(f"Tarea de calendarizado eliminada: {identifier}")
        if queueName == 'UNIQUE':
            when = data['periodicity'].split('/')
            date_execute = when[0].split('-')
            time_execute = when[1].split(':')
            if current_year in date_execute \
                and current_month in date_execute \
                and current_day in date_execute \
                and ((current_hour in time_execute 
                and current_minute in time_execute) or current_hour+':'+current_minute == when[1]) :
                    schedule.every().second.do(executeTask,data).tag(identifier)
                    schedule.clear(identifier)
        else:
            message = ""
            when = data['periodicity']
            current = when[when.find(";")+1:when.find(":")]
            periodicity = when[when.find(";") + 1:]

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
                print(current_hour+':'+current_minute, data_time[1])
                if str(int(current_year)) in date_years \
                    and str(int(current_month)) in date_months \
                    and str(int(current_day)) in date_days \
                    and str(int(current_hour)) in time_hours \
                    and current_hour+':'+current_minute == data_time[0]: # Mientras se encuentre dentro de la fecha de ejecución, la tarea se resgistra.
                        print('Registrando tarea...')
                        schedule.every(int(current)).minutes.at(':00').do(executeTask,data).tag(identifier)
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
                        print('Registrando tarea...')
                        schedule.every(int(current)).hours.at(':'+(str(int(data_time[0].split(':')[1])+1) if len(str(int(data_time[0].split(':')[1])+1)) > 1 and int(data_time[0].split(':')[1])+1 > 0 else '0'+str(int(data_time[0].split(':')[1])+1))).do(executeTask,data).tag(identifier) # Se ejecuta cada "current" hora en el minuto "data_time"
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
                        print('Registrando tarea...')
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
                        print('Registrando tarea...')
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
                        print('Registrando tarea...')
                        schedule.every().minute.at(':00').do(executeTask,data).tag(identifier)
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
                        print('Registrando tarea...')
                        schedule.every().minute.at(':00').do(executeTask,data).tag(identifier)
                        message = f"Nueva tarea anual calendarizada: {identifier} periodo: {current}"
                if current_hour+':'+current_minute == data_time[1]: # Cuando la hora actual coincida con la hora fin, la tarea se limpia.
                    schedule.clear(identifier)

            if message != "":
                app.logger.info(message)
            else:
                app.logger.info(f"Nueva tarea calendarizada:{periodicity} {data}")

def job(tag, data):
    if data:
        print('Resgitrando tarea por minuto...')
        schedule.every(1).minutes.do(executeTask,data).tag(tag)

def executeTask(data):
    task =data
    if(task['queueName'] == 'MONTHLY'):
        identifier = task['identifier']
        app.logger.info(f"Ejecutando tarea mensual: {data}")
        app.logger.info("Tarea ejecutada.")
        app.logger.info("Limpiando tarea de registro diario")
        schedule.clear(identifier)
        app.logger.info(f"Tarea de calendarizado eliminada: {identifier} con éxito.")
    elif(task['queueName'] == 'YEARLY'):
        identifier = task['identifier']
        app.logger.info(f"Ejecutando tarea anual: {data}")
        app.logger.info("Tarea ejecutada.")
        app.logger.info("Limpiando tarea de registro diario")
        schedule.clear(identifier)
        app.logger.info(f"Tarea de calendarizado eliminada: {identifier} con éxito.")
    else:
        app.logger.info(f"Ejecutando tarea: {data}")

    task_metadata = json.loads(task['metadata'])
    scheduled = BotScheduledJob.query.get(task_metadata['id'])
    try:
        play_task(task_id=scheduled.task_id,
                    bot_id=scheduled.bot_id, 
                    parameters=scheduled.parameters)
        scheduled.status = ScheduledJobStatus.PROCESSING
        db.session.commit()
    except:
        db.session.rollback()
        app.logger.error("Error in get_task_last_rev", exc_info=sys.exc_info())

def getQueuesFromServer():
    qMinute = app.redis.hgetall("MINUTE")
    qHour = app.redis.hgetall("HOUR")
    qDay = app.redis.hgetall("DAY")
    qWeek = app.redis.hgetall("WEEK")
    qMonth = app.redis.hgetall("MONTHLY")
    qYear = app.redis.hgetall("YEARLY")

    if qMinute:
        for queue in qMinute:
            processScheduleJob(qMinute[queue], current_date=str(datetime.datetime.now()).split())
    if qHour:
        for queue in qHour:
            processScheduleJob(qHour[queue], current_date=str(datetime.datetime.now()).split())
    if qDay:
        for queue in qDay:
            processScheduleJob(qDay[queue], current_date=str(datetime.datetime.now()).split())
    if qWeek:
        for queue in qWeek:
            processScheduleJob(qWeek[queue], current_date=str(datetime.datetime.now()).split())
    if qMonth:
        for queue in qMonth:
            processScheduleJob(qMonth[queue], current_date=str(datetime.datetime.now()).split())
    if qYear:
        for queue in qYear:
            processScheduleJob(qYear[queue], current_date=str(datetime.datetime.now()).split())
    return

def get_task_last_rev(task_id):
    """gets the task last revision that match with `task_id`.

    Parameters
    ----------
    task_id: int
        the task id
    
    Returns
    -------
    int
        the task last revision
    """
    
    taskVersion = db.session.query(
        TaskVersion.task_id, db.func.max(TaskVersion.id).label('last_version_id')
    ).group_by(TaskVersion.task_id).filter(TaskVersion.task_id == task_id)
    row = taskVersion.first()
    if row != None:
        value = row.last_version_id
        return value

def play_task(task_id, bot_id, parameters):
    """Plays the task with `bot_job_sm.id` in the specified `bot_job_sm.botSecretLists`.

    Parameters
    task_id: int
        the task id to schedule
    bot_id: int
        the bot id that is going to perform the task
    parameters: str
        the additional parameters to execute the task

    Returns
    -------
    """

    task_version_id = get_task_last_rev(task_id)
    botJob = BotJob(bot_id = bot_id, \
                    task_version_id = task_version_id, \
                    parameters = parameters, \
                    status = Status.NOT_PROCESSED, \
                    job_type = BotJobType.SCHEDULED)
    db.session.add(botJob)

if __name__ == "__main__":
    try:
        p = app.redis.pubsub()
        app.logger.info("Recuperación y calendarizado de colas existentes")
        getQueuesFromServer()
        app.logger.info("Subscrito a colas MINUTE, HOUR, DAY, WEEK, MONTHLY y DELETE.")
        p.subscribe('MINUTE','HOUR','DAY','WEEK','MONTHLY','YEARLY',"DELETE")
        while True:
            #Revisando tareas por ejecutar
            schedule.run_pending()
            #Creando subscripcion mensual y anual
            schedule.every().day.at("23:59").do(scheduleYearMonth)
            current_date = str(datetime.datetime.now()).split()
            print(current_date)
            #Revisando si existe nuevas colas en bus de datos.
            metadata = checkChannelsForNews()
            if metadata:
                processScheduleJob(metadata, current_date=current_date)
            time.sleep(1)
    except:
        app.logger.error('Unhandled exception',exc_info=sys.exc_info())