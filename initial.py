#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

try:  
    import pygtk
    pygtk.require("2.0")  
except:  
    print("pyGTK 2.12 not Available")
    sys.exit(1)

import logging.config
import ConfigParser
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session


config = ConfigParser.ConfigParser()
config.read("configuracio.ini")

configLog = yaml.safe_load(open('logging.yaml').read())
logging.config.dictConfig(configLog)
myLogger = logging.getLogger(__name__)
loggingLevel = logging.getLogger().getEffectiveLevel()
myLogger.info("LOGGING en funcionament en nivell: "  + str(myLogger.getEffectiveLevel()))

# CONEXIO A LA BBDD 
bbddType = config.get("BBDD","tipus")
if bbddType == "mysql":        
    user = config.get("BBDD","usuari")
    password = config.get("BBDD","contrasenya")
    database = config.get("BBDD","basedades")
    server = config.get("BBDD","servidor")
    stringConnection = "mysql+mysqlconnector://" + str(user) + ":" + str(password) + \
       "@" + str(server) + "/" + database
    myLogger.info("Connecting to Database using string: " + stringConnection)
        
elif bbddType == "sqlite":
    arxiuSqlite = config.get("BBDD","arxiuSqlite")
    rutaSqlite = config.get("BBDD","rutaSqlite")
    #engine = create_engine(r'sqlite:///dades.db')
    #engine = create_engine(r'sqlite:///\\192.168.0.3\vc_TEMP\dades.db')      
    
try:
    if bbddType == "sqlite" and len(rutaSqlite)>0: 
        engine = create_engine(r'sqlite:///' + rutaSqlite + arxiuSqlite)
    elif bbddType == "sqlite" and len(rutaSqlite)==0: 
        engine = create_engine(r'sqlite:///' + arxiuSqlite)            
    elif bbddType == "mysql":
        engine = create_engine(stringConnection, pool_recycle=3600)                 
    auxiliar = engine.execute("select 1").scalar()
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
except Exception as detail:
    myLogger.error("Error accedint a la BBDD: " + database)
    myLogger.error(str(detail))
else:
    myLogger.debug("Inicializada BBDD correcta")

