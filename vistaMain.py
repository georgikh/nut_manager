#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, time
import shutil
import sqlite3

try:  
    import pygtk
    pygtk.require("2.0")  
except:  
    print("pyGTK 2.12 not Available")
    sys.exit(1)
try:  
    import gtk  
except:  
    print("GTK Not Available")
    sys.exit(1)
import py_compile
import logging
from model import Soci, Varietat, Finca #Silo, Albara
import vistaData
import vistaAlbara
import vistaWizard
from vistaAux import decorateString,WindowAux
#import databaseManager
from initial import config, Session

class MainWindow(object):

    def __init__( self):
  
        self.logger = myLogger
        self.config = config
        
        self.lastAlbara = None       

        self.builder = gtk.Builder()
        self.builder.add_from_file("glade/main.glade")
            
        self.windowMain = self.builder.get_object("windowMain")
        
        garrofa = self.config.get("opcions","garrofa")
        if garrofa == 'SI':
            lTipRevision = "GARROFA 2.2.05"             
        else:
            lTipRevision = "AMETLLA 2.2.05"
            
            
        self.logger.info("Repository tip version is %s" % lTipRevision )
                       
        dic = { 
            "on_windowMain_destroy" : self.mainQuit,
            "on_buttonStart_clicked" : self.openWizard,
            "on_buttonData_clicked" : self.openDataWindow,
            "on_buttonAlbarans_clicked": self.openAlbaransWindow,
            }
        self.builder.connect_signals( dic )

        self.buttonStart = self.builder.get_object("buttonStart")        
        self.buttonData = self.builder.get_object("buttonData")
        self.buttonAlbarans = self.builder.get_object("buttonAlbarans")

        self.labelTitle = self.builder.get_object("labelTitle")
        self.labelTitle.set_label(decorateString(lTipRevision,"black","26"))
       
        self.labelNumeroAlbara = self.builder.get_object("labelNumeroAlbara")
        self.labelNumeroSoci = self.builder.get_object("labelNumeroSoci")
        self.labelNomSoci = self.builder.get_object("labelNomSoci")
        self.labelFinca = self.builder.get_object("labelFinca")
        self.labelVarietat = self.builder.get_object("labelVarietat")
        self.labelHumitat = self.builder.get_object("labelHumitat")
        self.labelMescla = self.builder.get_object("labelMescla")
        self.labelCarrega = self.builder.get_object("labelCarrega")
        self.labelTR = self.builder.get_object("labelTR")
        self.labelRendiment = self.builder.get_object("labelRendiment")
                            
        self.updateLabels()
                                                     
        self.windowMain.maximize()     
        self.windowMain.show()

    def updateLabels(self):
        
        session = Session()
        self.logger.debug("Update Labels. Inciant session: " + str(session))
        
        if self.lastAlbara <> None:        
            numeroAlbara = str(self.lastAlbara.num_albara)
            idSoci = self.lastAlbara.id_soci
            idFinca = self.lastAlbara.id_finca
            numeroSoci = str(session.query(Soci).filter(Soci.id_soci==idSoci).one().num_soci)
            nomSoci = str(session.query(Soci).filter(Soci.id_soci==idSoci).one().nom)
            nomFinca = str(session.query(Finca).filter(Finca.id_finca==idFinca).one().nom_finca)
            idVarietat = self.lastAlbara.id_varietat
            descVarietat = session.query(Varietat).filter(Varietat.id_varietat==idVarietat).one().desc_varietat
            humitat = str(self.lastAlbara.humitat)
            mescla = str(self.lastAlbara.mescla)
            carrega = str(self.lastAlbara.carga)
            tr = self.lastAlbara.tablilla_resultas
            rendiment = str(self.lastAlbara.rendiment_total)
        else:
            numeroAlbara = "Albara"
            numeroSoci = "Numero Soci"
            nomSoci = "nom Soci"
            nomFinca = "Finca"
            descVarietat = "Varietat"
            humitat = "Humitat"
            mescla = "Mescla"
            carrega = "Carrega"
            tr = "TR"
            rendiment = "Rendiment"
                   
        self.labelNumeroAlbara.set_label(decorateString(numeroAlbara,"blue","16"))
        self.labelNumeroSoci.set_label(decorateString(numeroSoci,"blue","16"))
        self.labelNomSoci.set_label(decorateString(nomSoci,"blue","16"))
        self.labelFinca.set_label(decorateString(nomFinca,"blue","16"))
        self.labelVarietat.set_label(decorateString(descVarietat,"blue","16"))
        self.labelHumitat.set_label(decorateString(humitat,"blue","16"))
        self.labelMescla.set_label(decorateString(mescla,"blue","16"))
        self.labelCarrega.set_label(decorateString(carrega,"blue","16"))
        self.labelRendiment.set_label(decorateString(rendiment,"blue","16"))
        self.labelTR.set_label(decorateString(tr,"blue","16"))        
         
        Session.remove()
                         
    def openWizard(self, widget):  #@UnusedVariable

        windowWizard = vistaWizard.WindowWizard(self) #@UnusedVariable    
            
    def openDataWindow(self, widget):  #@UnusedVariable
        windowData = vistaData.WindowData() #@UnusedVariable

    def openAlbaransWindow(self, widget):  #@UnusedVariable
        
        windowAlbarans = vistaAlbara.WindowAlbara() #@UnusedVariable
                
    def mainQuit(self, widget): #@UnusedVariable
        self.databaseBackup()
        gtk.main_quit()
 
    def databaseBackup(self):
        bbddType = config.get("BBDD","tipus") 
        backupDir = self.config.get("BBDD","directoriBackup")
            
        if bbddType == "mysql":
            try:
                user = self.config.get("BBDD","usuari")
                password = self.config.get("BBDD","contrasenya")
                databaseUsed = self.config.get("BBDD","basedades")
                #server = self.config.get("BBDD","servidor")      
                manager = databaseManager.DatabaseManager(user,password,password,backupDir)
                arxiu = manager.safetyBackupDatabase(databaseUsed)
            except Exception as error:
                self.logger.error("Error copiant BBDD MySQL:")
                self.logger.error(str(error))
            else:
                self.logger.debug("Copia seguretat BBDD Mysql en arxiu "+ arxiu )
        elif bbddType == "sqlite":
            try:
                arxiuSqlite = config.get("BBDD","arxiuSqlite")
                rutaSqlite = config.get("BBDD","rutaSqlite")
                backup_file = os.path.join(backupDir, os.path.basename(arxiuSqlite) +
                               time.strftime("-%Y%m%d"))

                connection = sqlite3.connect(rutaSqlite + arxiuSqlite)
                cursor = connection.cursor()

                # Lock database before making a backup
                cursor.execute('begin immediate')
                # Make new backup file
                shutil.copyfile(rutaSqlite + arxiuSqlite, backup_file)
                # Unlock database
                connection.rollback()
            except Exception as error:
                self.logger.error("Error copiant BBDD SQlite:")
                self.logger.error(str(error))
            else:
                self.logger.debug("Copia seguretat BBDD Sqlite en arxiu "+ backup_file )
                       
if __name__ == "__main__":
    try:
        py_compile.compile('vistaMain.py')
    except:
        print "No es pot compilar arxiu vistaMain.py"
 
    myLogger = logging.getLogger(__name__)      
        
    try:
        session = Session()       
    except Exception as detail:
        myLogger.error("Error accedint a la BBDD. ")
        myLogger.error(str(detail))
        app = WindowAux()
        app.openWindowError("No es pot accedir a la BBDD ")
    else:
        Session.remove()
        myLogger.debug("Iniciant aplicacio principal...")
        app = MainWindow()
    finally:
        Session.remove()
        gtk.main()
