from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User
from app.core.rbac import ROLE_PERMISSIONS


def require_permission(
    permission: str,
) -> Callable:

    async def checker(
        user: User = Depends(
            get_current_user
        ),
    ) -> User:

        permissions = ROLE_PERMISSIONS.get(
            user.role,
            set(),
        )

        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

        return user

    return checker