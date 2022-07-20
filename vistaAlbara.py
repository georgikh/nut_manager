#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

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

from datetime import datetime, date, time
from model import Soci, Albara, Silo, Varietat #, Finca
import decimal
import csv
import vistaAux
import printer
import logging
from initial import config, Session

class WindowAlbara(object):

    def __init__( self):
                
        self.builder = gtk.Builder()
        self.builder.add_from_file("glade/albara.glade")

        self.windowAlbara = self.builder.get_object("windowAlbara")
        
        self.windowAux = vistaAux.WindowAux()
        
        myLogger = logging.getLogger(__name__)
        self.logger = myLogger
        self.config = config
        self.printer = printer.Printer()
        
        dic = { 
            "on_buttonEditAlbara_clicked" : self.openWindowEditAlbara,
            "on_buttonDeleteAlbara_clicked" : self.openWindowDeleteAlbara,
            "on_buttonPrintAlbara_clicked" : self.printAlbara,
            "on_windowAlbara_destroy" : self.windowAlbaraDestroy,        
            "on_data_hora_clicked" : self.orderByTimestamp,
            "on_num_soci_clicked" : self.orderByNumSoci,
            "on_buttonFilter_clicked" : self.filterAlbara,
            "on_buttonInitialDate_clicked" : self.buttonInitialDate,
            "on_buttonFinalDate_clicked" : self.buttonFinalDate,
            "on_buttonCalendarSave_clicked" : self.saveDate,
            "on_calendar_day_selected_double_click" : self.saveDate,        
            "on_buttonCalendarCancel_clicked": self.cancelCalendar,
            "on_buttonCancelEdit_clicked" : self.closeWindowEditAlbara,
            "on_treeviewAlbara_cursor_changed" : self.cursorAlbaraChanged,
            "on_buttonSaveEditSoci_clicked" : self.saveAlbaraEditData,
            "on_buttonExportData_clicked" : self.exportData,
            "on_buttonSi_clicked" : self.deleteAlbara,
            "on_buttonNo_clicked" : self.closeWindowDeleteAlbara,
            }
            
        self.builder.connect_signals(dic)

        self.albaraList = self.builder.get_object("liststoreAlbara")
        self.albaraList.set_sort_column_id(0,gtk.SORT_DESCENDING)
        self.orderDescending = True
        
        self.varietatList = self.builder.get_object("liststoreVarietats")
        self.siloList = self.builder.get_object("liststoreSilos")
        self.trList = self.builder.get_object("liststoreTR")
        
        session = Session()
        
        for instance in session.query(Varietat):
            self.varietatList.append([instance.id_varietat,instance.desc_varietat,instance.codi])

        for instance in session.query(Silo):
            self.siloList.append([instance.id_silo,instance.desc_silo])

        Session.remove()
        
        self.trList.append([0,"T"])
        self.trList.append([1,"R"])
        self.trList.append([2,"0"])
        self.trList.append([3,"D"]) 
               
        self.buttonEditAlbara = self.builder.get_object("buttonEditAlbara")
        self.buttonDeleteAlbara = self.builder.get_object("buttonDeleteAlbara")
        self.buttonPrintAlbara = self.builder.get_object("buttonPrintAlbara")
        self.buttonEditAlbara.set_sensitive(False)
        self.buttonDeleteAlbara.set_sensitive(False)
        self.buttonPrintAlbara.set_sensitive(False)
                
        self.entryFilterSociNumero = self.builder.get_object("entryFilterSociNumero")
        self.entryFilterSociNom = self.builder.get_object("entryFilterSociNom")
        self.entryFilterAlbaraNumAlbara = self.builder.get_object("entryFilterAlbaraNumAlbara")
        self.entryFilterInitialDate = self.builder.get_object("entryFilterInitialDate")
        self.entryFilterFinalDate = self.builder.get_object("entryFilterFinalDate")
        
        self.treeviewAlbara = self.builder.get_object("treeviewAlbara")
        self.treeSelectionAlbara = self.treeviewAlbara.get_selection()
        self.treeSelectionAlbara.set_mode(gtk.SELECTION_SINGLE)
                
        self.windowEditAlbara = self.builder.get_object("windowEditAlbara")
        self.dialogConfirmDelete = self.builder.get_object("dialogConfirmDelete")
        
        self.windowCalendar = self.builder.get_object("windowCalendar")
        self.calendar = self.builder.get_object("calendar")
        self.isInitialDate = False
        self.isFinalDate = False
        self.dateInitial = date(2000,1,1)
        self.dateFinal = date(2100,1,1)
        self.timeInitial = time(0,0)
        self.timeFinal = time(23,59)
        self.datetimeInitial = datetime.combine(self.dateInitial,self.timeInitial)
        self.datetimeFinal = datetime.combine(self.dateFinal,self.timeFinal)
        self.idAlbaraSelected = None

        self.entryEditNumeroAlbara = self.builder.get_object("entryEditNumeroAlbara")
        self.entryTimestamp = self.builder.get_object("entryTimestamp")
        self.entryEditSociNumero = self.builder.get_object("entryEditSociNumero")
        self.entryEditSociNom = self.builder.get_object("entryEditSociNom")
        self.comboboxVarietat = self.builder.get_object("comboboxVarietat")
        self.entryEditCarrega = self.builder.get_object("entryEditCarrega")
        self.entryEditHumitat = self.builder.get_object("entryEditHumitat")
        self.comboboxTR = self.builder.get_object("comboboxTR")
        self.entryEditMescla = self.builder.get_object("entryEditMescla")
        self.comboboxSilo1 = self.builder.get_object("comboboxSilo1")
        self.entryEditPorcSilo1 = self.builder.get_object("entryEditPorcSilo1")
        self.comboboxSilo2 = self.builder.get_object("comboboxSilo2")
        self.entryEditPorcSilo2 = self.builder.get_object("entryEditPorcSilo2")
        self.entryEditRendiment = self.builder.get_object("entryEditRendiment")
        self.entryEditPorcTamany1 = self.builder.get_object("entryEditPorcTamany1")
        self.entryEditPorcTamany2 = self.builder.get_object("entryEditPorcTamany2")
        self.entryEditPorcTamany3 = self.builder.get_object("entryEditPorcTamany3")
        self.entryEditObservacions = self.builder.get_object("entryEditObservacions")

        self.updateAlbaraTreeView()               
                     
        try:
            self.windowAlbara.maximize()
            self.windowAlbara.show()                    
        except:
            self.logger.error("Error Mostrant finestra albarans")
            
    def orderByTimestamp(self,widgets): #@UnusedVariable
        if self.orderDescending :
            self.albaraList.set_sort_column_id(2,gtk.SORT_ASCENDING)
            self.orderDescending = False
        else:
            self.albaraList.set_sort_column_id(2,gtk.SORT_DESCENDING)
            self.orderDescending = True
            
    def orderByNumSoci(self,widgets): #@UnusedVariable
        self.albaraList.set_sort_column_id(3,gtk.SORT_ASCENDING)

    def cursorAlbaraChanged(self,widget): #@UnusedVariable
        self.buttonEditAlbara.set_sensitive(True)
        self.buttonDeleteAlbara.set_sensitive(True)        
        self.buttonPrintAlbara.set_sensitive(True)

    def openWindowEditAlbara(self,widgets): #@UnusedVariable
        try:
            (treemodel, iterSelected) = self.treeviewAlbara.get_selection().get_selected()
            self.idAlbaraSelected = treemodel.get_value(iterSelected,0)
        except:
            self.windowAux.openWindowError("Heu d'escollir un albarà")

        self.entryEditNumeroAlbara.set_text(treemodel.get_value(iterSelected,1))
        self.entryTimestamp.set_text(treemodel.get_value(iterSelected,2))
        self.entryEditSociNumero.set_text(treemodel.get_value(iterSelected,3))
        self.entryEditSociNom.set_text(treemodel.get_value(iterSelected,4))
        self.entryEditCarrega.set_text(treemodel.get_value(iterSelected,6))
        self.entryEditHumitat.set_text(treemodel.get_value(iterSelected,7))
        self.entryEditMescla.set_text(treemodel.get_value(iterSelected,9))
        self.entryEditPorcSilo1.set_text(treemodel.get_value(iterSelected,11))
        self.entryEditPorcSilo2.set_text(treemodel.get_value(iterSelected,13))
        self.entryEditRendiment.set_text(treemodel.get_value(iterSelected,14))
        self.entryEditPorcTamany1.set_text(treemodel.get_value(iterSelected,15))
        self.entryEditPorcTamany2.set_text(treemodel.get_value(iterSelected,16))
        self.entryEditPorcTamany3.set_text(treemodel.get_value(iterSelected,17))
        self.entryEditObservacions.set_text(treemodel.get_value(iterSelected,18))
        
                
        aux = self.varietatList.get_iter_first()
        while aux <> None:
            if self.varietatList.get_value(aux,1) == treemodel.get_value(iterSelected,5):
                self.comboboxVarietat.set_active_iter(aux)
                break        
            else:
                aux = self.varietatList.iter_next(aux)

        aux = self.siloList.get_iter_first()
        while aux <> None:
            if self.siloList.get_value(aux,1) == treemodel.get_value(iterSelected,10):
                self.comboboxSilo1.set_active_iter(aux)
                break        
            else:
                aux = self.siloList.iter_next(aux)                

        aux = self.siloList.get_iter_first()
        while aux <> None:
            if self.siloList.get_value(aux,1) == treemodel.get_value(iterSelected,12):
                self.comboboxSilo2.set_active_iter(aux)
                break        
            else:
                aux = self.siloList.iter_next(aux)

        aux = self.trList.get_iter_first()
        while aux <> None:
            if self.trList.get_value(aux,1) == treemodel.get_value(iterSelected,8):
                self.comboboxTR.set_active_iter(aux)
                break        
            else:
                aux = self.trList.iter_next(aux)
                                          
        self.windowEditAlbara.show()

    def openWindowDeleteAlbara(self,widget): #@UnusedVariable
        self.dialogConfirmDelete.show()
        
    def closeWindowEditAlbara(self,widget): #@UnusedVariable
        self.windowEditAlbara.hide()

    def saveAlbaraEditData(self,widget): #@UnusedVariable
        session = Session()                           
        albara = session.query(Albara).filter_by(id_albara=self.idAlbaraSelected).one()
        albara.id_silo_1 = self.siloList.get_value(self.comboboxSilo1.get_active_iter(),0)
        albara.id_silo_2 = self.siloList.get_value(self.comboboxSilo2.get_active_iter(),0)
        albara.id_varietat = self.varietatList.get_value(self.comboboxVarietat.get_active_iter(),0)                        
        albara.tablilla_resultas = self.trList.get_value(self.comboboxTR.get_active_iter(),1)
        albara.carga = int(self.entryEditCarrega.get_text())
        albara.humitat = float(self.entryEditHumitat.get_text())
        albara.mescla = int(self.entryEditMescla.get_text())
        albara.porc_silo_1 = int(self.entryEditPorcSilo1.get_text())
        albara.porc_silo_2 = int(self.entryEditPorcSilo2.get_text())
        albara.rendiment_total = decimal.Decimal(self.entryEditRendiment.get_text()).\
                                quantize(decimal.Decimal('0.01'))
        albara._porc_tamany_1 = int(self.entryEditPorcTamany1.get_text())
        albara._porc_tamany_2 = int(self.entryEditPorcTamany2.get_text())
        albara._porc_tamany_3 = int(self.entryEditPorcTamany3.get_text())
        albara.observacions = self.entryEditObservacions.get_text()
        
        session.commit()
        
        Session.remove()
        
        self.updateAlbaraTreeView()
                            
        self.windowEditAlbara.hide()        

    def deleteAlbara(self,widget): #@UnusedVariable
        session = Session()
        
        try:
            (treemodel, iterSelected) = self.treeviewAlbara.get_selection().get_selected()
            self.idAlbaraSelected = treemodel.get_value(iterSelected,0)
        except:
            self.windowAux.openWindowError("Heu d'escollir un albarà")

        try:
            albara = session.query(Albara).filter_by(id_albara=self.idAlbaraSelected).delete() #@UnusedVariable
            session.commit()
            Session.remove()
        except Exception as detail:
            self.logger.error("Error Deleting albara id: " + str(self.idAlbaraSelected))
            self.logger.error("Error detail: " + str(detail))
            errorString = "Error intentant esborrar algun element de la BBDD. Reviseu les dependencies."
            self.windowAux.openWindowError(errorString)        
        else:    
            (treemodel, iterSelected) = self.treeviewAlbara.get_selection().get_selected()            
            self.albaraList.remove(iterSelected)
        finally:
            self.dialogConfirmDelete.hide()

    def closeWindowDeleteAlbara(self,widget): #@UnusedVariable
        self.dialogConfirmDelete.hide()

    def printAlbara(self,widget): #@UnusedVariable
 
        try:
            (treemodel, iterSelected) = self.treeviewAlbara.get_selection().get_selected()
            self.idAlbaraSelected = treemodel.get_value(iterSelected,0)
        except:
            self.windowAux.openWindowError("Heu d'escollir un albarà")
            raise
        
        try:
            self.printer.sendAlbara(self.idAlbaraSelected)
        except:
            errorWindow = vistaAux.WindowAux()
            errorWindow.openWindowError("Error imprimint en la impresora")
        else:
            self.logger.debug("Albara impres amb Id " + str(self.idAlbaraSelected))
               
    def filterAlbara(self,widget):  #@UnusedVariable  
        session = Session()
        txtFilterSociNumero = self.entryFilterSociNumero.get_text()
        txtFilterSociNom = self.entryFilterSociNom.get_text()
        txtFilterAlbaraNumAlbara = self.entryFilterAlbaraNumAlbara.get_text()
                        
        self.albaraList.clear()
        for albara, soci, varietat in session.query(\
                Albara,Soci,Varietat).\
                filter(Albara.id_soci==Soci.id_soci).\
                filter(Albara.id_varietat==Varietat.id_varietat).\
                filter(Soci.num_soci.contains(txtFilterSociNumero)).\
                filter(Soci.nom.contains(txtFilterSociNom)).\
            filter(Albara.num_albara.contains(txtFilterAlbaraNumAlbara)).\
            filter(Albara.timestamp >= self.datetimeInitial).\
            filter(Albara.timestamp <= self.datetimeFinal):
            try:
                desc_silo_1 = session.query(Silo).\
                            filter(Silo.id_silo==albara.id_silo_1).one().\
                    desc_silo
            except Exception:
                desc_silo_1 = ''
                
            try:
                desc_silo_2 = self.session.query(Silo).\
                    filter(Silo.id_silo==albara.id_silo_2).\
                    desc_silo                        
            except Exception:
                desc_silo_2 = ''
                 
            self.albaraList.append([albara.id_albara,albara.num_albara,\
                albara.timestamp,soci.num_soci,soci.nom,albara.id_finca,varietat.desc_varietat,\
                albara.carga,albara.humitat,albara.tablilla_resultas,\
                albara.mescla,desc_silo_1,albara.porc_silo_1,\
                desc_silo_2,albara.porc_silo_2,albara.rendiment_total,\
                albara.porc_tamany_1,albara.porc_tamany_2,albara.porc_tamany_3,\
                albara.observacions,varietat.codi])
        Session.remove() 
              
    def buttonInitialDate(self,widget): #@UnusedVariable
        self.isInitialDate = True
        self.isFinalDate = False
        self.windowCalendar.show()        

    def buttonFinalDate(self,widget): #@UnusedVariable
        self.isInitialDate = False
        self.isFinalDate = True
        self.windowCalendar.show()

    def updateAlbaraTreeView(self):

        self.albaraList.clear()
        
        session = Session()
        
        for albara, soci, varietat in session.query(\
                Albara,Soci,Varietat).\
                filter(Albara.id_soci==Soci.id_soci).\
                filter(Albara.id_varietat==Varietat.id_varietat):
            try:
                desc_silo_1 = session.query(Silo).\
                            filter(Silo.id_silo==albara.id_silo_1).one().\
                            desc_silo
            except Exception:
                desc_silo_1 = ''
                
            try:
                desc_silo_2 = session.query(Silo).\
                            filter(Silo.id_silo==albara.id_silo_2).one().\
                            desc_silo                        
            except Exception:
                desc_silo_2 = ''
                
            self.albaraList.append([albara.id_albara,albara.num_albara,\
                albara.timestamp,soci.num_soci,soci.nom,albara.id_finca,varietat.desc_varietat,\
                albara.carga,albara.humitat,albara.tablilla_resultas,\
                albara.mescla,desc_silo_1,albara.porc_silo_1,\
                desc_silo_2,albara.porc_silo_2,albara.rendiment_total,\
                albara.porc_tamany_1,albara.porc_tamany_2,albara.porc_tamany_3,\
                albara.observacions,varietat.codi])
        
        Session.remove()

    def saveDate(self,widget): #@UnusedVariable
        
        if self.isInitialDate:
            selDate = self.calendar.get_date() 
            self.entryFilterInitialDate.set_text(str(selDate[2])+\
                "/"+str(selDate[1]+1)+"/"+str(selDate[0]))
            self.dateInitial = date(selDate[0],selDate[1]+1,selDate[2])
            self.datetimeInitial = datetime.combine(self.dateInitial,self.timeInitial)
        elif self.isFinalDate:
            selDate = self.calendar.get_date() 
            self.entryFilterFinalDate.set_text(str(selDate[2])+\
                "/"+str(selDate[1]+1)+"/"+str(selDate[0]))
            self.dateFinal = date(selDate[0],selDate[1]+1,selDate[2])
            self.datetimeFinal = datetime.combine(self.dateFinal,self.timeFinal)
        self.windowCalendar.hide()                

    def cancelCalendar(self,widget): #@UnusedVariable
        self.windowCalendar.hide()                

    def exportData(self,widget): #@UnusedVariable
        regFile = self.config.get("Configuracio","arxiu_csv") + \
            datetime.now().strftime("%Y%m%d%H%M") + ".csv"
        delimitador = self.config.get("Configuracio","delimitador")   # delimitar excel           

        try:
            f = open(regFile,"wb")
            registerWritter = csv.writer(f,delimiter = delimitador)
            registerWritter.writerow(["N ALBARA","DATA HORA","Num SOCI","Nom SOCI",\
            "Varietat","Carrega","Humitat","TablRes","Mescla","Silo 1", "Silo 1 %",\
            "Silo 2","Silo 2 %","Rendiment","Tamany 1 %", "Tamany 2 %", "Tamany 3 %",\
            "Observacions"])
            session = Session()
            aux = self.albaraList.get_iter_first()
            while aux <> None:
                n_albara = self.albaraList.get_value(aux,1)
                timestamp = self.albaraList.get_value(aux,2)[:-7]
                
                albaraC = session.query(Albara).\
                            filter(Albara.num_albara==n_albara).one()
                id_soci = albaraC.id_soci 
                sociC = session.query(Soci).\
                            filter(Soci.id_soci==id_soci).one()
                n_soci = sociC.num_soci
                soci = sociC.nom
                id_varietat = albaraC.id_varietat
                varietatC = session.query(Varietat).\
                            filter(Varietat.id_varietat==id_varietat).one()
                varietat = varietatC.codi
                carrega = albaraC.carga
                humitat = albaraC.humitat
                tr = albaraC.tablilla_resultas
                mescla = albaraC.mescla
                id_silo1 = albaraC.id_silo_1
                silo1C = session.query(Silo).\
                            filter(Silo.id_silo==id_silo1).one()
                silo1 = silo1C.desc_silo
                psilo1 = albaraC.porc_silo_1
                id_silo2 = albaraC.id_silo_2
                silo2C = session.query(Silo).\
                            filter(Silo.id_silo==id_silo2).one()
                silo2 = silo2C.desc_silo
                psilo2 = albaraC.porc_silo_2
                rendiment = albaraC.rendiment_total
                tamany1 = albaraC.porc_tamany_1
                tamany2 = albaraC.porc_tamany_2
                tamany3 = albaraC.porc_tamany_3
                observacions = albaraC.id_finca
                
                registerWritter.writerow([n_albara,timestamp,n_soci,soci,\
                    varietat,carrega,humitat,tr,mescla,silo1,psilo1,silo2,\
                    psilo2,rendiment,tamany1,tamany2,tamany3,observacions])
                    
                aux = self.albaraList.iter_next(aux)
                                            
            Session.remove()
            
            f.close()

        except Exception as detail:
            self.logger.error("Error accedint al fitxer de registre")
            self.logger.error(str(detail))
            self.windowAux.openWindowError("Error gravant arxiu de registre.\n" + str(detail))
        else:
            self.logger.info("Arxiu exportat:" + str(regFile))
            self.windowAux.openWindowInfo("Arxiu exportat en: " + str(regFile))
            
    def windowAlbaraDestroy(self,widget): #@UnusedVariable
        self.builder.get_object("windowAlbara").destroy()
        if __name__ == "__main__":
            print "Tanquem aplicacio"
            sys.exit(0)
                                    
if __name__ == "__main__":
    app = WindowAlbara()
    gtk.main()
