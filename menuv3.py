# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 22:05:48 2023

@author: horus garcia villanueva
"""

#importamos todas las librerias que se usaran
from imag import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLCDNumber
from PyQt5.QtCore import Qt, QTime, QTimer
from datetime import datetime
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from time import sleep
import time
import qrcode
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

GPIO.setwarnings(False)


#definimos entradas y salidas raspberry
#entradas:
s1 = 3 #presencia
s2 = 5 #PET
s3 = 7 #obstrucciones
s4 = 12 #humedad y temperatura


#usando sensor de nivel
#set GPIO Pins
GPIO_TRIGGER = 11 
GPIO_ECHO = 13 #peligroso conectar con resistencias

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


#salidas
in3 = 36
in4 = 38
enb = 40

#definimos los pines como entradas o salidas
GPIO.setup(s1,GPIO.IN)
GPIO.setup(s2,GPIO.IN)
GPIO.setup(s3,GPIO.IN)
GPIO.setup(s4,GPIO.IN)

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
        
    def digito(self,pressed):
      if pressed == "borrar":
        self.password.setText("")
      else:
        self.password.setText(f'{self.password.text()}{pressed}')
    
        
    def volver(self):
      self.hide()
      otraventana=info(self)
      otraventana.show()

    def cerrarp(self):
      if self.password.text() == "2018":
        sys.exit()
      else:
        self.respuesta.setText("Contraseña\nincorrecta")


class principal(QMainWindow):
    #inicializamos los contadores
    contadorusuario=0
    contadordia=0
    contadormes=0
    contadorhora=0
    s3=0
    s4=0
    
    
    lleno=False
    horaactual=datetime.now().time().hour
    diaactual=datetime.now().day
    #print(diaactual)
    mesactual=datetime.now().month
    #print(mesactual)
    
    def __init__(self,parent=None):
        
        super(principal, self).__init__(parent)
        loadUi('menuv1.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.iniciar.clicked.connect(self.begin)
        self.ajustes.clicked.connect(self.f_info)
        self.estadisticas.clicked.connect(self.f_estadisticas)
       
        
        
        #instruccion que reinicia el contador de usuario
        principal.contadorusuario=0
        
        #instruccion que reinicia el nivel lleno de almacenamiento para ventana agregar pet
        principal.lleno=False
        
        #deteccion de obstrucciones
        principal.s3=GPIO.input(s3)
        
        if (principal.s3 == 1):
            self.notificacion.setGeometry(230,40,771,551)
            self.notificacion.setText("Obstrucción en la banda detectada, salga del menu principal, retirela y \nvuelva al menu principal")
            self.etiquetallenado_2.setText("¿Problema resuelto?\nPresióname")
          
            self.etiquetallenado.hide()
            self.iniciar.hide()
            self.nivelalmacenamiento.hide()
            self.label.hide()
            self.estadisticas.hide()
            self.etiquetallenado_3.hide()
            self.frame.hide()
            self.fecha.hide()
            self.Hora.hide()
            
        
        
        
        # Sensor para detectar nivel de almacenamiento
        #Se manda a traer la funcion
        dist = principal.distance(self) #x
        #interpolacion lineal
        distancia_vacio=50 #x1  100%=y1
        distancia_lleno=6 #x2 0%=y2
        
        #interpolacionlineal= y=y1+((y2-y1)/(x2-x1))*(x-x1)
        nivel=(100+((0-100)/(6-50))*(dist-50))
         
        
         
        #declaramos valores de llenado y vacio
        
        if(dist)>distancia_vacio :
            #"Nivel de llenado = 0%"
            
            self.nivelalmacenamiento.setValue(0)
            
        elif(dist)<distancia_lleno :
            #"Nivel de llenado = 100%"
            self.notificacion.setText("¡ALMACENAMIENTO LLENO!")
              
            self.nivelalmacenamiento.setValue(100)
            self.iniciar.hide()
            
         
        else:
            #nivel actual
            niveldisponible=100-nivel
            
            self.nivelalmacenamiento.setValue(int(niveldisponible))
          
       
            
            
            
        self.timer=QTimer()
        self.timer.timeout.connect(self.lcd_number)
        self.timer.start(1000)
        
    
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
        
    
          

    def begin(self):
        self.hide()
        otraventana=ingresopet(self)
        otraventana.show()
       
       
            

    def f_info(self):
         
          
        self.hide()
        otraventana=info(self)
        otraventana.show()
#           
		
    def f_estadisticas(self):
        self.hide()
        otraventana=estadisticas(self)
        otraventana.show()






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
        
        
    def back(self):
       
        self.hide()
        otraventana=principal(self)
        otraventana.show()






class info(QMainWindow):

    def __init__(self, parent=None):
        super(info, self).__init__(parent)
        loadUi('info.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.regresar.clicked.connect(self.back)
        self.salir.clicked.connect(self.cerrar)
        
        
    def back(self):
        self.hide()
        otraventana=principal(self)
        otraventana.show()

    def cerrar(self):
        self.hide()
        otraventana=salir(self)
        otraventana.show()



class ingresopet(QMainWindow):
    s1=0
    #sensor de PET
    s2=0
    def __init__(self, parent=None):
        super(ingresopet, self).__init__(parent)
        loadUi('ingresopet.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.regresar.clicked.connect(self.back)
        self.continuar.clicked.connect(self.cont)
        
        
        
    def back(self):
        self.hide()
        otraventana=principal(self)
        otraventana.show()
        
    def cont(self):
        ingresopet.s1=GPIO.input(s1)
        ingresopet.s2=GPIO.input(s2)
        #aqui se evalua sensor de presencia de residuo, posterior a ello se compara con sensor de pet para saber si es valido o no 
        
        if (ingresopet.s1 == ingresopet.s2 == 1):
              self.hide()    
              otraventana=aceptada(self)
              otraventana.show()
             
              principal.contadoru(self)
              
        else:
              self.hide()    
              otraventana=rechazada(self)
              otraventana.show()
            
class aceptada(QMainWindow):

    def __init__(self, parent=None):
        super(aceptada, self).__init__(parent)
        loadUi('aceptada.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.continuar.clicked.connect(self.cont)
        
        for i in range (3):
          GPIO.output(in3,GPIO.HIGH)
          GPIO.output(in4,GPIO.LOW)
          sleep(1)
        GPIO.output(in3,GPIO.LOW)
        GPIO.output(in4,GPIO.LOW)
        
        
    def cont(self):
       
        
        #sensor revisa si el contador ya esta lleno
        #se crea variable para ver nivel actual de almacenamiento
        aceptada.sensor=principal.distance(self)
        
        valor_vacio=50 #x1  100%=y1
        valor_lleno=6 #x2 0%=y2
        
            
        if(aceptada.sensor)<valor_lleno :
            #"Nivel de llenado = 100%"
            principal.lleno=True
              
        else:
            pass
            
        self.hide()
        otraventana=agregarpet(self)
        otraventana.show()       
                



class rechazada(QMainWindow):

    def __init__(self, parent=None):
        super(rechazada, self).__init__(parent)
        loadUi('invalida.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.regresar.clicked.connect(self.atras)
        if ingresopet.s1==1:
          for i in range(3):
            GPIO.output(in3,GPIO.LOW)
            GPIO.output(in4,GPIO.HIGH)
            sleep(1)
        GPIO.output(in3,GPIO.LOW)
        GPIO.output(in4,GPIO.LOW)
        
    def atras(self):
        self.parent().show()
        self.close()
        
        
        
        
class agregarpet(QMainWindow):

    def __init__(self, parent=None):
        super(agregarpet, self).__init__(parent)
        loadUi('agregarbotellas.ui', self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.botonsi.clicked.connect(self.si)
        self.botonno.clicked.connect(self.no)
        
        #Condicion que evalua si se lleno el almacenamiento en el paso anterior
        if principal.lleno==True:
              
              self.label.setText("¡ALMACENAMIENTO LLENO!,\nYa no hay espacio \npara agregar más\n Sal y vaciar contenedor")
              self.botonno.setText("Salir")
              self.botonsi.hide()
        else:
              pass
        
        
        
    def si(self):
          
        
        self.hide()
        otraventana=ingresopet(self)
        otraventana.show()        

    def no(self):
        self.hide()
        otraventana=fin(self)
        otraventana.show()


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
        
      
        
        
    def back(self):
        self.hide()
        otraventana=principal(self)
        otraventana.show()

if __name__=="__main__":       
      app= QtWidgets.QApplication([])
      main = fondo()
      main2 = principal()
      
      
      main.show()
      main2.show()
      app.exec_()
