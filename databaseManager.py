#!/usr/bin/python
# -*- coding: utf-8 -*-

#import MySQLdb as mdb
import mysql.connector as mdb
import subprocess
import ConfigParser
import os
import model
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

'''
Com fer backup i restore amb mysql i mysqldump
http://www.thewebhostinghero.com/tutorials/mysql-backup-and-restore.html
SET FOREIGN_KEY_CHECKS=0;
Com donar access a l'usuari pondusoil en la nova BBDD
http://kb.mediatemple.net/questions/788/HOWTO%3A+GRANT+privileges+in+MySQL#dv
GRANT SELECT, INSERT, DELETE ON database TO username@'localhost' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
'''

class DatabaseManager():
    def __init__(self,user,password,adminPassword,backupFolder="../backup"):
        self.user = user
        self.password = password
        self.adminPassword = adminPassword
        self.backupFolder = os.path.join("c:",backupFolder)

    def listDatabase(self):

        command = "mysqlshow"
        user='pondusnut'
        password=self.password   
        try: 
            subprocess.call(command+ ' -u '+user+" -p"+password,shell=True)
        except Exception:
            raise
        
    def backupDatabase(self,database):
        ''' Fa una copia de la BBDD en una carpeta determinada 
        i retorna el nom de l'arxiu'''    
        command = "mysqldump"
        user='root'
        password=self.adminPassword 
        try:   
            subprocess.call(command+" --add-drop-table -u"+user+" -p"+password+\
                    " --default-character-set=latin1"+\
                    " "+database+" > "+self.backupFolder+database+".bak.sql",shell=True)
        except:
            raise
        else:
            return folder+database+'.bak.sql'

    def safetyBackupDatabase(self,database):
        ''' Fa una copia de la BBDD en una carpeta determinada 
        i retorna el nom de l'arxiu'''    
        command = "mysqldump"
        user='root'
        password=self.adminPassword 
        try:   
            subprocess.call(command+" --add-drop-table -u"+user+" -p"+password+\
                    " --default-character-set=latin1"+\
                    " "+database+" > ./backup/copiaBBDDactual.bak.sql",shell=True)
        except:
            raise
        else:
            return 'copiaBBDDactual.bak.sql'

        
    def createDatabase(self,database):
        try:
            db=mdb.connect(user='root',passwd=self.adminPassword)
            c=db.cursor()
            c.execute('CREATE DATABASE '+ database + ' CHARACTER SET UTF8 COLLATE utf8_general_ci')
            c.execute('GRANT SELECT, INSERT, DELETE, CREATE ON '+ database+ '.* TO pondusnut@localhost IDENTIFIED BY "440885"')
        except:
            raise
        finally:
            db.close()

    def restoreDatabase(self,database,arxiu):
        
        command = "mysql"
        try:   
            subprocess.call(command+" -u root -p"+self.adminPassword+\
                      " --default-character-set=utf8 "+database+" < "+ arxiu,shell=True)
        except:
            raise
        else:
            try:
                db=mdb.connect(user='root',passwd=self.adminPassword)
                c=db.cursor()
                c.execute('GRANT ALL PRIVILEGES ON '+ database+ '.* TO pondusoil@localhost IDENTIFIED BY "440885"')
            except:
                raise
            finally:
                db.close()
        
    def deleteWeights(self,database):
        try:
            db=mdb.connect(user='root',passwd=self.adminPassword,db=database)
            c=db.cursor()
            c.execute('TRUNCATE TABLE partial_weights')
            c.execute('TRUNCATE TABLE weights')
        except:
            raise
        finally:
            db.close()

    def modifyUpdateTables(self,database):
        try:
            db=mdb.connect(user='pondusoil',passwd='440885')
            c=db.cursor()
            
            c.execute('ALTER TABLE '+ database + '.properties DROP FOREIGN KEY `fk_id_member2`')
            c.execute('ALTER TABLE '+ database + '.properties ADD CONSTRAINT `fk_id_member2` \
                FOREIGN KEY `fk_id_member2` (`id_member`)\
                REFERENCES `members` (`id_member`)\
                ON DELETE CASCADE\
                ON UPDATE CASCADE')

            c.execute('ALTER TABLE '+ database + '.partial_weights DROP FOREIGN KEY `fk_id_weight`')
            c.execute('ALTER TABLE '+ database + '.partial_weights ADD CONSTRAINT `fk_id_weight` \
                FOREIGN KEY `fk_id_weight` (`id_weight`)\
                REFERENCES `weights` (`id_weight`)\
                ON DELETE CASCADE\
                ON UPDATE CASCADE')
        except:
            raise
        finally:
            db.close()

    def executeSQLSentence(self,database,sentence):
        try:
            db=mdb.connect(user='pondusnut',passwd='440885')
            c=db.cursor()
        except:
            print "Error conectant amb MySQL. \n"
        else:
            try:
                c.execute('use ' + database + ';')
                c.execute(sentence)
                result=c.fetchall()
                db.commit()
            except Exception as detail:
                db.rollback()
                print 'Error executant sentencia SQL'
                print str(detail)
            else:
                print "sentencia executada correctament \r\n"
                print str(result)+"\n"
            finally:
                db.close()

    def createStructure(self,database):
        try:
            engine = create_engine('mysql+mysqldb://pondusnut:440885@localhost/pondusnut2012', pool_recycle=3600)
            Session = sessionmaker(bind=engine)
            session = Session() #@UnusedVariable
        except Exception as detail:
            print "Error creant engine.\n"
            print str(detail)+"\n"
        else:
            try:
                model.metadata.create_all(engine)            
            except Exception as detail:
                print "Error creant estructura.\n"
                print str(detail)+"\n"
            else:
                print "Estructura creada correctament.\n"    
                    
    def backupAndNewDatabase(self,database):
        print "Realizant copia de seguretat de la BBDD actual...\n\r"
        try:
            arxiu = self.backupDatabase(database)
        except:
            print "Error fent la copia de la BBDD actual"
        else:
            print "Copia de la BBDD actual realitzada en: " + arxiu + "\n\r"
        
        new_database = raw_input("Nom de la nova BBDD a crear:")
        try:
            self.createDatabase(new_database)
        except:
            print "Error creant la nova BBDD!\n\r"
        else:
            print "Nova BBDD creada amb exit!\n\r"
        
        print "Restaurant la copia de seguretat en la nova BBDD...\n\r"
        try:
            self.restoreDatabase(new_database,arxiu)
        except:
            print "Error restaurant la BBDD!\r\n"
        else:
            print " arxiu restaurat amb exit!"

        print "Actualitzant taules de la nova BBDD...\n\r"
                        
        try:
            self.modifyUpdateTables(new_database)
        except:
            print "Error modificant taules de la BBDD!\r\n"
        else:
            print " BBDD modificada amb exit!"

        print "Esborrant pesades antigues de la nova BBDD...\n\r"
        
        try:
            self.deleteWeights(new_database)
        except:
            print "Error esborrant les pesades!!\r\n"
        else:
            print "Pesades esborrades amb exit!\r\n"
            print "Ara nomes cal que actualitzeu el nou nom de la bbdd en arxiu de configuracio.\r\n"
        
        
def mainMenu():
    cmd = raw_input('\n\r\
0 -> SURT de l\'aplicacio \n\r\
\n\r\
1 -> LLISTA de les BBDD actuals \n\r\
2 -> COPIA de la base de dades actual \n\r\
3 -> COPIA de la base de dades qualsevol \n\r\
4 -> CREA una nova BBDD \n\r\
5 -> RESTAURA bbdd a partir d\'arxiu \n\r\
6 -> ESBORRA TOTES LES PESADES de la BBDD \n\r\
7 -> Modifica UPDATE de les taules FINQUES, PESADES, PESADES PARCIALS \n\r\
8 -> Executa sentencia SQL \n\r\
9 -> Crea estructura de la BBDD a partir del model \n\r\
\r\n\
10 -> Proces complet de copia de BBDD, restauracio amb nom nou i esborra pesades \n\r\
\n\r\
Introduiu comanda:')
    return cmd
            
if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read("configuracio.ini")

    user = config.get("BBDD","usuari")
    password = config.get("BBDD","contrasenya")
    databaseUsed = config.get("BBDD","basedades")
    server = config.get("BBDD","servidor")
    folder = config.get("BBDD","directori")
    
    manager = DatabaseManager(user,password,password,folder)
    
    while True:     
        command = mainMenu()
        
        if command == '1': # LLISTAT DE BBDD
            try:
                answer = manager.listDatabase()
            except Exception as error:
                print "Error: " + str(error)
            else:
                raw_input("\n Fi del llistat. \n")

        if command == '2': # COPIA DE BBDD actual
            database = config.get("BBDD","basedades")
            try:
                arxiu = manager.backupDatabase(database)
            except Exception as error:
                print "Error fent backup: " + str(error)
            else:
                raw_input("\n Copia realitzada en arxiu "+ arxiu + ". Premeu ENTER\n")

        if command == '3': # COPIA DE BBDD qualsevol
            database = raw_input("Entreu el nom de la BBDD a copiar:")
            try:
                arxiu = manager.backupDatabase(database)
            except Exception as error:
                print "Error fent backup: " + str(error)
            else:
                raw_input("\n Copia realitzada en arxiu "+ arxiu + ". Premeu ENTER\n")

        if command == '4': # CREA UNA NOVA BBDD
            database = raw_input("Entreu el nom de la BBDD a crear:")
            try:
                arxiu = manager.createDatabase(database)
            except Exception as error:
                print "Error creant la BBDD: " + str(error)
            else:
                raw_input("\n Base de dades creada. Premeu ENTER\n")

        if command == '5': # RESTAURA UNA BBDD DES DE ARXIU SQL
            sqlFiles = os.listdir(folder)
            if len(sqlFiles) == 0:
                print "No hi ha arxius per restaurar"
            else:
                i = 0 
                for i,sqlFile in enumerate(sqlFiles):             
                    print str(i) + " -> " + sqlFile + "\r" 
                iChosen = raw_input("Entreu el numero de l'arxiu a restaurar:")
                backupFile = sqlFiles[int(iChosen)]
                manager.listDatabase()
                database = raw_input("Entreu el nom de la BBDD en la que voleu restaurar l'arxiu:")                    
            try:
                manager.restoreDatabase(database, folder+backupFile)
            except Exception as error:
                print "Error restaurant la BBDD: " + str(error)
            else:
                raw_input("\n Base de dades restaurada. Premeu ENTER\n")

        if command == '6': # Esborra pesades
            try:
                answer = manager.listDatabase()
            except Exception as error:
                print "Error: " + str(error)
            else:
                database = raw_input("\nBase de dades a esborrar pesades:")
                try:
                    manager.deleteWeights(database)
                except:
                    print "Error esborrant pesades!\r\n"
                else:
                    print "Totes les pesades esborrades amb exit!\r\n"

        if command == '7': # Modifica UPDATE CASCADE
            try:
                answer = manager.listDatabase()
            except Exception as error:
                print "Error: " + str(error)
            else:
                database = raw_input("\nBase de dades a actualitzar taules:")
                try:
                    manager.modifyUpdateTables(database)
                except:
                    print "Error modificant taules\r\n"
                else:
                    print "Taules actualitzades amb exit!\r\n"

        if command == '8': # Executa Sentencia SQL
            try:
                answer = manager.listDatabase()
            except Exception as error:
                print "Error: " + str(error)
            else:
                database = raw_input("\nBase de dades on voleu executar sentencia SQL:")
                sentence = raw_input("\nSentencia SQL a executar:")
                try:
                    manager.executeSQLSentence(database, sentence)
                except:
                    print "Premeu ENTER per continuar\r\n"

        if command == '9': # Crea estructura BBDD
            answer = manager.listDatabase()
            database = raw_input("Entreu el nom de la BBDD on voleu crear estructura:")
            try:
                answer = manager.createStructure(database)
            except:
                print "Premeu ENTER per continuar\r\n"
            else:
                print "Premeu ENTER per continuar\r\n"
                
        if command == '10': # RESTAURA UNA BBDD DES DE ARXIU SQL
        
            manager.backupAndNewDatabase(databaseUsed)
        
        elif command == '0':
            print "\n Tancant aplicacio. \n"
            break
