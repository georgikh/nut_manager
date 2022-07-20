#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mysql import VARCHAR, DECIMAL, TIMESTAMP
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import MetaData

Base = declarative_base()
metadata = MetaData()

class Varietat(Base):
    __tablename__ = "varietats"

    id_varietat = Column(Integer, primary_key=True)
    desc_varietat = Column(VARCHAR(100))
    codi = Column(VARCHAR(10))
    
    albarans = relationship("Albara", backref="varietats",\
        cascade="all,delete",passive_updates=False)
        
    def __init__(self,desc_varietat,codi):
        self.desc_varietat = desc_varietat
        self.codi = codi
        
    def __repr__(self):
        return "Descripcio varietat : %s. Codi Varietat: %s." % self.desc_varietat,self.codi

class Soci(Base):
    __tablename__ = "socis"

    id_soci   =       Column(Integer, primary_key=True)
    num_soci =        Column(VARCHAR(6))
    CIF =             Column(VARCHAR(15))
    nom =             Column(VARCHAR(100))
    adressa =         Column(VARCHAR(100))
    ciutat =          Column(VARCHAR(45))
    CP =              Column(VARCHAR(6))
    provincia =       Column(VARCHAR(25))
    telefon =         Column(VARCHAR(45))
    telefon2 =        Column(VARCHAR(45))

    albarans = relationship("Albara", backref="socis",\
        cascade="all,delete",passive_updates=False)
        
    def __init__(self,num_soci,CIF,nom,adressa,ciutat,CP,provincia,telefon,telefon2):
        self.num_soci = num_soci
        self.CIF = CIF
        self.nom = nom
        self.adressa = adressa
        self.ciutat = ciutat
        self.CP = CP
        self.provincia = provincia
        self.telefon = telefon
        self.telefon2 = telefon2

class Silo(Base):
    __tablename__ = "silos"

    id_silo   = Column(Integer, primary_key=True)
    desc_silo = Column(VARCHAR(45))
            
    def __init__(self,desc_silo):
        self.desc_silo = desc_silo

    def __repr__(self):
        return "Descripcio silo : %s" % self.desc_silo

class Albara(Base):
    __tablename__ = "albarans"

    id_albara   = Column(Integer, primary_key=True)
    num_albara = Column(VARCHAR(10))
    id_soci = Column(Integer, ForeignKey('socis.id_soci'))
    timestamp = Column(TIMESTAMP)
    id_varietat = Column(Integer, ForeignKey('varietats.id_varietat'))             
    carga = Column(VARCHAR(10))
    humitat = Column(VARCHAR(10))
    tablilla_resultas = Column(VARCHAR(2))
    mescla = Column(Integer)
    id_silo_1 = Column(Integer, ForeignKey('silos.id_silo'))
    porc_silo_1 = Column(Integer)
    id_silo_2 = Column(Integer, ForeignKey('silos.id_silo'))
    porc_silo_2 = Column(Integer)
    grs_cascara_1 = Column(VARCHAR(10))
    grs_gra_1 = Column(VARCHAR(10))
    rendiment_1 = Column(VARCHAR(10))
    grs_cascara_2 = Column(VARCHAR(10))
    grs_gra_2 = Column(VARCHAR(10))
    rendiment_2 = Column(VARCHAR(10))
    grs_cascara_3 = Column(VARCHAR(10))
    grs_gra_3 = Column(VARCHAR(10))
    rendiment_3 = Column(VARCHAR(10))
    rendiment_total = Column(VARCHAR(10))
    grs_tamany_1 = Column(VARCHAR(10))
    grs_tamany_2 = Column(VARCHAR(10))
    grs_tamany_3 = Column(VARCHAR(10))
    porc_tamany_1 = Column(VARCHAR(10))
    porc_tamany_2 = Column(VARCHAR(10))
    porc_tamany_3 = Column(VARCHAR(10))
    observacions = Column(VARCHAR(100))
    id_finca = Column(Integer, ForeignKey('finques.id_finca'))

    silo_1 = relationship("Silo",primaryjoin="Silo.id_silo==Albara.id_silo_1")
    silo_2 = relationship("Silo",primaryjoin="Silo.id_silo==Albara.id_silo_2")
    
    def __init__(self,num_albara,id_soci,timestamp,id_varietat=0,\
                 carga=0,humitat=0,tablilla_resultas='',mescla=0,\
                 id_silo_1=0,porc_silo_1=0,id_silo_2=0,porc_silo_2=0,\
                 grs_cascara_1=0,grs_gra_1=0,rendiment_1=0,\
                 grs_cascara_2=0,grs_gra_2=0,rendiment_2=0,\
                 grs_cascara_3=0,grs_gra_3=0,rendiment_3=0,\
                 rendiment_total=0,\
                 grs_tamany_1=0.0,grs_tamany_2=0.0,grs_tamany_3=0.0,\
                 porc_tamany_1=0,porc_tamany_2=0,porc_tamany_3=0,\
                 observacions='',\
                 id_finca=0):

        self.num_albara = num_albara
        self.id_soci = id_soci
        self.timestamp = timestamp
        self.id_varietat = id_varietat
        self.carga = carga
        self.humitat = humitat        
        self.tablilla_resultas = tablilla_resultas
        self.mescla = mescla
        self.id_silo_1 = id_silo_1
        self.porc_silo_1 = porc_silo_1
        self.id_silo_2 = id_silo_2
        self.porc_silo_2 = porc_silo_2 
        self.grs_cascara_1 = grs_cascara_1
        self.grs_gra_1 = grs_gra_1
        self.rendiment_1 = rendiment_1
        self.grs_cascara_2 = grs_cascara_2
        self.grs_gra_2 = grs_gra_2
        self.rendiment_2 = rendiment_2
        self.grs_cascara_3 = grs_cascara_3
        self.grs_gra_3 = grs_gra_3
        self.rendiment_3 = rendiment_3
        self.rendiment_total = rendiment_total
        self.grs_tamany_1 = grs_tamany_1
        self.grs_tamany_2 = grs_tamany_2
        self.grs_tamany_3 = grs_tamany_3
        self.porc_tamany_1 = porc_tamany_1
        self.porc_tamany_2 = porc_tamany_2
        self.porc_tamany_3 = porc_tamany_3
        self.observacions = observacions 
        self.id_finca = id_finca    
                        
    def getId(self):
        return self.id_albara

class Finca(Base):
    __tablename__ = "finques"

    id_finca   = Column(Integer, primary_key=True)    
    id_soci = Column(Integer, ForeignKey('socis.id_soci'))

    nom_finca = Column(VARCHAR(45))
    municipi = Column(VARCHAR(45))
    terme = Column(VARCHAR(45))
    poligon = Column(VARCHAR(45))
    parcela = Column(VARCHAR(45))
    #area = Column(DECIMAL(6,2))
    area = Column(VARCHAR(10))
    tipus = Column(VARCHAR(45))

    albarans = relationship("Albara", backref="finques",\
        cascade="all,delete",passive_updates=False)

    def __init__(self,id_soci,nom_finca,municipi,terme,poligon,parcela,area,tipus):
        self.id_soci = id_soci
        self.nom_finca = nom_finca
        self.municipi = municipi
        self.terme = terme
        self.poligon = poligon
        self.parcela = parcela
        self.area = area
        self.tipus = tipus
           
def mainMenu():
    cmd = raw_input('\
1 -> Crear estructura de la BBDD \n\r\
0 -> Sortir de l\'aplicacio\n\r\
Introduiu comanda:')
    return cmd

if __name__ == "__main__":
    import ConfigParser
    import logging.config
    import yaml
    
    config = ConfigParser.ConfigParser()
    config.read("configuracio.ini")
    
    configLog = yaml.safe_load(open('logging.yaml').read())
    logging.config.dictConfig(configLog)
    myLogger = logging.getLogger(__name__)
    loggingLevel = logging.getLogger().getEffectiveLevel()
    myLogger.info("Inicialitzant aplicacio... en nivell de log " + str(loggingLevel))

    # CONEXIO A LA BBDD 
    bbddType = config.get("BBDD","tipus")
    if bbddType == "mysql":        
        user = config.get("BBDD","usuari")
        password = config.get("BBDD","contrasenya")
        database = config.get("BBDD","basedades")
        server = config.get("BBDD","servidor")
        stringConnection = "mysql+mysqlconnector://" + str(user) + ":" + str(password) + \
                        "@" + str(server) + "/" + database
        myLogger.debug("Connecting to MYSQL Database using string: " + stringConnection)
        
    elif bbddType == "sqlite":
        arxiuSqlite = config.get("BBDD","arxiuSqlite")
        rutaSqlite = config.get("BBDD","rutaSqlite")
        #engine = create_engine(r'sqlite:///dades.db')
        #engine = create_engine(r'sqlite:///\\192.168.0.3\vc_TEMP\dades.db')

    while True:     
        command = mainMenu()
    
        if command == '1':
            try:
                if bbddType == "sqlite" and len(rutaSqlite)>0: 
                    engine = create_engine(r'sqlite:///' + rutaSqlite + arxiuSqlite)
                elif bbddType == "sqlite" and len(rutaSqlite)==0: 
                    engine = create_engine(r'sqlite:///' + arxiuSqlite)            
                elif bbddType == "mysql":
                    engine = create_engine(stringConnection, pool_recycle=3600)                 
                auxiliar = engine.execute("select 1").scalar()         
            except Exception as detail:
                myLogger.error("Error accedint a la BBDD: " + database)
                myLogger.error(str(detail))
            else:
                myLogger.debug("Enllac correcte amb la BBDD.")
                try:
                    Base.metadata.create_all(engine)
                except:
                    myLogger.error("Error creant la estructura de la BBDD.")
                    raise
                else:
                    myLogger.debug("Estructura BBDD creada correctament.")   
              
        elif command == '0':
            print "\n Tancant aplicacio \n"
            break


