#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime #, date, time

try:  
    import pygtk  
    pygtk.require("2.0")  
except:  
    print("pyGTK 2.12 not Available")
    sys.exit(1)
try:  
    import gtk  
#    import gtk.glade  
except:  
    print("GTK Not Available")
    sys.exit(1)
    
import logging   
import pango
from sqlalchemy import func, cast, NUMERIC, desc
import decimal
from model import Soci, Silo, Varietat, Albara, Finca
import scale
import printer
from vistaAux import WindowAux,decorateString
from initial import config, Session

class WindowWizard(object):

    def __init__(self,parent):

        self.builder = gtk.Builder()
        self.builder.add_from_file("glade/wizard.glade")

        myLogger = logging.getLogger(__name__)
        self.logger = myLogger      
        self.config = config
        session = Session()
        self.logger.debug("Session: " + str(session))
        
        self.parent = parent
        self.windowAux = WindowAux()
        self.errorWindow = WindowAux()
        self.scale = scale.Scale()
        self.printer = printer.Printer()
        self.iterSelected = None
        self.IdSociSelected = None
        self.IdVarietatSelected = None
        self.IdPropertySelected = None
        self.IdSilo1Selected = 1
        self.IdSilo2Selected = 1
        self.trSelected = None
        self.carrega = 0 
        self.humitat = 0 
        self.mescla = 0
        self.grsMescla = 0.0
        self.porcSilo1 = 100  
        self.porcSilo2 = 0
        self.cascara1 = 0.0  
        self.cascara2 = 0.0
        self.cascara3 = 0.0
        self.gra1 = 0.0
        self.gra2 = 0.0
        self.gra3 = 0.0
        self.rendiment1 = 0.0
        self.rendiment2 = 0.0        
        self.rendiment3 = 0.0
        self.rendimentTotal = 0.0
        self.tamany1 = 0.0
        self.tamany2 = 0.0
        self.tamany3 = 0.0
        self.porcTamany1 = 0
        self.porcTamany2 = 0
        self.porcTamany3 = 0
        self.garrofa = False
        self.averiaBascula = False
              
        garrofa = self.config.get("opcions","garrofa")
        if garrofa == 'SI':
            self.garrofa = True
        averia = self.config.get("opcions","averia")
        if averia == 'SI':
            self.averiaBascula = True       
        
        dic = { 
            "on_windowSelection_destroy" : self.windowSelectionDestroy,        
            "on_entryFilterSociNumero_changed" : self.entrySociChanged,
            "on_entryFilterSociNom_changed" : self.entrySociChanged,
            "on_treeviewSocis_cursor_changed" : self.cursorChangedSocis,
            "on_treeviewProperties_cursor_changed" : self.cursorChangedProperties,
            "on_comboboxVarietat_changed" : self.changedVarietat,
            "on_comboboxSilo1_changed"  : self.changedSilo1,
            "on_comboboxSilo2_changed"  : self.changedSilo2,
            "on_entryCarrega_changed"  : self.changedCarrega,
            "on_entryHumitat_changed"  : self.changedHumitat,
            "on_entryPorcSilo1_changed"  : self.changedPorcSilo1,
            "on_entryPorcSilo2_changed"  : self.changedPorcSilo2,
            "on_comboboxTR_changed" : self.changedTR,
            "on_buttonMescla_clicked" : self.captureMescla,
            "on_buttonCascara1_clicked" : self.captureCascara1,
            "on_buttonCascara2_clicked" : self.captureCascara2,
            "on_buttonCascara3_clicked" : self.captureCascara3,
            "on_buttonGra1_clicked" : self.captureGra1,                        
            "on_buttonGra2_clicked" : self.captureGra2,                        
            "on_buttonGra3_clicked" : self.captureGra3,                        
            "on_buttonTamany1_clicked" : self.captureTamany1,                        
            "on_buttonTamany2_clicked" : self.captureTamany2,
            "on_entryCascara1_changed" : self.readCascara1,
            "on_entryCascara2_changed" : self.readCascara2,
            "on_entryCascara3_changed" : self.readCascara3,
            "on_entryGra1_changed" : self.readGra1,
            "on_entryGra2_changed" : self.readGra2,
            "on_entryGra3_changed" : self.readGra3,
            "on_entryMescla_changed" : self.readMescla,
            "on_entryTamany1_changed" : self.readTamany1,
            "on_entryTamany2_changed" : self.readTamany2,            
            "on_buttonWizardCancel_clicked" : self.windowSelectionDestroy,
            "on_buttonWizardValidate_clicked" : self.validateSelection
            }
            
        self.builder.connect_signals(dic)

        self.window = self.builder.get_object("windowSelection")
        self.socisList = self.builder.get_object("liststoreSocis")
        self.propertiesList = self.builder.get_object("liststoreProperties")
        self.varietatsList = self.builder.get_object("liststoreVarietats")
        self.silosList = self.builder.get_object("liststoreSilos")
        self.trList = self.builder.get_object("liststoreTR")
                
        for silo  in session.query(Silo):
            self.silosList.append([silo.id_silo,silo.desc_silo])

        for varietat  in session.query(Varietat):
            self.varietatsList.append([varietat.id_varietat,varietat.desc_varietat])

        self.trList.append([0,"T"])
        self.trList.append([1,"R"])
        self.trList.append([1,"0"])
        self.trList.append([1,"D"])
                
        self.treeviewSocis = self.builder.get_object("treeviewSocis")
        self.treeSelectionSocis = self.treeviewSocis.get_selection()
        self.treeSelectionSocis.set_mode(gtk.SELECTION_SINGLE)

        self.treeviewProperties = self.builder.get_object("treeviewProperties")
        self.treeSelectionProperties = self.treeviewProperties.get_selection()
        self.treeSelectionProperties.set_mode(gtk.SELECTION_SINGLE)
        
        self.entryFilterSociNumero = self.builder.get_object("entryFilterSociNumero")
        self.entryFilterSociNom = self.builder.get_object("entryFilterSociNom")

        self.entrySelectedSociNumero = self.builder.get_object("entrySelectedSociNumero")
        self.entrySelectedSociNom = self.builder.get_object("entrySelectedSociNom")

        self.comboboxVarietat = self.builder.get_object("comboboxVarietat")
        self.comboboxSilo1 = self.builder.get_object("comboboxSilo1")
        self.comboboxSilo2 = self.builder.get_object("comboboxSilo2")
        self.comboboxTR = self.builder.get_object("comboboxTR")
        
        self.entryCarrega = self.builder.get_object("entryCarrega")
        self.entryMescla = self.builder.get_object("entryMescla")
        self.entryPorcMescla = self.builder.get_object("entryPorcMescla")
        self.entryHumitat = self.builder.get_object("entryHumitat")
        self.entryPorcSilo1 = self.builder.get_object("entryPorcSilo1")
        self.entryPorcSilo2 = self.builder.get_object("entryPorcSilo2")
        self.entryPorcSilo1.set_text(str(self.porcSilo1))
        self.entryPorcSilo2.set_text(str(self.porcSilo2))        
        self.entryCascara1 = self.builder.get_object("entryCascara1")
        self.entryCascara2 = self.builder.get_object("entryCascara2")
        self.entryCascara3 = self.builder.get_object("entryCascara3")
        self.entryGra1 = self.builder.get_object("entryGra1")
        self.entryGra2 = self.builder.get_object("entryGra2")
        self.entryGra3 = self.builder.get_object("entryGra3")
        self.entryRendiment1 = self.builder.get_object("entryRendiment1")
        self.entryRendiment2 = self.builder.get_object("entryRendiment2")
        self.entryRendiment3 = self.builder.get_object("entryRendiment3")
        self.entryRendimentTotal = self.builder.get_object("entryRendimentTotal")
        self.entryTamany1 = self.builder.get_object("entryTamany1")
        self.entryTamany2 = self.builder.get_object("entryTamany2")
        self.entryTamany3 = self.builder.get_object("entryTamany3")
        self.entryPorcTamany1 = self.builder.get_object("entryPorcTamany1")
        self.entryPorcTamany2 = self.builder.get_object("entryPorcTamany2")
        self.entryPorcTamany3 = self.builder.get_object("entryPorcTamany3")
        self.entryObservacions = self.builder.get_object("entryObservacions")

        self.entryCarrega.modify_font(pango.FontDescription("sans bold 16"))
        self.entryMescla.modify_font(pango.FontDescription("sans bold 16"))
        self.entryPorcMescla.modify_font(pango.FontDescription("sans bold 16"))
        self.entryHumitat.modify_font(pango.FontDescription("sans bold 16"))        
        self.entryPorcSilo1.modify_font(pango.FontDescription("sans bold 16"))
        self.entryPorcSilo2.modify_font(pango.FontDescription("sans bold 16"))
        self.entryCascara1.modify_font(pango.FontDescription("sans bold 16"))
        self.entryCascara2.modify_font(pango.FontDescription("sans bold 16"))                        
        self.entryCascara3.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryGra1.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryGra2.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryGra3.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryRendiment1.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryRendiment2.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryRendiment3.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryRendimentTotal.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryTamany1.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryTamany2.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryTamany3.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryPorcTamany1.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryPorcTamany2.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryPorcTamany3.modify_font(pango.FontDescription("sans bold 16"))                               
        self.entryObservacions.modify_font(pango.FontDescription("sans 12"))

        if self.averiaBascula:
            self.entryCascara1.set_editable(True)
            self.entryCascara2.set_editable(True)
            self.entryCascara3.set_editable(True)
            self.entryGra1.set_editable(True)
            self.entryGra2.set_editable(True)
            self.entryGra3.set_editable(True)
            self.entryMescla.set_editable(True)
            self.entryTamany1.set_editable(True)
            self.entryTamany2.set_editable(True)            
            
        aux = self.silosList.get_iter_first()
        while aux <> None:
            if self.silosList.get_value(aux,1) == "Cap":
                self.comboboxSilo2.set_active_iter(aux)
                self.IdSilo2Selected = self.silosList.get_value(aux,0)
                break        
            else:
                aux = self.silosList.iter_next(aux)
                                                                                        
        self.buttonWizardValidate = self.builder.get_object("buttonWizardValidate")
        self.labelButtonValidate = self.builder.get_object("labelButtonValidate")
        
        self.buttonWizardValidate.set_sensitive(False)
        self.labelButtonValidate.set_label(\
                decorateString("Guardar i imprimir albarà","grey","20"))        
        
        Session.remove()
                        
        self.window.maximize()
        self.window.show()
        
    def entrySociChanged(self,widget):    
        self.filterSoci(widget)

    def filterSoci(self,widget): #@UnusedVariable
        session = Session()
        txtFilterSociNumero = self.entryFilterSociNumero.get_text()
        txtFilterSociNom = self.entryFilterSociNom.get_text()
            
        if txtFilterSociNumero <> "" or txtFilterSociNom <> ""  :
            self.socisList.clear()
            for instance in session.query(Soci).\
                filter(Soci.num_soci.contains(txtFilterSociNumero)).\
                filter(Soci.nom.contains(txtFilterSociNom)):                                                
                self.socisList.append([instance.id_soci,\
                                       instance.num_soci,\
                                       instance.CIF,instance.nom])
        elif txtFilterSociNumero == "" and txtFilterSociNom == "":
            self.socisList.clear()
        Session.remove()
        
    def cursorChangedSocis(self,widget): #@UnusedVariable
        session = Session()
        
        (treemodel, iterSelected) = self.treeSelectionSocis.get_selected() #@UnusedVariable
        self.IdSociSelected = self.socisList.get_value(iterSelected,0)
    
        txtSociNumeroSelected = session.query(Soci).\
            filter(Soci.id_soci==self.IdSociSelected).one().num_soci
        txtSociNomSelected = session.query(Soci).\
            filter(Soci.id_soci==self.IdSociSelected).one().nom    

        self.entrySelectedSociNumero.set_text(txtSociNumeroSelected)
        self.entrySelectedSociNom.set_text(txtSociNomSelected)

        # print list of properties of selected member
        self.propertiesList.clear()
        for pro  in session.query(Finca).\
            filter(Finca.id_soci==self.IdSociSelected):
            self.propertiesList.append([pro.id_finca,pro.nom_finca,pro.municipi,pro.terme,pro.poligon,pro.parcela,pro.area,pro.tipus])        

        # first property selected automaticly
        try:
            #txtSelectedPropertyDesc = session.query(Finca).\ 
            #    filter(Finca.id_soci==self.IdSociSelected).first().nom_finca 
            self.IdPropertySelected = session.query(Finca).\
                filter(Finca.id_soci==self.IdSociSelected).first().id_finca
        except Exception as detail:
            self.logger.debug("Error selecting property of member")
            self.logger.debug("Error : " + str(detail))
            errorString = "Aquest soci no te finques assignades."
            self.errorWindow.openWindowError(errorString)
        
        Session.remove()
           
        self.checkConditionsToSave()


    def cursorChangedProperties(self,widget): #@UnusedVariable
        # Revisar codi
        (treemodel, iterSelected) = self.treeSelectionProperties.get_selected() #@UnusedVariable
        self.IdPropertySelected = self.propertiesList.get_value(iterSelected,0)
        #self.logger.debug("Finca seleccionada amb id: " + str(self.IdPropertySelected))

        self.checkConditionsToSave()
                        
    def changedVarietat(self,widget): #@UnusedVariable
        try:
            iterSelected = self.comboboxVarietat.get_active_iter()
            self.IdVarietatSelected = self.varietatsList.get_value(iterSelected,0)
        except:
            self.windowAux.openWindowError("No heu introduit un valor valid")
        else:
            self.checkConditionsToSave()
            
    def changedSilo1(self,widget): #@UnusedVariable
        try:    
            iterSelected = self.comboboxSilo1.get_active_iter()
            self.IdSilo1Selected = self.silosList.get_value(iterSelected,0)
        except:
            self.windowAux.openWindowError("No heu introduit un valor valid")
        else:
            self.checkConditionsToSave()
            
    def changedSilo2(self,widget): #@UnusedVariable
        try:    
            iterSelected = self.comboboxSilo2.get_active_iter()
            self.IdSilo2Selected = self.silosList.get_value(iterSelected,0)
        except:
            self.windowAux.openWindowError("No heu introduit un valor valid")

    def changedCarrega(self,widget): #@UnusedVariable
        if self.entryCarrega.get_text() <> '':
            try:    
                self.carrega = int(self.entryCarrega.get_text())
            except:
                self.windowAux.openWindowError("EL valor introduit no es correcte")
            else:
                self.checkConditionsToSave()
                        
    def changedHumitat(self,widget): #@UnusedVariable
        if self.entryHumitat.get_text() <> '':
            try:    
                self.humitat = decimal.Decimal(self.entryHumitat.get_text()).quantize(decimal.Decimal('0.1'))
            except:
                self.windowAux.openWindowError("EL valor introduit no es correcte")
            else:
                self.checkConditionsToSave()
            
    def changedPorcSilo1(self,widget): #@UnusedVariable
        if self.entryPorcSilo1.get_text() <> '':
            try:    
                self.porcSilo1 = int(self.entryPorcSilo1.get_text())
            except:
                self.windowAux.openWindowError("EL valor introduit no es correcte")

    def changedPorcSilo2(self,widget): #@UnusedVariable
        if self.entryPorcSilo2.get_text() <> '':
            try:    
                self.porcSilo2 = int(self.entryPorcSilo2.get_text())
            except:
                self.windowAux.openWindowError("EL valor introduit no es correcte")

    def changedTR(self,widget): #@UnusedVariable
        try:    
            iterSelected = self.comboboxTR.get_active_iter()
            self.trSelected = self.trList.get_value(iterSelected,1)
        except:
            self.windowAux.openWindowError("No heu introduit un valor valid")
        else:
            self.checkConditionsToSave()

    def captureMescla(self,widget): #@UnusedVariable
        try:
            self.grsMescla = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryMescla.set_text(str(self.grsMescla))
            self.calculateMescla()
            self.checkConditionsToSave()

    def calculateMescla(self): #@UnusedVariable
        if self.gra1 <> 0.0 :
            self.mescla = int(self.grsMescla*100.0/\
                           (self.gra1 + self.gra2 + self.gra3))
            self.entryPorcMescla.set_text(str(self.mescla))
            
    def captureCascara1(self,widget): #@UnusedVariable        
        try:
            self.cascara1 = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryCascara1.set_text(str(self.cascara1))
            self.calculateRendiment1()
            self.checkConditionsToSave()
                                  
    def captureCascara2(self,widget): #@UnusedVariable
        try:
            self.cascara2 = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryCascara2.set_text(str(self.cascara2))
            self.calculateRendiment2()

    def captureCascara3(self,widget): #@UnusedVariable
        try:
            self.cascara3 = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryCascara3.set_text(str(self.cascara3))
            self.calculateRendiment3()

    def captureGra1(self,widget): #@UnusedVariable
        try:
            self.gra1 = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryGra1.set_text(str(self.gra1))
            self.calculateRendiment1()
            self.calculateMescla()
            self.checkConditionsToSave()
            
    def captureGra2(self,widget): #@UnusedVariable
        try:
            self.gra2 = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryGra2.set_text(str(self.gra2))
            self.calculateRendiment2()
            self.calculateMescla()

    def captureGra3(self,widget): #@UnusedVariable
        try:
            self.gra3 = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryGra3.set_text(str(self.gra3))
            self.calculateRendiment3()
            self.calculateMescla()

    def captureTamany1(self,widget): #@UnusedVariable
        try:
            self.tamany1 = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryTamany1.set_text(str(self.tamany1))
            self.calculateTamany3()
            
    def captureTamany2(self,widget): #@UnusedVariable
        try:
            self.tamany2 = self.scale.readWeight()
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryTamany2.set_text(str(self.tamany2))
            self.calculateTamany3()
            
    def calculateTamany3(self):
        try:
            aux = decimal.Decimal((self.gra1 + self.gra2 + self.gra3) \
                            - (self.tamany1 - self.tamany2)).\
                                quantize(decimal.Decimal('0.1'))
            self.tamany3 = float(aux)
        except Exception as detail:
            self.windowAux.openWindowError(str(detail))
        else:
            self.entryTamany3.set_text(str(self.tamany3))
            self.calculatePorcTamany()
            self.checkConditionsToSave()

    def calculatePorcTamany(self):
        total = self.tamany1 + self.tamany2 + self.tamany3
        if total <> 0.0:
            self.porcTamany1 = int((self.tamany1 / total)*100.0) 
            self.porcTamany2 = int((self.tamany2 / total)*100.0)
            self.porcTamany3 = int((self.tamany3 / total)*100.0)
            self.entryPorcTamany1.set_text(str(self.porcTamany1))
            self.entryPorcTamany2.set_text(str(self.porcTamany2))
            self.entryPorcTamany3.set_text(str(self.porcTamany3))        

    def readCascara1(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.cascara1 = float(self.entryCascara1.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateRendiment1()
                self.checkConditionsToSave()

    def readCascara2(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.cascara2 = float(self.entryCascara2.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateRendiment2()
                self.checkConditionsToSave()

    def readCascara3(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.cascara3 = float(self.entryCascara3.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateRendiment3()
                self.checkConditionsToSave()

    def readGra1(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.gra1 = float(self.entryGra1.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateRendiment1()
                self.calculateMescla()
                self.checkConditionsToSave()

    def readGra2(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.gra2 = float(self.entryGra2.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateRendiment2()
                self.calculateMescla()
                self.checkConditionsToSave()

    def readGra3(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.gra3 = float(self.entryGra3.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateRendiment3()
                self.calculateMescla()
                self.checkConditionsToSave()

    def readMescla(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.grsMescla = float(self.entryMescla.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateMescla()
                self.checkConditionsToSave()

    def readTamany1(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.tamany1 = float(self.entryTamany1.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateTamany3()
                self.checkConditionsToSave()

    def readTamany2(self,widget): #@UnusedVariable
        if self.averiaBascula:
            try:
                self.tamany2 = float(self.entryTamany2.get_text())                                                
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.calculateTamany3()
                self.checkConditionsToSave()

    def calculateRendiment1(self):
        if self.cascara1 <> 0.0:
            try:
                aux = (self.gra1 / self.cascara1) * 100.0
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.rendiment1 = float("{0:.2f}".format(aux))
                self.entryRendiment1.set_text(str(self.rendiment1))
                self.calculateRendimentTotal()
            
    def calculateRendiment2(self):
        if self.cascara2 <> 0.0:
            try:
                aux = (self.gra2 / self.cascara2) * 100.0
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.rendiment2 = float("{0:.2f}".format(aux))
                self.entryRendiment2.set_text(str(self.rendiment2))
                self.calculateRendimentTotal()
            
    def calculateRendiment3(self):
        if self.cascara3 <> 0.0:
            try:
                aux = (self.gra3 / self.cascara3) * 100.0
            except Exception as detail:
                self.windowAux.openWindowError(str(detail))
            else:
                self.rendiment3 = float("{0:.2f}".format(aux))
                self.entryRendiment3.set_text(str(self.rendiment3))
                self.calculateRendimentTotal()
            
    def calculateRendimentTotal(self):
        
        if self.rendiment1 <> 0.0 and self.rendiment2 == 0.0 and self.rendiment3 == 0.0 :
            self.rendimentTotal = self.rendiment1
        elif self.rendiment1 <> 0.0 and self.rendiment2 <> 0.0 and self.rendiment3 == 0.0 :
            aux = (self.rendiment1 + self.rendiment2) / 2.0
            self.rendimentTotal = float("{0:.2f}".format(aux))
        elif self.rendiment1 <> 0.0 and self.rendiment2 <> 0.0 and self.rendiment3 <> 0.0 :
            aux = (self.rendiment1 + self.rendiment2 + self.rendiment3) / 3.0
            self.rendimentTotal = float("{0:.2f}".format(aux))

        self.entryRendimentTotal.set_text(str(self.rendimentTotal))

        self.checkConditionsToSave()          
        
    def checkConditionsToSave(self):
        if not self.garrofa and self.IdSociSelected <> None and \
                    self.IdPropertySelected <> None and \
                     self.rendimentTotal <> 0.0 and \
                     self.carrega <> 0 and self.humitat <> 0 and \
                     self.cascara1 <> 0 and self.gra1 <> 0 and \
                     self.IdVarietatSelected <> None and self.IdSilo1Selected <> None and \
                     (self.tamany1 <> 0 or self.tamany2 <> 0) and \
                     self.trSelected <> None :
            self.buttonWizardValidate.set_sensitive(True)
            self.labelButtonValidate.set_label(\
                decorateString("Guardar i imprimir albarà","black","20"))            
            
        if self.garrofa and self.IdSociSelected <> None and \
                    self.IdPropertySelected <> None and \
                     self.carrega <> 0 and self.humitat <> 0 and \
                    self.IdVarietatSelected <> None and self.IdSilo1Selected <> None and \
                    self.trSelected <> None :
            self.rendimentTotal = 100.0
            self.buttonWizardValidate.set_sensitive(True)
            self.labelButtonValidate.set_label(\
                decorateString("Guardar i imprimir albarà","black","20"))            

            
    def validateSelection(self,widget): #@UnusedVariable
        self.createNewAlbara()
        self.window.hide()

    def createNewAlbara(self):
        session = Session()
             
        id_soci = self.IdSociSelected
        id_finca = self.IdPropertySelected
        try:            
            #idUltimAlbara = session.query(func.max(cast(Albara.num_albara,NUMERIC))).one()[0]           
            #albara = session.query(Albara).filter_by(id_albara=idUltimAlbara).one()
            albara = session.query(Albara).order_by(desc(cast(Albara.num_albara,NUMERIC))).first()
            
        except Exception as detail:
            self.logger.info("No es troba num albara. Donem numero 1")            
            num_albara = 1                
        else:
            num_albara = int(albara.num_albara) + 1
            

        timestamp = datetime.now()    
        self.observacions = self.entryObservacions.get_text()
        
        new = Albara(num_albara,id_soci,timestamp,self.IdVarietatSelected,str(self.carrega),\
                     str(self.humitat),self.trSelected,str(self.mescla),self.IdSilo1Selected,\
                     str(self.porcSilo1),self.IdSilo2Selected,str(self.porcSilo2),\
                     str(self.cascara1),str(self.gra1),str(self.rendiment1),\
                     str(self.cascara2),str(self.gra2),str(self.rendiment2),\
                     str(self.cascara3),str(self.gra3),str(self.rendiment3),\
                     str(self.rendimentTotal),
                     str(self.tamany1),str(self.tamany2),str(self.tamany3),\
                     str(self.porcTamany1),str(self.porcTamany2),str(self.porcTamany3),\
                     self.observacions,\
                     id_finca)
        
        try:
            session.add(new)                            
            session.commit()
        except Exception as detail:
            self.logger.error("Error guardant albara en BBDD.")
            self.logger.error(str(detail))
            self.windowAux.openWindowError("Error guardant albara en BBDD.")
        else:
            idAlbara = new.getId()
            self.logger.debug("Nou albarà creat amb ID: " + str(idAlbara))
            self.parent.lastAlbara = new
            self.parent.updateLabels()
            self.printer.sendAlbara(idAlbara)
            copia = str(self.config.get("ticket","copia"))
            self.logger.debug("Copia: " + copia)
            if copia=="SI":
                self.logger.debug("Enviant copia...")
                self.printer.sendAlbara(idAlbara)
        
        Session.remove()
                
    def windowSelectionDestroy(self,widget): #@UnusedVariable
        self.window.destroy()

