# FastAPI: los imports son un framework para crear apis
# Depends: SE usa para inyectar unas dependecias (la conexion de base de datos en las rutas)
from fastapi import FastAPI, Depends

# CORSMiddleware: Permite que el backend acepte peticiones desde otros dominios
from fastapi.middleware.cors import CORSMiddleware

# create_engine: crea la conexión con la base de datps
# Colum, Integer, String: definen las columnas de las tablas
from sqlalchemy import create_engine, Column, Integer, String

# sessionmaker: fabrica de sesiones para interactuar con la base de datos
# Session: permite realizar operaciones con la base de datos
from sqlalchemy.orm import sessionmaker, Session

# declarative base: clase para definir modelos
from sqlalchemy.ext.declarative import declarative_base

# os: Para leer variables de entorno
import os

#*1. CONFIGURACIÓN DE BASE DE DATOS

# Railway nos dará una URL (DATABASE_URL) cuando despleguemos a producción
# Si estamos probando en local y no hay url, nos conectaremos a la base de datos XAMPP.
# Por defecto en XAMPP, el usuario es 'root', no hay cotraseña, el host es 'localhost' y la base de datos es 'mis_tareas_db'
DATABASE_URL = os.getenv("DATABASE_URL","mysql+pymysql://root@localhost/mis_tareas_db")

# Ajuste necesario para SQLalchemy si usamos MySQL en Railway
if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.REPLACE("mysql://","mysql+pymysql://",1)
        
# Ajuste por si tenemos PostgreSQL  en Railway
elif DATABASE_URL.startswith("postgress://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://","postgresql://",1)

# Crea el motor de conexión para la base de datos
engine = create_engine(DATABASE_URL)

# Define como se crean las sesiones de la base de datos (sin autocommits, sin autoflush)
# Consulta, no se llevará acabo de forma automática
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

# Base para definir los modelos
Base = declarative_base()

#* 2. MODELOS DE LA BASE DE DATOS

class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(Integer,primary_key=True,index=True)
    titulo = Column(String(50))
    descripcion = Column(String(255))
    
# Como en XAMPP no creamos la tabla hay que decirle que la cree
Base.metadata.create_all(bind=engine)

#* CONFIGURACIÓN DE LA APP (FAQSTAPI)
app = FastAPI()

#Permitir que nuestro front se ccomunique con nuestro back
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #Aqui va la dirección de vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para interactuar con la base de datos, para que el backend revise la tabla y haga las peticiones
def get_db():
    
    # Crea  una variable que se conecta con el motor de la base de datos
    db= SessionLocal()
    
    # Hace la consulta y finalmente cierra la consulta a la base de datos
    try:
        yield db
    finally:
        db.close()
        
#* RUTAS (ENDPOINTS)
@app.get("/")
def ruta_principal():
    return{"mensaje":"Backend funcionando a la perfección, ya casi nos vamos"}

@app.get("/tareas")
def obtener_tareas(db:Session=Depends(get_db)):
    return db.query(Tarea).all()

@app.post("/tareas")
def crear_tarea(titulo:str,descripcion:str,db:Session=Depends(get_db)):
    nueva_tarea = Tarea(titulo=titulo,descripcion=descripcion)
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)
    return nueva_tarea