# Read
Bot/readme

# 🤖Botic
##¿Qué es Botic?
```
  Botic es una aplicación donde podemos hacer la calendarización de un Bot para realizar 
  procesos automatizados. Estos bots están programados en Automagica y para usar 
  este aplicativo se necesitan tener ciertos prerequisitos instalados.
```
### Prerequisitos
```
  Para tener la aplicación de Botic instalada de manera local y corriendo de manera 
  adecuada en nuestro ordenador, primero necesitamos tener instalados ciertos prerequisitos:
```
#### - Tener instalado Python en su versión 3.7.4
  - Instalación en Windows:
  
    - Para realizar la instalación en su ordenador con Windows, nos dirigimos a la [página oficial de Python](https://www.python.org/downloads/release/python-374/) 
      donde descargaremos el archivo de Python 3.7.4 correspondiente a las especificaciones para su ordenador.
    
    ![imagen windows1](https://miro.medium.com/max/2732/1*b5SZWxlBXkkhmAXjZgUWWg.png)
    
    
    - Una vez descargado este archivo, nos dirigimos a la carpeta donde se ha guardado el archivo,
      y ejecutamos el instalador.
    
    - Nos aparecerá una pantalla como la siguiente: 
    ![imagen windows2](https://www.ics.uci.edu/~pattis/common/handouts/pythoneclipsejava/images/python/pythonsetup.jpg)

    - Marcamos la casilla que dice "Add Python 3.7 to PATH", esto agregará la ruta de instalación de Python
      a sus variables de entorno. Hacemos click en "Install now" y empezará a instalar el paquete.
      
    - Te aparecerá una pantalla con una barra de progreso como la siguiente:
    
    ![imagen windows3](https://i.ytimg.com/vi/Wx8XU2L2k6Q/maxresdefault.jpg)
    
    - Una vez acabando la instalación presionamos en el botón de "Close", y listo! Ya tendremos Python en su
      versión 3.7.4 instalado en nuestro ordenador.
      
    - Para verificarlo, abra su CMD y escriba el siguiente comando:
    
    ```cmd
        >python -V
    ```
    - Resultado:
    ```cmd
        Python 3.7.4
    ```
    
  - Instalación en Linux
  
    - Antes de realizar la instalación en su ordenador, debemos instalar algunos paquetes necesarios para ejecutar
      Python desde la fuente. Sólo copie los siguientes comandos:
      
    ```bash
        $ sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
        $ sudo apt update
    ```
      
    - Después de haber instalado estos paquetes, ahora debemos descargar el código fuente de
      la versión 3.7.4 de la [página oficial de Python](https://www.python.org/downloads/release/python-374/) con el comando wget:
      
    ```bash
        $ wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tar.xz
    ```
    
    - Al terminar descargaremos un archivo comprimido "Python-3.7.4.tar.xz". Descomprimimos este archivo con el siguiente comando:
    ```bash
        $ tar -xf Python-3.7.4.tar.xz
    ```
    
    - Nos aparecerá la carpeta del archivo comprimido llamada "Python-3.7.4", entramos a ella, ejecutamos el siguiente comando para
      configurar todo lo necesario, y listo! Ya tenemos Python3.7.4 disponible en su ordenador Linux, sólo falta realizar
      el proceso de construcci贸n en el sistema y guardar los cambios para poder utilizarlo de manera global.
    ```bash
        $ cd Python-3.7.4
        $ ./configure --enable-optimizations
    ```
    
    - A continuación, inicie el proceso de construcción usando el comando make -j 1. Reemplace el # 1 con la cantidad de núcleos de CPU en su sistema para un tiempo de construcción más rápido. Para saber cuántos nucleos tiene su CPU consulte el comando "nproc".
    ```bash
        $ make -j 1
    ```
    
    - Ahora ejecute el siguiente comando para que haga todos los cambios de la instalaci贸n sin sobreescribir otras versiones de Python que tenga instalado.
    ```bash
        $ make altinstall
    ```
    
    - Ya tendrá python3.7 disponible desde cualquier directorio. Para verificarlo escriba el siguiente comando:
    ```bash
        $ python3.7 --version
    ```
    - Resultado:
    ```bash
        $ Python 3.7.4
    ```

#### - Tener una cuenta en GitHub y tener Git instalado en nuestro ordenador.
  - Registro en GitHub
    - Para registrarnos vamos [a la página de GitHub](https://github.com) donde sólo llenamos el formulario de 
      registro.
      ![github_registro](https://cdn.kastatic.org/ka-perseus-images/b96521d07ec01801331b4eec8d399c84f2131050.png)
     
    - Confirmamos nuestro correo, y listo! ya tendremos nuestro usuario de GitHub.
    
    
  - Instalación Git en Windows
    - Para instalar Git en nuestro ordenador con  windows,  ingresar a la liga  https://gitforwindows.org y hacer clic en download,  seguir el proceso de instalación. (en la           instalación dar a todo siguiente como viene por defecto en la instalación)
 
 
 ![instal en windows](https://scontent.fmex16-1.fna.fbcdn.net/v/t1.15752-9/124402478_3738900932841178_1399512574307556546_n.png?_nc_cat=102&ccb=2&_nc_sid=ae9488&_nc_eui2=AeFgO1bzrQls15z-v7G-C9e66i94bWmP96nqL3htaY_3qeWpPnorUmoOEkHT8tPBy9w1OjwqdkpRyk-qNrARi_29&_nc_ohc=u2mXMp1gmZkAX_peAqu&_nc_ht=scontent.fmex16-1.fna&oh=078e3a2b0f5fd519d49a5c0aff21f253&oe=5FD15A5B)
  
  
  -para verificar que la instalación fue correcta escribir el comando: 
    ```
        git
    ```
    en la consola y deberá devolver  información como en la siguiente imagen 
    
![imagen para verificar1](https://scontent.fmex16-1.fna.fbcdn.net/v/t1.15752-9/124449034_1092222884560251_6182625493900793297_n.png?_nc_cat=104&ccb=2&_nc_sid=ae9488&_nc_eui2=AeGuPvuQck4hDIw6PRn6MwN-yaUaopVEXIPJpRqilURcg6UStbfH5AWPwSd2KRaiSPzm2Q1xCKScKb8Tq5llJY8g&_nc_ohc=T7-nz4h_0X8AX_Ehesn&_nc_ht=scontent.fmex16-1.fna&oh=3639265c974c90eb2aef187c271f1dce&oe=5FD44A3B)
 
 
  - Instalación Git en Linux
    - Para realizar la instalación en nuestro ordenador con Linux, haremos uso de nuestra línea de comandos. 
      Escribimos el siguiente comando para instalar git:
      ```bash
        $ sudo apt-get install git
      ```
    - Y listo! Ya tendremos git instalado en nuestro ordenador, para verificarlo escriba el comando $ git --version.
      Sólo hace falta realizar la configuración inicial.
    
    - Para esta configuración haremos uso del Nombre de Usuario y Correo de nuestra cuenta de GitHub.
      Escriba los siguientes comandos reemplazando los datos de "name" & "email" por sus datos correspondientes.
      ```bash
        $ git config --global user.name "tu_nombre_de_usuario"
        $ git config --global user.email "tu_correo@example.com"
      ```
    - Con esto ya tendremos git configurado y listo para usarlo posteriormente. Para ver los datos de su cuenta de git 
      puede usar el siguiente comando:
      ```bash
        $ git config --global -l
      ```
    - Resultado
      ```bash
        user.name=tu_nombre_de_usuario
        user.email=tu_correo@example.com
      ```
#### - Tener una cuenta en GitLab-git2-condor.
  - Para este paso debemos tener [acceso](https://git2-condor.ddns.net/users/sign_in) departe del equipo de Condor, de no ser así ponserse en contacto con Condor Consulting.


###### Si ha llegado hasta este punto, ya está listo para instalar Botic en su ordenador, sigas las siguientes instrucciones.


### Instalación de Botic de manera local.
  - Descarga del repositorio botic-app
  
    - Para descargar este repositorio haremos uso de los comandos de git, en caso de Windows usa la línea de comandos de git.
      Descargaremos este repositorio de la rama autov3:
    ```bash
        $ git clone -b autov3 https://git2-condor.ddns.net/botic/botic-app.git
    ```
   
 ### Crear el entorno virtual en la carpeta de botic-app
  - Crear entorno virtual con windows
  
    - Ingresar desde el cmd a la carpeta que se generó en el paso anterior (botic-app)
    - Crear el entorno virtual con el siguiente comando
   ```
      python -m venv nombre_del_entorno
   ```
   
   - Entrar entrar en la carpta con el nombre del entorno que se generó y posteriormente en el siguiente directorio y activar el entorno:
    
   ```
      Scipts/activate
   ```
   - Deberá aparecer el nombre del entorno al principio del prompt


 ![entrono activado](https://scontent.fmex16-1.fna.fbcdn.net/v/t1.15752-9/125028784_843487856447848_2078547274048912438_n.png?_nc_cat=100&ccb=2&_nc_sid=ae9488&_nc_eui2=AeGmFeUdwYXTBbkBS2L1LaMCCGHs3IS8yIEIYezchLzIgdng31k4JafZ3fNxE4Z88zKpVdIWAYY4kcvKljC4lpGW&_nc_ohc=vccVndJlRnEAX9uqKrS&_nc_ht=scontent.fmex16-1.fna&oh=2c1f454f73216262669df63762ccc02a&oe=5FD1EA93)
 
 - Cear entorno virtual en linux
   - bla bla bla xd
   
 ### Descargar los requerimientos para Botic
 - Descarga en windows
   - Ubicarte en la carpeta de botic-app desde el cmd con el entorno virtual activado, y ejecutar el siguiente comando: 
   ```
      python -m pip install -r app/requirements.txt
   ```  
  
  - Se abrirá una ventana en la cual se debe ingresar tu usuario y contraseaña de git
  
  ![usuario de git](https://scontent.fmex16-1.fna.fbcdn.net/v/t1.15752-9/124574830_437639197618591_5419471592337621046_n.png?_nc_cat=108&ccb=2&_nc_sid=ae9488&_nc_eui2=AeF5BEUYY5adl-YMqzdQ42NQXgNUQTfrRVpeA1RBN-tFWmen2q7VqMO9GDvt1kU4gB2FFJxICIcrYsg942IABMt-&_nc_ohc=6Ofj67u41vYAX_tJr1I&_nc_ht=scontent.fmex16-1.fna&oh=675604a4402893f963582b9ede0eeb96&oe=5FD3DD79)
   - Posteriormente empesará la descarga e instalación
  
  
  
  ![instalacion de rquerimentos](https://scontent.fmex16-1.fna.fbcdn.net/v/t1.15752-9/125191375_424375621906810_1730549728267896119_n.png?_nc_cat=106&ccb=2&_nc_sid=ae9488&_nc_eui2=AeE8t6Nk7dUmHI7JHH7ORCs9ujOtcZ1goXW6M61xnWChdWwPxDasEEdr7OrxVFcTss2C5YUjwtLp1utu6JpRTQ5B&_nc_ohc=uM2syFuvx2MAX-61xgh&_nc_ht=scontent.fmex16-1.fna&oh=1371ce50e37742d95615a8b3d31afd07&oe=5FD204DD) 
  
  
  - Al terminar la instalación para asegurarnos de que la base de datos este actualizada ejecutaremos el siguiente comando:
  ```
      flask db upgrade
   ```  
  
  ![verificar actualización](https://scontent.fmex16-1.fna.fbcdn.net/v/t1.15752-9/125152736_468076537497753_3485632196933569344_n.png?_nc_cat=102&ccb=2&_nc_sid=ae9488&_nc_eui2=AeHnJcEbIxQ-jX5mCsVpknvisfNtghhon5qx822CGGifmu7y3vWolnEDHN4rKTIMD55hjoSzlDZjcWBzOX2jCdJi&_nc_ohc=1PqbAPAhAMsAX9zJl7H&_nc_ht=scontent.fmex16-1.fna&oh=48b86c701026cd3c6d01c5cbee10dbb0&oe=5FD219A5)
  
  - Por ultimo, levantar el servidor ejecutando:
  ```
     flask run
   ```
  ![levantar sevidor win](https://scontent.fmex16-1.fna.fbcdn.net/v/t1.15752-9/124412478_853961815349316_5194944618905622950_n.png?_nc_cat=101&ccb=2&_nc_sid=ae9488&_nc_eui2=AeH-a_TL-WfGExvcl_1yQRd2o7So9ZBDT7ujtKj1kENPu8I8Q6DCfrCE13tOf7nUdEoIZC_98QwrIKUocsfEX9qr&_nc_ohc=bq0aeh1pWkwAX_NZice&_nc_ht=scontent.fmex16-1.fna&oh=5d1be14cce133980d9afc74989ad2526&oe=5FD32D3C)


d
    
    
  
