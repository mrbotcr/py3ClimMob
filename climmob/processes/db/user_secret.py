from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from climmob.models import UserSecret

__all__ = [
    "create_user_secret",
    "get_user_secret",
    "update_user_secret",
    "delete_user_secret",
]


def create_user_secret(request, user_name: str, secret: str, two_fa_method: str):
    try:
        new_secret = UserSecret(
            user_name=user_name,
            secret=secret,
            two_fa_method=two_fa_method,  # Guardar el método
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        request.dbsession.add(new_secret)
        return {"success": True, "message": "Secret created successfully"}
    except SQLAlchemyError as e:
        request.dbsession.rollback()
        return {"success": False, "message": str(e)}


def get_user_secret(request, user_name: str):
    try:
        user_secret = (
            request.dbsession.query(UserSecret).filter_by(user_name=user_name).first()
        )
        if user_secret:
            return {"success": True, "data": user_secret}
        return {"success": False, "message": "User secret not found"}
    except SQLAlchemyError as e:
        return {"success": False, "message": str(e)}


def update_user_secret(
    request, user_name: str, new_secret: str = None, new_two_fa_method: str = None
):
    try:
        user_secret = (
            request.dbsession.query(UserSecret).filter_by(user_name=user_name).first()
        )
        if user_secret:
            if new_secret:
                user_secret.secret = new_secret
            if new_two_fa_method:
                user_secret.two_fa_method = new_two_fa_method
            user_secret.updated_at = datetime.now()
            return {"success": True, "message": "Secret updated successfully"}
        return {"success": False, "message": "User secret not found"}
    except SQLAlchemyError as e:
        request.dbsession.rollback()
        return {"success": False, "message": str(e)}


def delete_user_secret(request, user_name: str):
    try:
        user_secret = (
            request.dbsession.query(UserSecret).filter_by(user_name=user_name).first()
        )
        if user_secret:
            request.dbsession.delete(user_secret)
            return {"success": True, "message": "Secret deleted successfully"}
        return {"success": False, "message": "User secret not found"}
    except SQLAlchemyError as e:
        request.dbsession.rollback()
        return {"success": False, "message": str(e)}


def is_two_fa_configured(request, user_name: str):
    try:
        user_secret = (
            request.dbsession.query(UserSecret).filter_by(user_name=user_name).first()
        )
        return user_secret is not None
    except Exception as e:
        request.dbsession.rollback()
        return False
