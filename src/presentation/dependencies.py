"""FastAPI dependencies for authentication and role-based access."""

from fastapi import HTTPException, Request

from src.models.user import User
from src.services.auth_service import auth_service


def get_current_user(request: Request) -> User:
    """Return the logged-in user or redirect unauthenticated visitors to /login."""
    session_user = request.session.get("user")
    if not session_user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    user = auth_service.get_user_by_username(session_user.get("username", ""))
    if user is None:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user


def require_role(*roles):
    """Dependency factory that allows only the given roles, else redirect to /dashboard."""

    def dependency(request: Request) -> User:
        user = get_current_user(request)
        if user.role not in roles:
            raise HTTPException(status_code=303, headers={"Location": "/dashboard"})
        return user

    return dependency
