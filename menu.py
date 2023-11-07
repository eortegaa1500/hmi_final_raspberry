# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 22:05:48 2023

@author: horug
"""
from imag import *
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLCDNumber
from PyQt5.QtCore import Qt, QTime, QTimer
from datetime import datetime
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from time import sleep
import qrcode
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)


#definimos entradas y salidas raspberry
#entradas:
s1 = 3 #presencia
s2 = 5 #PET
s3 = 7 #nivel alto de almacenamiento
s4 = 11 #nivel medio de almacenamiento
s5 = 13 #nivel bajo almacenamiento
#salidas
in3 = 36
in4 = 38
enb = 40

#definimos los pines como entradas o salidas
GPIO.setup(s1,GPIO.IN)
GPIO.setup(s2,GPIO.IN)
GPIO.setup(s3,GPIO.IN)
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
    s5=0
    
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
       # self.nivel()#en caso de que este lleno
        
        
        #instruccion que reinicia el contador de usuario
        principal.contadorusuario=0
        
        #instruccion que reinicia el nivel lleno de almacenamiento para ventana agregar pet
        principal.lleno=False
        
        
        
        
        
        
        #####################sensores para detectar niveles de almacenamiento
        principal.s3=GPIO.input(s3)
        principal.s4=GPIO.input(s4)
        principal.s5=GPIO.input(s5)
        #sensor almacenamiento inferior  
        #principal.s4="a"
        #principal.s4=input("Detecto bajo?: ")
        #sensor almacenamiento medio  
        #principal.s5="a"
        #principal.s5=input("Detecto medio?: ")
        #sensor almacenamiento superior  
        #principal.s3="a"
        #principal.s3=input("Detecto superior?: ")
        
        if (principal.s3 == 1):
              self.notificacion.setText("¡ALMACENAMIENTO LLENO!")
              
              self.nivelalmacenamiento.setValue(100)
              self.iniciar.hide()
        else:
              if (principal.s5 == 1):
                    self.nivelalmacenamiento.setValue(66)
              else:     
                   if (principal.s4 == 1):
                         self.nivelalmacenamiento.setValue(33)
                   else:
                         self.nivelalmacenamiento.setValue(0)
          
          
       
            
            
            
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
        #print(dianuevo)
        #print(mesnuevo)
        
        #condicion si cambia de dia se reinicia contador dia
        if dianuevo == principal.diaactual:
              #print("nada")
              pass
        else:
              #print("cambio")
              principal.contadordia=0
              principal.diaactual=fecha_actual.day
        #print(principal.diaactual)  
        
        
        #condicion si cambia de hora se reinicia contador hora
        if horanuevo == principal.horaactual:
              #print("nada")
              pass
        else:
              #print("cambio")
              principal.contadorhora=0
              principal.horaactual=hora_actual.hour
        #print(principal.diaactual)
        
        #condicion si cambia de mes se reinicia contador mes
        if mesnuevo == principal.mesactual:
              #print("nada")
              pass
        else:
              #print("cambio")
              principal.contadormes=0
              principal.mesactual=fecha_actual.month
        #print(principal.mesactual)
        #print("bu")
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
        #sensor de presencia
        #s1=0
        #sensor de PET
        #s2=0
        #s1=input("Hay residuo?: ")
        #s2=input("Es PET?: ")
        #s1=principal.s1
        #s2=principal.s2
        #print(s1 == s2)
        if (ingresopet.s1 == ingresopet.s2 == 1):
              self.hide()    
              otraventana=aceptada(self)
              otraventana.show()
             
              principal.contadoru(self)
              #print(principal.contadorusuario)
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
       
        #sensor que detectara si ya esta lleno el contenedor por lo que al darle continuar no dejara que ingrese mas botellas indicando que esta lleno
        #sensor detector de almacenamiento lleno
        #principal.s3="a"
        #principal.s3=input("Contenedor lleno? ")
        #print(principal.s3)
        #s3=principal.s3
        aceptada.s3=GPIO.input(s3)
        if aceptada.s3 == 1:
              #print(principal.s3)
              principal.lleno=True
              #print(principal.lleno)
              
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
        #print(principal.lleno)
        if principal.lleno==True:
              #print(principal.lleno)
              self.label.setText("¡ALMACENAMIENTO LLENO!,\nYa no hay espacio \npara agregar más\n Sal y vaciar contenedor")
              self.botonno.setText("Salir")
              self.botonsi.hide()
        else:
              pass
        
        
        
#    def lleno(self):
#        self.label.setText("¡ALMACENAMIENTO LLENO!")
#        self.botonno.setText("Salir")
#        self.botonsi.hide()
        
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
