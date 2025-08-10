from fastapi import Depends, HTTPException, status
from app import models
from app.dependencies import get_current_user # Changed import
from typing import List

def role_required(allowed_roles: List[models.Role]):
    async def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker