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

class WindowAux(object):

    def __init__( self ):
        self.builder = gtk.Builder()
        self.builder.add_from_file("glade/auxiliar.glade")
        
        dic = { 
            "on_buttonDialogErrorOk_clicked" : self.closeWindowError,            
            "on_buttonDialogInfoOk_clicked" : self.closeWindowInfo
            }
        self.builder.connect_signals( dic )
        
        self.dialogError = self.builder.get_object("dialogError")
        self.labelErrorString = self.builder.get_object("labelErrorString")

        self.dialogInfo = self.builder.get_object("dialogInfo")
        self.labelInfoString = self.builder.get_object("labelInfoString")
        
    def openWindowError(self,errorString):
        self.labelErrorString.set_label("<span font=\"14\" weight=\"bold\">"+\
        errorString+"</span>") 
        self.dialogError.show()

    def closeWindowError(self,widget): #@UnusedVariable
        self.dialogError.hide()

    def openWindowInfo(self,message):
        self.labelInfoString.set_label("<span font=\"14\" weight=\"bold\">"+\
        message+"</span>") 
        self.dialogInfo.show()

    def closeWindowInfo(self,widget): #@UnusedVariable
        self.dialogInfo.hide()
                        
def decorateString(string,color,size):
    # return the same string using MARKUP
    
        new_string = "<span font=\"" + size + \
                "\" foreground=\"" + color + \
                "\" weight=\"bold\">" + string + "</span>"
    
        return new_string


