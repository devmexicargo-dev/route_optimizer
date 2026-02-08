from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

# 👤 Usuarios definidos en código
USERS = {
    "asesor1": "clave123",
    "asesor2": "clave456",
    "jquiroag": "Rhuman851129",
    "admin": "admin123"
}

def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security)
):
    correct_password = USERS.get(credentials.username)

    if not correct_password or not secrets.compare_digest(
        credentials.password, correct_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
