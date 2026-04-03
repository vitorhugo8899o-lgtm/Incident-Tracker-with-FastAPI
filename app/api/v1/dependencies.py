from typing import Annotated
import jwt
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordBearer
from app.db.session import AsyncSessionLocal
from app.core.config import Settings
from app.models.users import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/Login", auto_error=False)
settings = Settings()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

DBSession = Annotated[AsyncSession, Depends(get_db)]

async def get_current_user(
        request: Request, 
        db: DBSession,
        header_token: str = Depends(oauth2_scheme)
    ) -> User:

    cookie_token = request.cookies.get("Login_info")
    
    token = cookie_token or header_token    
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado.")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # O sub virá como string "6"
        user_id_str: str = payload.get("sub")
        
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Token inválido")
            
        # Transformamos em int para o banco de dados
        user_id = int(user_id_str)
            
    except (jwt.PyJWTError, ValueError) as e:
        raise HTTPException(status_code=401, detail=f"Token inválido ou expirado {e}")
    # BUSCA POR ID: Muito mais rápido e direto
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")

    return user

CurrentUser = Annotated[User, Depends(get_current_user)]