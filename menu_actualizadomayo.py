# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 22:05:48 2023

@author: horus garcia villanueva
"""
#Para editar el archivo comentar lo que tenga que ver con el sensor ultrasonico ya que sin el el programa no compilara

#importamos todas las librerias que se usaran
from imagenes import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLCDNumber
from PyQt5.QtCore import Qt, QTime, QTimer
from datetime import datetime
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
import time
from time import sleep
import qrcode
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

GPIO.setwarnings(False)


#definimos entradas y salidas raspberry
#entradas:
s1 = 19 #presencia y obstrucciones (presencia 2)
s2 = 21 #PET proveniente de arduino (presencia1)

s4 = 23 #humedad y temperatura proveniente de arduino
s5 = 24 #sensor de peso proveniente de arduino


#usando sensor de nivel
#set GPIO Pins
GPIO_TRIGGER = 16
GPIO_ECHO = 18 #peligroso, conectar con resistencias

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


#salidas
in3 = 38
in4 = 40
enb = 36

#definimos los pines como entradas o salidas
GPIO.setup(s1,GPIO.IN)
GPIO.setup(s2,GPIO.IN)

GPIO.setup(s4,GPIO.IN)
GPIO.setup(s5,GPIO.IN)

GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)
GPIO.setup(enb,GPIO.OUT)

#declaramos condiciones iniciales
GPIO.output(in3,GPIO.LOW)
GPIO.output(in4,GPIO.LOW)
p=GPIO.PWM(enb,100)

p.start(25)




#Clase fondo
class fondo(QMainWindow):
    def __init__(self, parent=None):
        super(fondo, self).__init__(parent)
        loadUi('procesando.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.label.setText("Cargando...")
        self.procesandopet.setValue(99)

#clase salir
class salir(QMainWindow):
    def __init__(self, parent=None):
        super(salir, self).__init__(parent)
        loadUi('salir.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.uno.clicked.connect(lambda: self.digito("1"))
        self.dos.clicked.connect(lambda: self.digito("2"))
        self.tres.clicked.connect(lambda: self.digito("3"))
        self.cuatro.clicked.connect(lambda: self.digito("4"))
        self.cinco.clicked.connect(lambda: self.digito("5"))
        self.seis.clicked.connect(lambda: self.digito("6"))
        self.siete.clicked.connect(lambda: self.digito("7"))
        self.ocho.clicked.connect(lambda: self.digito("8"))
        self.nueve.clicked.connect(lambda: self.digito("9"))
        self.cero.clicked.connect(lambda: self.digito("0"))
        self.borrar.clicked.connect(lambda: self.digito("borrar"))
        self.regresar.clicked.connect(self.volver)
        self.finalizar.clicked.connect(self.cerrarp)
        
    #funcion para presionar digitos
    def digito(self,pressed):
      if pressed == "borrar":
        self.password.setText("")
      else:
        self.password.setText(f'{self.password.text()}{pressed}')
    
    #funcion volver
    def volver(self):
      self.hide()
      otraventana=info(self)
      otraventana.show()

    #funcion para salir de la hmi
    def cerrarp(self):
      if self.password.text() == "2018":
        sys.exit()
      else:
        self.respuesta.setText("Contraseña\nincorrecta")



#Clase advertencia
class advertencia(QMainWindow):
    def __init__(self, parent=None):
        super(advertencia, self).__init__(parent)
        loadUi('advertencia1.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        #self.ajustes.clicked.connect(self.f_info)
        
        #inicializacion de timer para ejecutar una funcion por tiempo indefinido
        self.timer=QTimer()
        self.timer.timeout.connect(self.back)
        self.timer.start(1000)

    #funcion que se encarga de decidir entre obstruccion o temperatura/humedad
    def back(self):
        if (GPIO.input(s2))== 1:
          self.notificacion.setText("Obstrucción en la banda detectada\n para poder continuar retire \nel residuo cuidadosamente, si\n los problemas persisten\n acuda con alumnos consejeros.")
        if GPIO.input(s4) == 1:
          self.notificacion.setText("Exceso de Temperatura y/o Humedad \ndetectadas, espere hasta que las \ncondiciones ambientales mejoren,\nsi el problema persiste acuda\n con los alumnos\n consejeros. ")

        if((GPIO.input(s2)) == (GPIO.input(s4)) == 0):
          self.hide()
          otraventana=principal(self)
          otraventana.show()
          self.timer.timeout.disconnect(self.back)
        
        
############################################CLASE PRINCIPAL ##############################
class principal(QMainWindow):
    #inicializamos los contadores
    contadorusuario=0
    contadordia=0
    contadormes=0
    contadorhora=0

    horaactual=datetime.now().time().hour
    diaactual=datetime.now().day
    mesactual=datetime.now().month
    
    def __init__(self,parent=None):
        #variable para ejecutar siempre revision de temperatura
        principal.a=0
        super(principal, self).__init__(parent)
        loadUi('menuv1.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.iniciar.clicked.connect(self.begin)
        self.ajustes.clicked.connect(self.f_info)
        self.estadisticas.clicked.connect(self.f_estadisticas)
       
        #instruccion que reinicia el contador de usuario
        principal.contadorusuario=0
        
        #instruccion que reinicia el nivel lleno de almacenamiento para ventana agregar pet
            
        self.timer=QTimer()
        self.timer.timeout.connect(self.lcd_number)
        self.timer.start(1000)
      
        #instruccion que manda a traer al la funcion de medir
        self.timer.timeout.connect(self.medir)
        
        #instrucciom que manda a traer al sensor de obstaculos, temperatura y humedad
        self.timer.timeout.connect(self.condiciones)
        
        
    #funcion que evalua las condiciones iniciales 
    def condiciones(self):
       #deteccion de obstrucciones y/o temperatura y humedad
        if((GPIO.input(s2)) or (GPIO.input(s4)) == 1):
            self.hide()
            otraventana=advertencia(self)
            otraventana.show()
            self.timer.timeout.disconnect(self.condiciones)    
          
    
    #funcion encargada de medir el almacenamiento
    def medir(self):
     
        # Sensor para detectar nivel de almacenamiento
        #Se manda a traer la funcion
        principal.dist = principal.distance(self) #x
        #interpolacion lineal
        principal.distancia_vacio=75 #x1  100%=y1
        principal.distancia_lleno=10 #x2 0%=y2
        
        #interpolacionlineal= y=y1+((y2-y1)/(x2-x1))*(x-x1)
        nivel=(100+((0-100)/(10-75))*(principal.dist-75))
         
         
        #declaramos valores de llenado y vacio
        if(principal.dist)>principal.distancia_vacio :
            #"Nivel de llenado = 0%"
            self.iniciar.show()
            self.notificacion.setText(" ")
            self.nivelalmacenamiento.setValue(0)
            
        elif(principal.dist)<principal.distancia_lleno :
            #"Nivel de llenado = 100%"
            self.notificacion.setText("¡ALMACENAMIENTO LLENO!\n Revisa en información como\n vaciar el almacenamiento")
              
            self.nivelalmacenamiento.setValue(100)
            self.iniciar.hide()
        
        else:
            #nivel actual
            niveldisponible=100-nivel
            self.iniciar.show()
            self.nivelalmacenamiento.setValue(int(niveldisponible))
            if(niveldisponible)>70:
              self.notificacion.setText("Nivel casi lleno")
            else:
              self.notificacion.setText(" ")
          

    def distance(self):
        # set Trigger to HIGH
       GPIO.output(GPIO_TRIGGER, True)

       # set Trigger after 0.01ms to LOW
       time.sleep(0.00001)
       GPIO.output(GPIO_TRIGGER, False)

       StartTime = time.time()
       StopTime = time.time()

       # save StartTime
       while GPIO.input(GPIO_ECHO) == 0:
            StartTime = time.time()

       # save time of arrival
       while GPIO.input(GPIO_ECHO) == 1:
            StopTime = time.time()

            # time difference between start and arrival
            TimeElapsed = StopTime - StartTime
            # multiply with the sonic speed (34300 cm/s)
            # and divide by 2, because there and back
            distance = (TimeElapsed * 34300) / 2

       return distance
        
    
    #funcion que suma contadores        
    def contadoru(self):
        principal.contadorusuario= principal.contadorusuario + 1
        principal.contadordia= principal.contadordia + 1
        principal.contadorhora= principal.contadorhora + 1
        principal.contadormes= principal.contadormes + 1
          
    #FUNCION para iniciar reciclaje
    def begin(self):
        self.hide()
        otraventana=ingresopet(self)
        otraventana.show()
        self.timer.timeout.disconnect(self.condiciones)   

    #funcion para acceder a informacion
    def f_info(self): 
        self.hide()
        otraventana=info(self)
        otraventana.show()
        self.timer.timeout.disconnect(self.condiciones)   
		
    #funcion para acceder a estadisticas
    def f_estadisticas(self):
        self.hide()
        otraventana=estadisticas(self)
        otraventana.show()
        self.timer.timeout.disconnect(self.condiciones)
        
    #funcion encargada de evaluar la hora    
    def lcd_number(self):
        hora_actual=datetime.now().time()
        fecha_actual=datetime.now() #quitar time() si quiero fecha 
        
        #modificar extrayendo las horas con hour =0 para que se haga el reinicio cada dia
        horanuevo=hora_actual.hour
        dianuevo=fecha_actual.day
        mesnuevo=fecha_actual.month
        #if que hace que se reinicien las botellas por cambio de dia
      
        #condicion si cambia de dia se reinicia contador dia
        if dianuevo == principal.diaactual:
              pass
        else:
              principal.contadordia=0
              principal.diaactual=fecha_actual.day
        
        #condicion si cambia de hora se reinicia contador hora
        if horanuevo == principal.horaactual:
              pass
        else:
              principal.contadorhora=0
              principal.horaactual=hora_actual.hour
        
        #condicion si cambia de mes se reinicia contador mes
        if mesnuevo == principal.mesactual:
              pass
        else:
              principal.contadormes=0
              principal.mesactual=fecha_actual.month
        
        time=datetime.now()
        
        #se muestra la fecha
        fechas=time.strftime("%d-%m-%Y")
        self.fecha.setSegmentStyle(QLCDNumber.Flat)
        self.fecha.setDigitCount(10)
        self.fecha.display(fechas)
        
        #se muestra la hora
        hora=time.strftime("%H:%M:%S")
        self.Hora.setSegmentStyle(QLCDNumber.Flat)
        self.Hora.setDigitCount(10)
        self.Hora.display(hora)


###################FIN DE CLASE PRINCIPAL#####################################


#clase estadisticas
class estadisticas(QMainWindow):
    def __init__(self, parent=None):
        super(estadisticas, self).__init__(parent)
        loadUi('estadisticas.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.regresar.clicked.connect(self.back)
        self.botellasdia.setMode(QLCDNumber.Dec)
        self.botellasdia.display(principal.contadordia)
        self.botellashora.setMode(QLCDNumber.Dec)
        self.botellashora.display(principal.contadorhora)
        self.botellames.setMode(QLCDNumber.Dec)
        self.botellames.display(principal.contadormes)
        
    #funcion atras
    def back(self):
        self.hide()
        otraventana=principal(self)
        otraventana.show()




#clase informacion
class info(QMainWindow):

    def __init__(self, parent=None):
        super(info, self).__init__(parent)
        loadUi('info.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.regresar.clicked.connect(self.back)
        self.salir.clicked.connect(self.cerrar)
        
    #funcion atras
    def back(self):
        self.hide()
        otraventana=principal(self)
        otraventana.show()

    #funcion cerrar
    def cerrar(self):
        self.hide()
        otraventana=salir(self)
        otraventana.show()



#clase ingresopet
class ingresopet(QMainWindow):
    def __init__(self, parent=None):
        super(ingresopet, self).__init__(parent)
        loadUi('ingresopet.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.regresar.clicked.connect(self.back)
        self.continuar.clicked.connect(self.cont)
        
        
    #inicializacion de timer para ejecutar una funcion por tiempo indefinido
        self.timer=QTimer()
        self.timer.timeout.connect(self.avanzar)
        self.timer.start(1000)
        self.label_2.hide()
        self.continuar.hide()
        
        
    #funcion que se encarga de avanzar si se detecto botella 
    def avanzar(self):
        
      #si detecto botella avanzare hasta que la botella sea detectada por el sensor de enmedio
        if (GPIO.input(s2))== 1 and (GPIO.input(s1))== 0:
          while (GPIO.input(s1))== 0:
            GPIO.output(in3,GPIO.HIGH)
            GPIO.output(in4,GPIO.LOW)
          sleep(0.32)
          GPIO.output(in3,GPIO.LOW)
          GPIO.output(in4,GPIO.LOW)
          self.timer.timeout.disconnect(self.avanzar)
          self.continuar.show()
          self.label_2.show()
      #si detecta botella en ambos sensores avanzara un poco para dejar botella enmedio
        elif (GPIO.input(s2))== 1 and (GPIO.input(s1))== 1:
          GPIO.output(in3,GPIO.HIGH)
          GPIO.output(in4,GPIO.LOW)
          sleep(0.32)
          GPIO.output(in3,GPIO.LOW)
          GPIO.output(in4,GPIO.LOW)
          self.timer.timeout.disconnect(self.avanzar)
          self.continuar.show()
          self.label_2.show()
          
    #funcion atras
    def back(self):
        #instruccion que devuelve el residuo si es que hay, cuando el usuario ingresa una botella y se regresa al menu principal
        if GPIO.input(s1)==1:
          for i in range(3):
            GPIO.output(in3,GPIO.LOW)
            GPIO.output(in4,GPIO.HIGH)
            sleep(1)
        GPIO.output(in3,GPIO.LOW)
        GPIO.output(in4,GPIO.LOW)
        
        self.hide()
        otraventana=principal(self)
        otraventana.show()
        
    #funcion continuar
    def cont(self):
        self.hide()    
        otraventana=cargando(self)
        otraventana.show()
        
        
#clase cargando  
class cargando(QMainWindow):
    def __init__(self, parent=None):
        super(cargando, self).__init__(parent)
        loadUi('procesando.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.label.setText("Procesando...")
        
        
        self.timer=QTimer()
        self.timer.timeout.connect(self.progreso)
        self.timer.start(1000)
        
        
    def progreso(self):
        
        #condiciones para ser aceptado
        #aqui se evalua sensor de presencia de residuo, posterior a ello se compara con sensor de pet para saber si es valido o no y posterior a ello se evalua si esta vacio o lleno con el sensor de peso
        if ((GPIO.input(s1)) ==1 and (GPIO.input(s5) == 0)):
              #en caso de ser aceptada mover el motor por 3 segundos
              for i in range (100):
                GPIO.output(in3,GPIO.HIGH)
                GPIO.output(in4,GPIO.LOW)
                sleep(0.03)
                self.procesandopet.setValue(i)
              GPIO.output(in3,GPIO.LOW)
              GPIO.output(in4,GPIO.LOW)
              self.hide()    
              otraventana=aceptada(self)
              otraventana.show()
              principal.contadoru(self)
              self.timer.timeout.disconnect(self.progreso)
        
        #como no es aceptado debe regresarse      
        else:
              #se comprueba que exista algun residuo, en caso de que no, el sistema no movera la banda
              if GPIO.input(s1)==1:
                for i in range(100):
                  GPIO.output(in3,GPIO.LOW)
                  GPIO.output(in4,GPIO.HIGH)
                  sleep(0.03)
                  self.procesandopet.setValue(i)
              GPIO.output(in3,GPIO.LOW)
              GPIO.output(in4,GPIO.LOW)
              
              self.hide()    
              otraventana=rechazada(self)
              otraventana.show()
              self.timer.timeout.disconnect(self.progreso)
        
        
#clase aceptada
class aceptada(QMainWindow):

    def __init__(self, parent=None):
        super(aceptada, self).__init__(parent)
        loadUi('aceptada.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.continuar.clicked.connect(self.cont)
        
        
    #funcion continuar 
    def cont(self):
        self.hide()
        otraventana=agregarpet(self)
        otraventana.show()       
                


#clase rechazada rechazada
class rechazada(QMainWindow):

    def __init__(self, parent=None):
        super(rechazada, self).__init__(parent)
        loadUi('invalida.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.regresar.clicked.connect(self.atras)
      
    
    #funcion regresar
    def atras(self):
        self.hide()
        otraventana=ingresopet(self)
        otraventana.show()
        
        
#clase agregar pet
class agregarpet(QMainWindow):

    def __init__(self, parent=None):
        super(agregarpet, self).__init__(parent)
        loadUi('agregarbotellas.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.botonsi.clicked.connect(self.si)
        self.botonno.clicked.connect(self.no)
        
        #Condicion que evalua si se lleno el almacenamiento en el paso anterior
        if (principal.dist < principal.distancia_lleno) :
              self.label.setText("¡ALMACENAMIENTO LLENO!,\nYa no hay espacio \npara agregar más\n Sal y vaciar contenedor")
              self.botonno.setText("Salir")
              self.botonsi.hide()
        else:
              pass
        
        
    #funcion si ingresar mas botellas
    def si(self):
        self.hide()
        otraventana=ingresopet(self)
        otraventana.show()        

    #funcion no ingresar mas botellas
    def no(self):
        self.hide()
        otraventana=fin(self)
        otraventana.show()


#clase fin del proceso
class fin(QMainWindow):

    def __init__(self, parent=None):
        super(fin, self).__init__(parent)
        loadUi('finproceso.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.regresar.clicked.connect(self.back)
        self.lcdNumber_3.setMode(QLCDNumber.Dec)
        self.lcdNumber_3.display(principal.contadorusuario)
        self.ntbotellas.setMode(QLCDNumber.Dec)
        self.ntbotellas.display(principal.contadordia)
        
        
        #instrucciones que describen lo que se muestra en el codigo qr
        if principal.contadorusuario == 1:
            img = qrcode.make("Continúa reciclando y descubre todas las frases que tengo para ti, ¿Te atreves?")
        elif principal.contadorusuario == 2:
            img = qrcode.make("La muerte no es más que el reciclaje que la naturaleza brinda a todos los seres.")
        elif principal.contadorusuario == 3:
            img = qrcode.make("En casa o en la escuela, reciclar es una cosa buena")
        elif principal.contadorusuario == 4:
            img = qrcode.make("Pocas palabras bastan para un buen entendedor, cada basura a su contenedor")
        elif principal.contadorusuario == 5:
            img = qrcode.make("Si no reciclas, no solo estás haciendo daño a la tierra, si no a tus hijos y al resto de descendientes de tu familia")
        elif principal.contadorusuario == 6:
            img = qrcode.make("Pienso, luego reciclo")
        elif principal.contadorusuario == 7:
            img = qrcode.make("Reciclar es más que una acción, es el valor de la responsabilidad por preservar los recursos naturales")
        elif principal.contadorusuario == 8:
            img = qrcode.make("Reciclar nos ayuda a fomentar la creatividad y de ese modo podemos crear nuesvos usos y nuevos tipos de productos")
        elif principal.contadorusuario == 9:
            img = qrcode.make("El Reciclaje y la sabiduría van de la mano. Reciclemos ahora que estamos a tiempo y démosle una segunda oportunidad al planeta.")
        elif principal.contadorusuario == 10:
            img = qrcode.make("¿10 botellas recicladas?, haz batido un gran record")
        elif principal.contadorusuario > 10:
            img = qrcode.make("Wow, me he quedado frases, has hecho una gran acción, continúa asi y comparte con tus compañeros esta experiencia de reciclaje")
        
        f = open("qr.png", "wb")
        img.save(f)
        f.close()
        
        self.pixmap = QPixmap("qr.png")
        smaller_pixmap = self.pixmap.scaled(480, 480, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.qr.setPixmap(smaller_pixmap)
        
      
        
    #funcion volver
    def back(self):
        self.hide()
        otraventana=principal(self)
        otraventana.show()


#instruccion inicial
if __name__=="__main__":       
      app= QtWidgets.QApplication([])
      main = fondo()
      main2 = principal()
      
      
      main.show()
      main2.show()
      app.exec_()
