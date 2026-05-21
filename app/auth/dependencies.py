from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from app.models.enums import UserRole
from app.db.session import get_db
from app.repositories.user_repo import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_user_by_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"leeway": 60}
        )

        user_id: int = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token"
            )
        
            
        
        repo = UserRepository(db)
        user = await repo.get_by_id(int(user_id))

        if not user:
            raise HTTPException(status_code=404, detail="user not found")

        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token"
        )



async def get_current_user(token:str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    return await get_user_by_token(token, db)
    
async def get_admin_user(current_user = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, 
            detail="Admin only"
        )
    
    return current_user