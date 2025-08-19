from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from passlib.hash import bcrypt

from v0 import login_user,get_object_by_alias,get_object_to_mesh,get_objects_to_mesh,get_meshes,publish_object_to_mesh,create_mesh,create_service,create_user,create_binding_object,execute_binding_object

app = FastAPI()

SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Modelo de entrada para login
class LoginRequest(BaseModel):
    username: str
    password: str

# Funciones de autenticación
def verify_password(password: str, hashed: str):
    return bcrypt.verify(password, hashed)

def create_access_token(user_data: dict, expires_delta: timedelta | None = None):
    to_encode = user_data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Login endpoint
@app.post("/login")
def login(data: LoginRequest):
    user = login_user(data.username, data.password)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    
    token = create_access_token({"sub": user.name, "id": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/meshes/create")
def create_mesh(current_user: str = Depends(get_current_user)):
    result = create_mesh()
    return result

@app.get("/objects",)
def get_objects(current_user: str = Depends(get_current_user)):
    # Lógica para obtener todos los objetos
    return {"objects": []}

@app.get("/objects/{alias}")
def get_objects_by_alias(alias: str, current_user: str = Depends(get_current_user)):
    result = get_object_by_alias(alias, current_user.user_id)
    return result

@app.post("/publish")
def publish(current_user: str = Depends(get_current_user)):
    # Lógica para publicar algo
    return {"message": f"Publicación realizada por {current_user}"}
