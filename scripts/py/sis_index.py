from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from dotenv import load_dotenv

# Carga variables de entorno
load_dotenv()

# Obtiene URL con valor por defecto si no existe
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

app = FastAPI()

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
#SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(100))
    dni = Column(String(8), unique=True)
    role = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Configuración de templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "sis_index.html",
        {"request": request}
    )

@app.post("/api/register")
async def register_user(user_data: dict, db: Session = Depends(get_db)):
    # Validar que el DNI no sea usado como contraseña
    if user_data["password"] == user_data["dni"]:
        raise HTTPException(status_code=400, detail="La contraseña no puede ser igual al DNI")
    
    # Crear usuario
    db_user = User(
        email=user_data["email"],
        hashed_password=user_data["password"],  # En producción: hash la contraseña
        full_name=user_data["full_name"],
        dni=user_data["dni"],
        role=user_data["role"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Usuario registrado exitosamente"}

@app.post("/api/login")
async def login(credentials: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials["email"]).first()
    if not user or user.hashed_password != credentials["password"]:  # En producción: verificar hash
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"message": "Login exitoso"}

@app.get("/api/stats/{sede}")
async def get_stats(sede: str):
    # Simulación de datos de estadísticas
    stats = {
        "lima": {
            "inventariado": 75,
            "pendiente": 25,
            "total_activos": 1500
        },
        "arequipa": {
            "inventariado": 60,
            "pendiente": 40,
            "total_activos": 800
        },
        "trujillo": {
            "inventariado": 85,
            "pendiente": 15,
            "total_activos": 600
        }
    }
    return stats.get(sede.lower(), {"error": "Sede no encontrada"})

"""
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""