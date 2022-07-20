#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
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

from model import Soci, Silo, Varietat, Finca
import vistaAux
from initial import Session

class WindowData(object):

    def __init__( self):
        myLogger = logging.getLogger(__name__)
        self.logger = myLogger
        self.builder = gtk.Builder()
        self.builder.add_from_file("glade/data.glade")

        self.windowData = self.builder.get_object("windowData")

        self.logger.debug("Obrint finestra de dades")
        self.iterSelected = None
        self.IdSelected = None
        session = Session()
        self.logger.debug("Iniciant session: " + str(session))
        self.windowAux = vistaAux.WindowAux()
        
        # editType 0=add 1=edit
        self.editType = 0
    
        dicData = { 
            "on_notebook_switch_page" : self.notebookSwitchPage,
            "on_buttonAddVarietat_clicked" : self.openWindowAdd,
            "on_buttonEditVarietat_clicked" : self.openWindowEdit,
            "on_buttonDeleteVarietat_clicked" : self.deleteElement,
            "on_buttonAddSilo_clicked" : self.openWindowAdd,
            "on_buttonEditSilo_clicked" : self.openWindowEdit,
            "on_buttonDeleteSilo_clicked" : self.deleteElement,
            "on_buttonAddSoci_clicked" : self.openWindowAddSoci,
            "on_buttonEditSoci_clicked" : self.openWindowEditSoci,
            "on_buttonDeleteSoci_clicked" : self.deleteElement,
            "on_buttonAddProperty_clicked" : self.openWindowAddProperty,
            "on_buttonEditProperty_clicked" : self.openWindowEditProperty,
            "on_buttonDeleteProperty_clicked" : self.deleteElement,
            "on_windowData_destroy" : self.windowDataDestroy,
            "on_treeviewProperties_cursor_changed" : self.cursorChanged,
            "on_treeviewPropertiesMembers_cursor_changed" : self.cursorPropertiesMembersChanged,           
            "on_treeviewVarietats_cursor_changed" : self.cursorChanged,
            "on_treeviewSilos_cursor_changed" : self.cursorChanged,
            "on_treeviewSocis_cursor_changed" : self.cursorChanged,
            "on_buttonSave_clicked" : self.saveEditData,
            "on_buttonCancel_clicked" : self.cancelEditData,
            "on_buttonSaveSoci_clicked" : self.saveEditData,
            "on_buttonCancelEditSoci_clicked" : self.cancelEditSoci,
            "on_buttonSaveEditProperty_clicked" : self.saveEditData,
            "on_buttonCancelEditProperty_clicked" : self.cancelEditProperty,
            "on_buttonSi_clicked" : self.confirmYes,
            "on_buttonNo_clicked" : self.confirmNo,
            "on_entryFilterSociNumero_changed" : self.filterSoci,
            "on_entryFilterSociNom_changed" : self.filterSoci,
            "on_entryFilterSociCif_changed" : self.filterSoci,
            "on_entryFilterPropertyMemberNumber_changed" : self.filterSoci,
            "on_entryFilterPropertyMemberName_changed" : self.filterSoci,
            "on_entryFilterPropertyMemberCif_changed" : self.filterSoci,
            "on_buttonCloseDataWindow_clicked":self.windowDataDestroy,
            "on_buttonCloseDataWindow1_clicked":self.windowDataDestroy,
            "on_buttonCloseDataWindow2_clicked":self.windowDataDestroy,
            "on_buttonCloseDataWindow3_clicked":self.windowDataDestroy,
            }
            
        self.builder.connect_signals( dicData )
    
        self.varietatsList = self.builder.get_object("liststoreVarietats")
        self.socisList = self.builder.get_object("liststoreSocis")
        self.silosList = self.builder.get_object("liststoreSilos")
        self.propertiesList = self.builder.get_object("liststoreProperties")

        for instance in session.query(Varietat):
            self.varietatsList.append([instance.id_varietat,instance.desc_varietat,instance.codi])

        for instance in session.query(Silo):
            self.silosList.append([instance.id_silo,instance.desc_silo])

        for instance in session.query(Soci):
            self.socisList.append([instance.id_soci,instance.num_soci,instance.CIF,instance.nom,instance.adressa, \
                                    instance.ciutat,instance.CP,instance.provincia,\
                                    instance.telefon,instance.telefon2])
                                    
        self.treeviewVarietats = self.builder.get_object("treeviewVarietats")
        self.treeSelectionVarietats = self.treeviewVarietats.get_selection()
        self.treeSelectionVarietats.set_mode(gtk.SELECTION_SINGLE)

        self.treeviewSilos = self.builder.get_object("treeviewSilos")
        self.treeSelectionSilos = self.treeviewSilos.get_selection()
        self.treeSelectionSilos.set_mode(gtk.SELECTION_SINGLE)
    
        self.treeviewSocis = self.builder.get_object("treeviewSocis")
        self.treeSelectionSocis = self.treeviewSocis.get_selection()
        self.treeSelectionSocis.set_mode(gtk.SELECTION_SINGLE)

        self.treeviewPropertiesMembers = self.builder.get_object("treeviewPropertiesMembers")
        self.treeSelectionPropertiesMembers = self.treeviewPropertiesMembers.get_selection()
        self.treeSelectionPropertiesMembers.set_mode(gtk.SELECTION_SINGLE)
         
        self.treeviewProperties = self.builder.get_object("treeviewProperties")
        self.treeSelectionProperties = self.treeviewProperties.get_selection()
        self.treeSelectionProperties.set_mode(gtk.SELECTION_SINGLE)
      
        self.buttonEditVarietat = self.builder.get_object("buttonEditVarietat")
        self.buttonDeleteVarietat = self.builder.get_object("buttonDeleteVarietat")
        self.buttonEditVarietat.set_sensitive(False)
        self.buttonDeleteVarietat.set_sensitive(False)

        self.buttonEditSilo = self.builder.get_object("buttonEditSilo")
        self.buttonDeleteSilo = self.builder.get_object("buttonDeleteSilo")
        self.buttonEditSilo.set_sensitive(False)
        self.buttonDeleteSilo.set_sensitive(False)

        self.buttonEditSoci = self.builder.get_object("buttonEditSoci")
        self.buttonDeleteSoci = self.builder.get_object("buttonDeleteSoci")
        self.buttonEditSoci.set_sensitive(False)
        self.buttonDeleteSoci.set_sensitive(False)
        
        self.buttonEditProperty = self.builder.get_object("buttonEditProperty")
        self.buttonAddProperty = self.builder.get_object("buttonAddProperty")
        self.buttonDeleteProperty = self.builder.get_object("buttonDeleteProperty")
        self.buttonAddProperty.set_sensitive(False)
        self.buttonEditProperty.set_sensitive(False)
        self.buttonDeleteProperty.set_sensitive(False)
              
        self.notebook = self.builder.get_object("notebook")
        self.currentPage = 0

        self.windowEditData = self.builder.get_object("windowEditData")
        self.windowEditSoci = self.builder.get_object("windowEditSoci")
        self.windowEditProperty = self.builder.get_object("windowEditProperty")
        
        self.entryFilterSociNumero = self.builder.get_object("entryFilterSociNumero")
        self.entryFilterSociNom = self.builder.get_object("entryFilterSociNom")
        self.entryFilterSociCif = self.builder.get_object("entryFilterSociCif")

        self.entryFilterPropertyMemberNumber = self.builder.get_object("entryFilterPropertyMemberNumber")
        self.entryFilterPropertyMemberName = self.builder.get_object("entryFilterPropertyMemberName")
        self.entryFilterPropertyMemberCif = self.builder.get_object("entryFilterPropertyMemberCif")
       
        Session.remove()
       
        self.windowData.maximize()
        try:        
            self.windowData.show()
        except:
            self.logger.error("Mostrant finestra de dades")
                    
    def notebookSwitchPage(self,notebook,page,page_num): #@UnusedVariable
        self.currentPage = page_num
        
        self.treeSelectionVarietats.unselect_all()
        self.treeSelectionSilos.unselect_all()
        self.treeSelectionSocis.unselect_all()
        self.treeSelectionProperties.unselect_all()
        
        self.buttonEditVarietat.set_sensitive(False)
        self.buttonDeleteVarietat.set_sensitive(False)
        self.buttonEditSilo.set_sensitive(False)
        self.buttonDeleteSilo.set_sensitive(False)
        self.buttonEditSoci.set_sensitive(False)
        self.buttonDeleteSoci.set_sensitive(False)
        self.buttonEditProperty.set_sensitive(False)
        self.buttonDeleteProperty.set_sensitive(False)
        
        self.entryFilterSociNumero.set_text("")
        self.entryFilterSociNom.set_text("")
        self.entryFilterSociCif.set_text("")

        self.entryFilterPropertyMemberNumber.set_text("")
        self.entryFilterPropertyMemberName.set_text("")
        self.entryFilterPropertyMemberCif.set_text("")
        
    def cursorChanged(self,widget): #@UnusedVariable
        if self.currentPage==0:
            self.buttonEditSoci.set_sensitive(True)
            self.buttonDeleteSoci.set_sensitive(True)
            (treemodel, self.iterSelected) = self.treeSelectionSocis.get_selected() #@UnusedVariable
            self.IdSelected = self.socisList.get_value(self.iterSelected,0)
        elif self.currentPage==1:
            self.buttonEditVarietat.set_sensitive(True)
            self.buttonDeleteVarietat.set_sensitive(True)
            (treemodel, self.iterSelected) = self.treeSelectionVarietats.get_selected() #@UnusedVariable
            self.IdSelected = self.varietatsList.get_value(self.iterSelected,0)
        elif self.currentPage==2:
            self.buttonEditSilo.set_sensitive(True)
            self.buttonDeleteSilo.set_sensitive(True)
            (treemodel, self.iterSelected) = self.treeSelectionSilos.get_selected() #@UnusedVariable
            self.IdSelected = self.silosList.get_value(self.iterSelected,0)
        elif self.currentPage==3: # FINQUES
            self.buttonEditProperty.set_sensitive(True)
            self.buttonDeleteProperty.set_sensitive(True)
            (treemodel, self.iterSelected) = self.treeSelectionProperties.get_selected() #@UnusedVariable
            self.IdSelected = self.propertiesList.get_value(self.iterSelected,0)
 
    def cursorPropertiesMembersChanged(self,widget): #@UnusedVariable
        
        session = Session()
        self.buttonEditProperty.set_sensitive(False)
        self.buttonDeleteProperty.set_sensitive(False)
        self.buttonAddProperty.set_sensitive(True)
                
        (treeselection, self.iterSelected) = self.treeSelectionPropertiesMembers.get_selected() #@UnusedVariable
        self.IdMemberSelected = self.socisList.get_value(self.iterSelected,0)
        
        self.propertiesList.clear()
        
        for pro in session.query(Finca).\
            filter(Finca.id_soci==self.IdMemberSelected):
            self.propertiesList.append([pro.id_finca,pro.nom_finca,pro.municipi,pro.terme,pro.poligon,\
                                  pro.parcela,str(pro.area),pro.tipus])
        
        Session.remove()
                       
    def openWindowAdd(self,widget): #@UnusedVariable
        self.editType = 0
        self.builder.get_object("entryDescription").set_text("")
        self.builder.get_object("entryCode").set_text("")
        self.windowEditData.show()

    def openWindowAddSoci(self,widget): #@UnusedVariable
        self.editType = 0
        self.builder.get_object("entrySociNumero").set_text("")
        self.builder.get_object("entrySociCif").set_text("")
        self.builder.get_object("entrySociNom").set_text("")
        self.builder.get_object("entrySociAdressa").set_text("")
        self.builder.get_object("entrySociCiutat").set_text("")
        self.builder.get_object("entrySociCp").set_text("")
        self.builder.get_object("entrySociProvincia").set_text("")
        self.builder.get_object("entrySociTelefon").set_text("")
        self.builder.get_object("entrySociTelefon2").set_text("")
        self.windowEditSoci.show()

    def openWindowAddProperty(self,widget): #@UnusedVariable
        self.editType = 0    # ADD MODE
        (treemodel, iterSelected) = self.treeviewPropertiesMembers.get_selection().get_selected()
       
        self.builder.get_object("entryPropertyMemberId").set_text(str(treemodel.get_value(iterSelected,0)))        
        self.builder.get_object("entryPropertyMemberNumber").set_text(treemodel.get_value(iterSelected,1))
        self.builder.get_object("entryPropertyMemberCif").set_text(treemodel.get_value(iterSelected,2))
        self.builder.get_object("entryPropertyMemberName").set_text(treemodel.get_value(iterSelected,3))
        self.builder.get_object("entryPropertyDescription").set_text("")
        self.builder.get_object("entryPropertyTown").set_text("")
        self.builder.get_object("entryPropertyDistrict").set_text("")
        self.builder.get_object("entryPropertyPoligon").set_text("")
        self.builder.get_object("entryPropertyParcel").set_text("")
        self.builder.get_object("entryPropertyArea").set_text("")
        self.builder.get_object("entryPropertyType").set_text("")
        self.windowEditProperty.show()
        
    def openWindowEdit(self,treeview):
        self.editType = 1
        (treemodel, iterSelected) = treeview.get_selection().get_selected()
        self.builder.get_object("entryDescription").set_text(treemodel.get_value(iterSelected,1))
        if self.currentPage == 1:
            self.builder.get_object("entryCode").set_text(treemodel.get_value(iterSelected,2))
        else:
            self.builder.get_object("entryCode").set_text("")
        self.windowEditData.show()

    def openWindowEditSoci(self,widgets): #@UnusedVariable
        self.editType = 1
        (treemodel, iterSelected) = self.treeviewSocis.get_selection().get_selected()

        self.builder.get_object("entrySociNumero").set_text(treemodel.get_value(iterSelected,1))

        if treemodel.get_value(iterSelected,2) is not None :
            self.builder.get_object("entrySociCif").set_text(treemodel.get_value(iterSelected,2))
        else:
            self.builder.get_object("entrySociCif").set_text("")
        if treemodel.get_value(iterSelected,3) is not None :
            self.builder.get_object("entrySociNom").set_text(treemodel.get_value(iterSelected,3))
        else:
            self.builder.get_object("entrySociNom").set_text("")
        if treemodel.get_value(iterSelected,4) is not None :
            self.builder.get_object("entrySociAdressa").set_text(treemodel.get_value(iterSelected,4))
        else:
            self.builder.get_object("entrySociAdressa").set_text("")
        if treemodel.get_value(iterSelected,5) is not None :
            self.builder.get_object("entrySociCiutat").set_text(treemodel.get_value(iterSelected,5))
        else:
            self.builder.get_object("entrySociCiutat").set_text("")
        if treemodel.get_value(iterSelected,6) is not None :
            self.builder.get_object("entrySociCp").set_text(treemodel.get_value(iterSelected,6))
        else:
            self.builder.get_object("entrySociCp").set_text("")
        if treemodel.get_value(iterSelected,7) is not None :
            self.builder.get_object("entrySociProvincia").set_text(treemodel.get_value(iterSelected,7))
        else:
            self.builder.get_object("entrySociProvincia").set_text("")
        if treemodel.get_value(iterSelected,8) is not None :
            self.builder.get_object("entrySociTelefon").set_text(treemodel.get_value(iterSelected,8))
        else:
            self.builder.get_object("entrySociTelefon").set_text("")
        if treemodel.get_value(iterSelected,9) is not None :
            self.builder.get_object("entrySociTelefon2").set_text(treemodel.get_value(iterSelected,9))
        else:
            self.builder.get_object("entrySociTelefon2").set_text("")
        self.windowEditSoci.show()


    def openWindowEditProperty(self,widgets): #@UnusedVariable
        self.editType = 1    # EDIT MODE
        (treemodelMembers, iterMemberSelected) = self.treeviewPropertiesMembers.get_selection().get_selected()
        (treemodelProperties, iterPropertySelected) = self.treeviewProperties.get_selection().get_selected()

        self.builder.get_object("entryPropertyMemberId").set_text(str(treemodelMembers.get_value(iterMemberSelected,0)))        
        self.builder.get_object("entryPropertyMemberNumber").set_text(treemodelMembers.get_value(iterMemberSelected,1))
        self.builder.get_object("entryPropertyMemberCif").set_text(treemodelMembers.get_value(iterMemberSelected,2))
        self.builder.get_object("entryPropertyMemberName").set_text(treemodelMembers.get_value(iterMemberSelected,3))
        self.builder.get_object("entryPropertyDescription").set_text(treemodelProperties.get_value(iterPropertySelected,1))
        if treemodelProperties.get_value(iterPropertySelected,2) is not None:
            self.builder.get_object("entryPropertyTown").set_text(treemodelProperties.get_value(iterPropertySelected,2))
        else:
            self.builder.get_object("entryPropertyTown").set_text("")            
        if treemodelProperties.get_value(iterPropertySelected,3) is not None:
            self.builder.get_object("entryPropertyDistrict").set_text(treemodelProperties.get_value(iterPropertySelected,3))
        else:
            self.builder.get_object("entryPropertyDistrict").set_text("")
        if treemodelProperties.get_value(iterPropertySelected,4) is not None:
            self.builder.get_object("entryPropertyPoligon").set_text(treemodelProperties.get_value(iterPropertySelected,4))
        else:
            self.builder.get_object("entryPropertyPoligon").set_text("")
        if treemodelProperties.get_value(iterPropertySelected,5) is not None:
            self.builder.get_object("entryPropertyParcel").set_text(treemodelProperties.get_value(iterPropertySelected,5))
        else:
            self.builder.get_object("entryPropertyParcel").set_text("")
        if treemodelProperties.get_value(iterPropertySelected,6) is not None:
            self.builder.get_object("entryPropertyArea").set_text(str(treemodelProperties.get_value(iterPropertySelected,6)))
        else:
            self.builder.get_object("entryPropertyArea").set_text("0")            
        if treemodelProperties.get_value(iterPropertySelected,7) is not None:
            self.builder.get_object("entryPropertyType").set_text(treemodelProperties.get_value(iterPropertySelected,7))
        else:
            self.builder.get_object("entryPropertyType").set_text("")            

        self.windowEditProperty.show()
        
    def cancelEditData(self,widget): #@UnusedVariable
        self.windowEditData.hide()

    def cancelEditSoci(self,widget): #@UnusedVariable
        self.windowEditSoci.hide()

    def cancelEditProperty(self,widget): #@UnusedVariable
        self.windowEditProperty.hide()
        
    def checkIfExists(self,component,text):
        session = Session()
        value = False
        if component == Varietat:
            for instance in session.query(component):
                if instance.desc_varietat == text or instance.codi == text:
                    value = True
                    break
        elif component == Silo:
            for instance in session.query(component):
                if instance.desc_silo == text :
                    value = True
                    break
        Session.remove()
        
        return value

    def saveEditData(self,widget): #@UnusedVariable
        
        session = Session()
        
        if self.currentPage == 0:    #  MEMBER
            if self.editType==0 :
                numero = self.builder.get_object("entrySociNumero").get_text()
                cif = self.builder.get_object("entrySociCif").get_text()
                nom = self.builder.get_object("entrySociNom").get_text()
                adressa = self.builder.get_object("entrySociAdressa").get_text()
                ciutat = self.builder.get_object("entrySociCiutat").get_text()
                cp = self.builder.get_object("entrySociCp").get_text()
                provincia = self.builder.get_object("entrySociProvincia").get_text()
                telefon = self.builder.get_object("entrySociTelefon").get_text()
                telefon2 = self.builder.get_object("entrySociTelefon2").get_text()

                new = Soci(numero,cif,nom,adressa,ciutat,cp,provincia,telefon,telefon2)
                session.add(new)
                
            elif self.editType==1 :
                numero = self.builder.get_object("entrySociNumero").get_text()
                cif = self.builder.get_object("entrySociCif").get_text()
                nom = self.builder.get_object("entrySociNom").get_text()
                adressa = self.builder.get_object("entrySociAdressa").get_text()
                ciutat = self.builder.get_object("entrySociCiutat").get_text()
                cp = self.builder.get_object("entrySociCp").get_text()
                provincia = self.builder.get_object("entrySociProvincia").get_text()
                telefon = self.builder.get_object("entrySociTelefon").get_text()
                telefon2 = self.builder.get_object("entrySociTelefon2").get_text()
                
                soci = session.query(Soci).filter_by(id_soci=self.IdSelected).one()
                soci.num_soci = numero
                soci.CIF = cif
                soci.nom = nom
                soci.adressa = adressa
                soci.ciutat = ciutat
                soci.CP = cp
                soci.provincia = provincia
                soci.telefon = telefon
                soci.telefon2 = telefon2
               
            try:        
                session.commit()    
            except:
                session.rollback()
                self.logger.error("Error gravant dades en BBDD")
                self.windowAux.openWindowError("No s'han pogut grabar les dades en la BBDD")
  
            self.socisList.clear()
            for instance in session.query(Soci):
                self.socisList.append([instance.id_soci,instance.num_soci,instance.CIF,instance.nom,\
                                    instance.adressa,instance.ciutat,instance.CP,instance.provincia,\
                                    instance.telefon,instance.telefon2])
            self.windowEditSoci.hide()

        elif self.currentPage == 3:    #  PROPERTY
            if self.editType==0 :    # ADD
                idMember =        int(self.builder.get_object("entryPropertyMemberId").get_text())            
                description =     self.builder.get_object("entryPropertyDescription").get_text()
                town =            self.builder.get_object("entryPropertyTown").get_text()
                district =        self.builder.get_object("entryPropertyDistrict").get_text()
                poligon =         self.builder.get_object("entryPropertyPoligon").get_text()
                parcel =          self.builder.get_object("entryPropertyParcel").get_text()
                try:
                    #area =        float(self.builder.get_object("entryPropertyArea").get_text())
                    area =        self.builder.get_object("entryPropertyArea").get_text()
                except:
                    area = "0.0"
                tipus =            self.builder.get_object("entryPropertyType").get_text()

                new = Finca(idMember,description,town,district,poligon,parcel,area,tipus)
                session.add(new)
                
            elif self.editType==1 :    # EDIT
                idMember =         int(self.builder.get_object("entryPropertyMemberId").get_text())            
                description =     self.builder.get_object("entryPropertyDescription").get_text()
                town =            self.builder.get_object("entryPropertyTown").get_text()
                district =        self.builder.get_object("entryPropertyDistrict").get_text()
                poligon =        self.builder.get_object("entryPropertyPoligon").get_text()
                parcel =        self.builder.get_object("entryPropertyParcel").get_text()
                try: 
                    area =      self.builder.get_object("entryPropertyArea").get_text()
                except:
                    area = "0.0"
                tipus =            self.builder.get_object("entryPropertyType").get_text()
                
                finca = session.query(Finca).filter_by(id_finca=self.IdSelected).one()
            
                finca.nom_finca = description
                finca.municipi = town            
                finca.terme = district
                finca.poligon = poligon
                finca.parcela = parcel
                try:
                    #finca.area = float(area)
                    finca.area = area
                except:
                    finca.area = "0.0"
                finca.tipus = tipus    

            try:    
                session.commit()    
            except IOError as error:
                session.rollback()
                self.logger.error("Error gravant dades en BBDD")
                self.windowAux.openWindowError("No s'han pogut grabar les dades en la BBDD: " + error)
                
            self.propertiesList.clear()        
            for pro in session.query(Finca).\
                filter(Finca.id_soci==self.IdMemberSelected):
                self.propertiesList.append([pro.id_finca,pro.nom_finca,pro.municipi,pro.terme,pro.poligon,\
                                    pro.parcela,str(pro.area),pro.tipus])
            self.windowEditProperty.hide()
    
        elif self.currentPage == 1:    #  Varietat
            if self.editType==0 :
                description = self.builder.get_object("entryDescription").get_text()
                code = self.builder.get_object("entryCode").get_text()
                if self.checkIfExists(Varietat,description) or self.checkIfExists(Varietat,code):
                    errorString = " Aquesta descripcio o codi ja existeixen!"
                    self.windowAux.openWindowError(errorString)   
                else:
                    new = Varietat(description,code)
                    session.add(new)
            elif self.editType==1 :
                txtDes = self.builder.get_object("entryDescription").get_text()
                txtCode = self.builder.get_object("entryCode").get_text()
                varietat = session.query(Varietat).filter_by(id_varietat=self.IdSelected).one()
                varietat.desc_varietat = txtDes
                varietat.codi = txtCode
            session.commit()    
            self.varietatsList.clear()
            for instance in session.query(Varietat):
                self.varietatsList.append([instance.id_varietat,instance.desc_varietat,instance.codi])
            self.windowEditData.hide()
    
        elif self.currentPage == 2:    #  SILO
            if self.editType==0 :
                description = self.builder.get_object("entryDescription").get_text()
                if self.checkIfExists(Silo,description):
                    errorString = " Aquesta descripcio ja existeix!"
                    self.windowAux.openWindowError(errorString)
                elif not self.checkIfExists(Silo,description):
                    new = Silo(description)
                    session.add(new)
            elif self.editType==1 :
                txtDes = self.builder.get_object("entryDescription").get_text()
                silo = session.query(Silo).filter_by(id_silo=self.IdSelected).one()
                silo.desc_silo = txtDes
            session.commit()    
            self.silosList.clear()
            for instance in session.query(Silo):
                self.silosList.append([instance.id_silo,instance.desc_silo])
            self.windowEditData.hide()
              
            self.windowEditProperty.hide()
                
        Session.remove()
        
    def deleteElement(self,widget): #@UnusedVariable
        self.builder.get_object("dialogConfirm").show()    
            
    def confirmYes(self,widget): #@UnusedVariable
        session = Session()
        if self.currentPage==0:            # Delete soci            
            Id = self.socisList.get_value(self.iterSelected,0)
            self.logger.debug("Deleting soci id: " + str(Id))
            try:        
                self.socisList.remove(self.iterSelected)
                session.query(Soci).filter(Soci.id_soci==Id).delete()
                session.commit()
            except Exception as detail:
                self.logger.error("Error Deleting soci id: " + str(Id))
                self.logger.error("Error detail: " + str(detail))
                errorString = "Error intentant esborrar algun element de la BBDD. Reviseu les dependencies."
                self.windowAux.openWindowError(errorString)
            self.builder.get_object("dialogConfirm").hide()
        elif self.currentPage==3:        # Delete property
            Id = self.propertiesList.get_value(self.iterSelected,0)
            self.logger.debug("Deleting property id: " + str(Id))
            try:
                self.propertiesList.remove(self.iterSelected)
                session.query(Finca).filter(Finca.id_finca==Id).delete()
                try:
                    session.commit()
                except:
                    session.rollback()
                    self.logger.error("Error gravant dades en BBDD")
                    self.windowAux.openWindowError("No s'han pogut grabar les dades en la BBDD")
            except Exception as detail:
                self.logger.error("ERROR deleting property id: " + str(Id))
                self.logger.error("Error detail: " + str(detail))
                errorString = "Error intentant esborrar algun element de la BBDD. Reviseu les dependencies."
                self.windowAux.openWindowError(errorString)
            self.builder.get_object("dialogConfirm").hide()
        elif self.currentPage==1:        # Delete varietat
            Id = self.varietatsList.get_value(self.iterSelected,0)
            try:
                self.varietatsList.remove(self.iterSelected)
                session.query(Varietat).filter(Varietat.id_varietat==Id).delete()
                session.commit()
            except:
                errorString = "Error intentant esborrar la varietat de la BBDD. Reviseu les dependencies."
                self.windowAux.openWindowError(errorString)
            self.builder.get_object("dialogConfirm").hide()                
        elif self.currentPage==2:        # Delete silo
            Id = self.silosList.get_value(self.iterSelected,0)
            try:
                self.silosList.remove(self.iterSelected)
                session.query(Silo).filter(Silo.id_silo==Id).delete()
                session.commit()
            except:
                errorString = "Error intentant esborrar el siloe de la BBDD. Reviseu les dependencies."
                self.windowAux.openWindowError(errorString)

            self.builder.get_object("dialogConfirm").hide()   
             
        Session.remove()    
            
    def confirmNo(self,widget): #@UnusedVariable      
        self.builder.get_object("dialogConfirm").hide()    
    
    def filterSoci(self,widget): #@UnusedVariable
        session = Session()
        if self.currentPage==0:
            txtFilterSociNumero = self.entryFilterSociNumero.get_text()
            txtFilterSociNom = self.entryFilterSociNom.get_text()
            txtFilterSociCif = self.entryFilterSociCif.get_text()
        elif self.currentPage==3:
            txtFilterSociNumero = self.entryFilterPropertyMemberNumber.get_text()
            txtFilterSociNom = self.entryFilterPropertyMemberName.get_text()
            txtFilterSociCif = self.entryFilterPropertyMemberCif.get_text()
            self.propertiesList.clear()
            
        if txtFilterSociNumero <> "" or txtFilterSociNom <> "" or txtFilterSociCif <> "" :
            self.socisList.clear()
            for instance in session.query(Soci).\
                filter(Soci.num_soci.contains(txtFilterSociNumero)).\
                filter(Soci.nom.contains(txtFilterSociNom)).\
                filter(Soci.CIF.contains(txtFilterSociCif)):                                                
                self.socisList.append([instance.id_soci,instance.num_soci,instance.CIF,instance.nom, \
                                    instance.adressa,instance.ciutat,instance.CP,instance.provincia, \
                                    instance.telefon,instance.telefon2])
        elif txtFilterSociNumero == "" and txtFilterSociNom == "" and txtFilterSociCif == "":
            self.socisList.clear()
            for instance in session.query(Soci):
                self.socisList.append([instance.id_soci,instance.num_soci,instance.CIF,instance.nom, \
                                    instance.adressa,instance.ciutat,instance.CP,instance.provincia,\
                                    instance.telefon,instance.telefon2])
        Session.remove()
                
    def filterProperty(self,widget):
    
        pass
                                    
    def windowDataDestroy(self,widget): #@UnusedVariable
        self.windowData.destroy()
        if __name__ == "__main__":
            print "Tanquem aplicacio"
            sys.exit(0)
                                    
if __name__ == "__main__":
    app = WindowData()
    gtk.main()



