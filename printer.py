#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import serial
import ConfigParser
import logging.handlers
from model import Soci,Varietat,Albara, Finca
from vistaAux import WindowAux
from initial import config, Session

class Printer(object):
    
    def __init__(self):
        
        myLogger = logging.getLogger(__name__)
        self.logger = myLogger
        self.config = config
        self.windowAux = WindowAux()
        try:
            self.port_name = self.config.get("impresora","port")
            self.baudrate = int(self.config.get("impresora","baudrate"))
        except:
            self.logger.debug("No es pot accedir a la configuracio de la impresora")
            errorString = " No es pot accedir a la configuracio de la impresora"
            self.windowAux.openWindowError(errorString)
               
        self.headLine1 = self.config.get("ticket","cap_lin_1")
        self.headLine2 = self.config.get("ticket","cap_lin_2")
        self.headLine3 = self.config.get("ticket","cap_lin_3")
        self.footLine1 = self.config.get("ticket","peu_lin_1")
        self.footLine2 = self.config.get("ticket","peu_lin_2")
        self.footLine3 = self.config.get("ticket","peu_lin_3")    
        self.footLine4 = self.config.get("ticket","peu_lin_4")        
        
        self.printNameFinca = self.config.get("ticket","nom") == 'SI'
        self.printMunicipiFinca = self.config.get("ticket","municipi") == 'SI'
        self.printTermeFinca = self.config.get("ticket","terme") == ' SI'
        self.printPoligonFinca = self.config.get("ticket","poligon") == 'SI'
        self.printParcelaFinca = self.config.get("ticket","parcela") == 'SI'       
        
        self.port = None
        self.portIsOpen = False
        
    def openPort(self):
        baudrate = self.baudrate
        bytesize = serial.EIGHTBITS
        parity = serial.PARITY_NONE
        stop_bits = serial.STOPBITS_ONE
        try:
            self.port = serial.Serial(self.port_name,baudrate,bytesize,parity,stop_bits)
            self.port.flushInput()
        except:
            self.logger.error("Error obrint el port serie en " + str(self.port_name))
            raise Exception('Error obrint port serie de la impresora.')        
        else:
            self.portIsOpen = True
            return self.port

    def closePort(self):
        if self.portIsOpen:
            self.port.close()

    def sendLine(self,line='****** TEST ***********'): 
        try:
            sentBytes = self.port.write(line + '\r\n')
            self.port.flush()
        except:
            self.logger.debug("Error enviant trama a la impresora")
            errorString = " Hi ha hagut un error enviat dades a la impresora. Reviseu el ticket."
            self.windowAux.openWindowError(errorString)
            return 0        
        else:
            return sentBytes

    def sendCut(self): 
        line = chr(29) + "V" + chr(1)
        sentBytes = self.port.write(line) #@UnusedVariable
        self.port.flush()

    def sendAlbara(self,idAlbara):
        ''' Print ticket '''
        session = Session()
        try:
            self.openPort()
        except Exception as detail:
            raise Exception(str(detail))
        else:
            self.logger.debug("Port de la impresora obert en: ")

        
        date = session.query(Albara).filter(Albara.id_albara==idAlbara).\
            one().timestamp.strftime("%d/%m/%Y %H:%M")
        num_albara = str(session.query(Albara).filter(Albara.id_albara==idAlbara).\
            one().num_albara)
        id_soci = session.query(Albara).filter(Albara.id_albara==idAlbara).\
            one().id_soci
        num_soci = str(session.query(Soci).filter(Soci.id_soci==id_soci).\
            one().num_soci)
        nom_soci= str(session.query(Soci).filter(Soci.id_soci==id_soci).\
            one().nom)
        id_finca = session.query(Albara).filter(Albara.id_albara==idAlbara).\
            one().id_finca
        nom_finca = str(session.query(Finca).filter(Finca.id_finca==id_finca).\
            one().nom_finca)
        municipi_finca = str(session.query(Finca).filter(Finca.id_finca==id_finca).\
            one().municipi)
        terme_finca = str(session.query(Finca).filter(Finca.id_finca==id_finca).\
            one().terme)
        poligon_finca = str(session.query(Finca).filter(Finca.id_finca==id_finca).\
            one().poligon)
        parcela_finca = str(session.query(Finca).filter(Finca.id_finca==id_finca).\
            one().parcela)
        id_varietat = session.query(Albara).filter(Albara.id_albara==idAlbara).\
            one().id_varietat
        desc_varietat = session.query(Varietat).\
            filter(Varietat.id_varietat==id_varietat).one().desc_varietat
        carrega = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().carga
        humitat = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().humitat


        lineAux = "\r\n"        
        aux = self.sendLine(lineAux)   #@UnusedVariable     
            
        lineAux = self.headLine1        
        if lineAux <> None:
            aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = self.headLine2        
        if lineAux <> None:
            aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = self.headLine3        
        if lineAux <> None:
            aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = "   ------------------- \r\n"        
        aux = self.sendLine(lineAux) #@UnusedVariable      
        lineAux = "Data i hora: " + date
        aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = 'Numero de albara: ' + num_albara   
        aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = "   ------------------- \r"        
        aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = 'Numero de soci: ' + num_soci
        aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = 'Soci: ' + nom_soci
        aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = "   ------------------- \r"        
        aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = 'Identificador finca: ' + str(id_finca)
        aux = self.sendLine(lineAux) #@UnusedVariable
        if self.printNameFinca :
            lineAux = "Partida: " + nom_finca
            aux = self.sendLine(lineAux) #@UnusedVariable
        if self.printMunicipiFinca :
            lineAux = 'Municipi: ' + str(municipi_finca)
            aux = self.sendLine(lineAux) #@UnusedVariable
        if self.printTermeFinca or self.printPoligonFinca or self.printParcelaFinca:
            lineAux = 'Terme: ' + str(terme_finca) + ' Poligon: ' \
             + str(poligon_finca) + ' Parcela: ' + str(parcela_finca)
            aux = self.sendLine(lineAux) #@UnusedVariable
        
        
        lineAux = "   ------------------- \r"        
        aux = self.sendLine(lineAux) #@UnusedVariable
        ulineAux = lineAux.decode('utf-8') #@UnusedVariable
        lineAux = lineAux.encode('latin-1','ignore')
        aux = self.sendLine(lineAux)  #@UnusedVariable       
        lineAux = 'Varietat: ' + str(desc_varietat)
        aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = 'Carrega: ' + str(carrega) + ' kg'
        aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = 'Humitat: ' + str(humitat) + ' %'
        aux = self.sendLine(lineAux) #@UnusedVariable

        tr = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().tablilla_resultas
        lineAux = 'Tabl/Res.: ' + str(tr)
        aux = self.sendLine(lineAux) #@UnusedVariable

        mescla = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().mescla
        lineAux = 'Mescla: ' + str(mescla) + ' %'
        aux = self.sendLine(lineAux) #@UnusedVariable

        rendiment = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().rendiment_total
        lineAux = 'Rendiment: ' + str(rendiment) + ' %'
        aux = self.sendLine(lineAux) #@UnusedVariable

        porcTamany1 = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().porc_tamany_1
        lineAux = 'Tamany 1: ' + str(porcTamany1) + ' %'
        aux = self.sendLine(lineAux) #@UnusedVariable

        porcTamany2 = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().porc_tamany_2
        lineAux = 'Tamany 2: ' + str(porcTamany2) + ' %'
        aux = self.sendLine(lineAux) #@UnusedVariable

        porcTamany3 = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().porc_tamany_3
        lineAux = 'Tamany 3: ' + str(porcTamany3) + ' %'
        aux = self.sendLine(lineAux) #@UnusedVariable

        observacions = session.query(Albara).\
                filter(Albara.id_albara==idAlbara).\
                one().observacions
        lineAux = 'Observacions: ' + str(observacions)
        aux = self.sendLine(lineAux) #@UnusedVariable

        lineAux = "   ------------------- \r\n"        
        aux = self.sendLine(lineAux) #@UnusedVariable

        lineAux = self.footLine1        
        ulineAux = lineAux.decode('utf-8') #@UnusedVariable
        lineAux = lineAux.encode('latin-1','ignore')
        if lineAux <> None:
            aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = self.footLine2        
        ulineAux = lineAux.decode('utf-8') #@UnusedVariable
        lineAux = lineAux.encode('latin-1','ignore')
        if lineAux <> None:
            aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = self.footLine3        
        ulineAux = lineAux.decode('utf-8') #@UnusedVariable
        lineAux = lineAux.encode('latin-1','ignore')
        if lineAux <> None:
            aux = self.sendLine(lineAux) #@UnusedVariable
        lineAux = self.footLine4        
        ulineAux = lineAux.decode('utf-8') #@UnusedVariable
        lineAux = lineAux.encode('latin-1','ignore')
        if lineAux <> None:
            aux = self.sendLine(lineAux) #@UnusedVariable

        lineAux = "  \r\n\n\n\n\n\n\n\n"        
        aux = self.sendLine(lineAux) #@UnusedVariable  
        
        Session.remove()
        
        self.sendCut()

        if self.portIsOpen:
            self.closePort()
            self.logger.debug("Port de la impresora tancat")
             
def inicialization(config):

######### CONFIGURACIO LOGGING ################################

    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
               'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}

    level_name = config.get("Configuracio","log")
    LOG_FILENAME = config.get("Configuracio","arxiu_log")

    # Set up a specific logger with our desired output level
    myLogger = logging.getLogger("register")
    myLogger.setLevel(LEVELS[level_name])
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(module)s - %(levelname)s - %(message)s")
    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=50000, backupCount=10)
    # add formatter to handler
    handler.setFormatter(formatter)
    myLogger.addHandler(handler)
    # Logging system started
    myLogger.info("LOGGING en funcionament en nivell: "  + str(myLogger.getEffectiveLevel()))
    return myLogger
###############################################################
        
def mainMenu():
    cmd = raw_input('1 -> Obrir port \n\r\
2 -> Tancar port \n\r\
3 -> Enviar trama\n\r\
4 -> Enviar ticket\n\r\
5 -> Enviar tall\n\r\
0 -> Sortir de l\'aplicacio\n\r\
Introduiu comanda:')
    return cmd
    
if __name__ == "__main__":
 
        
    try:
        config = ConfigParser.SafeConfigParser()
        config.read("configuracio.ini")
    except Exception:
        print "No es possible llegir ARXIU DE CONFIGURACIO"
        print Exception.message
        sys.exit()
        
    logger = inicialization(config)
    session = None
    printer = Printer(logger,config,session)

    while True:     
        command = mainMenu()
    
        if command == '1':
            try:
                port = printer.openPort()
            except Exception as error:
                print "Error: " + str(error)
            else:
                print "\n Port obert \n"
                
        elif command == '2':
            try:
                port = printer.closePort()
            except:
                print "Error tancant el port"
            else:
                print "\n Port Tancat \n"
                
        elif command == '3':
            line = raw_input('Introduiu linia a enviar:')
            aux = printer.sendLine(line)
            print "Bytes sent: " + str(aux)

        elif command == '4':
            pesada = raw_input('Introduiu numero de pesada a enviar:')
            aux = printer.sendAlbara(pesada)
            print "Bytes sent: " + str(aux) 
        elif command == '5':
            print "Enviant tall..."
            printer.sendCut()
              
        elif command == '0':
            print "\n Tancant aplicacio \n"
            break
            
        