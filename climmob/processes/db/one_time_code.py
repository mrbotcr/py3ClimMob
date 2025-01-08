import datetime
import secrets
from sqlalchemy.exc import SQLAlchemyError
from climmob.models import UserOneTimeCode


def generate_grouped_code(length=24, group_size=6):

    raw_code = secrets.token_hex(length // 2).upper()
    grouped_code = "-".join(
        [raw_code[i : i + group_size] for i in range(0, length, group_size)]
    )
    return grouped_code


def create_one_time_codes(request, user_name: str, count=6):
    try:
        codes = [
            UserOneTimeCode(
                user_name=user_name,
                code=generate_grouped_code(),
                created_at=datetime.datetime.now(),
            )
            for _ in range(count)
        ]

        request.dbsession.add_all(codes)
        request.dbsession.flush()

        return {"success": True, "message": f"{count} One-Time Codes created."}
    except SQLAlchemyError as e:
        request.dbsession.rollback()
        return {"success": False, "message": str(e)}


def get_active_codes(request, user_name: str):
    try:
        codes = (
            request.dbsession.query(UserOneTimeCode)
            .filter_by(user_name=user_name)
            .all()
        )
        return {"success": True, "data": codes}
    except SQLAlchemyError as e:
        return {"success": False, "message": str(e)}


def validate_and_consume_code(request, user_name: str, code: str):
    try:
        one_time_code = (
            request.dbsession.query(UserOneTimeCode)
            .filter_by(user_name=user_name, code=code)
            .first()
        )
        if not one_time_code:
            return {"success": False, "message": "Invalid or expired code."}

        request.dbsession.delete(one_time_code)
        request.dbsession.flush()
        return {"success": True, "message": "Code validated and consumed."}
    except SQLAlchemyError as e:
        request.dbsession.rollback()
        return {"success": False, "message": str(e)}


def delete_all_codes(request, user_name: str):
    try:
        request.dbsession.query(UserOneTimeCode).filter_by(user_name=user_name).delete()
        request.dbsession.flush()
        return {"success": True, "message": "All codes deleted."}
    except SQLAlchemyError as e:
        request.dbsession.rollback()
        return {"success": False, "message": str(e)}
