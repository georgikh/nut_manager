#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import serial
import ConfigParser
import logging.handlers
from vistaAux import WindowAux
from initial import config

class Scale(object):
    
    def __init__(self):
        myLogger = logging.getLogger(__name__)
        self.logger = myLogger
        self.config = config
        self.windowAux = WindowAux()
        try:
            self.port_name = self.config.get("balanca","port")
            self.baudrate = int(self.config.get("balanca","baudrate"))
        except:
            self.port_name = "dev/tttyUSB0"
            self.baudrate = 9600
            self.logger.debug("No es pot accedir a la configuracio de la balanca")
            errorString = " No es pot accedir a la configuracio de la balanca"
            self.windowAux.openWindowError(errorString)
        
        self.lockScalePort = threading.Lock()      
        self.port = None
        self.portIsOpen = False
        
    def openPort(self):
        baudrate = self.baudrate
        bytesize = serial.EIGHTBITS
        parity = serial.PARITY_NONE
        stop_bits = serial.STOPBITS_ONE
        timeout=0.3
        try:
            self.port = serial.Serial(self.port_name,baudrate,bytesize,parity,stop_bits,timeout)
            self.port.flushInput()
        except Exception as detail:
            self.logger.error("Error obrint el port serie en " + str(self.port_name))
            self.logger.error(str(detail))
            raise Exception('Error obrint port serie de la balanca')        
        else:
            self.portIsOpen = True
            return self.port

    def closePort(self):
        if self.portIsOpen:
            self.port.close()

    def receiveData(self):
        
        self.lockScalePort.acquire()
        try:
            self.port.flushInput()
            data = self.port.read(50)
        except Exception as detail:
            return None
            self.logger.error("Error rebent dades: " + detail)
            raise         
        else:
            if len(data)==0:
                raise Exception("No es reben dades de la balanca")
            else:
                return data
        finally:
            self.lockScalePort.release()

    def readWeight(self):
        
        try:
            self.openPort()
        except:
            raise Exception("Error obrint port")
            return None
        
        try:
            data = self.receiveData()
        except Exception as detail:
            raise Exception(str(detail))
        else:
            for i in range(len(data)):
                if data[i-1]=='S' and data[i]=='T' and data[i+13]==',':
                    weight = float(data[i+5:i+13])
                    return weight
                    break
            else:
                raise Exception("No es pot capturar el pes, per que no es estable")
        finally:
            if self.portIsOpen:
                self.closePort()
                        
if __name__ == "__main__" :
    ######### CONFIGURACIO ARXIU INI ##############################

    config = ConfigParser.ConfigParser()
    config.read("configuracio.ini")
    
        ######### CONFIGURACIO LOGGING ################################
    LEVELS = {'debug': logging.DEBUG,
         'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL}    
    level_name = config.get("Configuracio","log")
    LOG_FILENAME = config.get("Configuracio","arxiu_log")
    myLogger = logging.getLogger("register")
    myLogger.setLevel(LEVELS[level_name])
    formatter = logging.Formatter("%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s")
    handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=50000, backupCount=10)
    handler.setFormatter(formatter)
    myLogger.addHandler(handler)
    myLogger.info("LOGGING en funcionament en nivell: "  + str(myLogger.getEffectiveLevel()))

    scale1 = Scale(myLogger,config)
    
    
    try:
        data = scale1.readWeight()
    except Exception as detail:
        print str(detail)
    else:
        print "pesada: " + str(data)
    
    