from ...models import Chat, mapToSchema, mapFromSchema
from sqlalchemy import func

__all__ = ["addChat", "readChatByUser", "counterChat"]


def addChat(data, request):
    mappedData = mapToSchema(Chat, data)
    newMessage = Chat(**mappedData)
    try:
        request.dbsession.add(newMessage)
        return True, ""
    except Exception as e:
        return False, str(e)


def counterChat(user, request):
    result = (
        request.dbsession.query(func.count(Chat.user_name).label("count"))
        .filter(Chat.user_name == user)
        .filter(Chat.chat_tofrom == 2)
        .filter(Chat.chat_read == 0)
        .first()
    )
    return result[0]


def readChatByUser(user, request):

    result = (
        request.dbsession.query(
            Chat.chat_date,
            Chat.user_name,
            Chat.chat_message,
            Chat.chat_send,
            Chat.chat_read,
            Chat.chat_tofrom,
        )
        .filter(Chat.user_name == user)
        .order_by(Chat.chat_date)
        .distinct()
        .all()
    )
    res = mapFromSchema(result)
    result = {}
    result["read"] = []
    result["unread"] = []
    for chat in res:

        if chat["chat_read"] == 1:
            result["read"].append(chat)
        else:
            if chat["chat_tofrom"] == 1:
                result["read"].append(chat)
            else:
                result["unread"].append(chat)

    updateChat(user, request)

    return result


def updateChat(user, request):
    try:
        request.dbsession.query(Chat).filter(Chat.user_name == user).filter(
            Chat.chat_tofrom == 2
        ).update({"chat_read": 1})
        return True, ""
    except Exception as e:
        return False, e
