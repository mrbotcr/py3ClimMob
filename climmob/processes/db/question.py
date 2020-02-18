from ...models import Question,Registry,mapToSchema,mapFromSchema,Qstoption, AssDetail
from sqlalchemy import func


__all__ = [
    'addQuestion',
    'addOptionToQuestion','updateQuestion',
    'deleteQuestion','UserQuestion','QuestionsOptions','getQuestionData',
    'getQuestionOptions','deleteOption','optionExists','getOptionData',
    'updateOption','questionExists'
]


def addQuestion(data,request):
    mappeData = mapToSchema(Question,data)
    newQuestion = Question(**mappeData)
    try:
        request.dbsession.add(newQuestion)
        request.dbsession.flush() ##Flush the session so we can get the last id created
        return True,newQuestion.question_id
    except Exception as e:
        return False,str(e)

def questionExists(user,code,request):
    inlocal = request.dbsession.query(Question).filter(Question.user_name == user).filter(Question.question_code == code).first()
    inglobal = request.dbsession.query(Question).filter(Question.user_name == 'bioversity').filter(Question.question_code == code).first()
    if inlocal is not None or inglobal is not None:
        return True
    return False

def addOptionToQuestion(data,request):
    mappeData = mapToSchema(Qstoption, data)
    max_id = request.dbsession.query(func.ifnull(func.max(Qstoption.value_order), 0).label("id_max")).one()
    mappeData["value_order"] = max_id.id_max + 1
    newQstoption= Qstoption(**mappeData)
    try:
        request.dbsession.add(newQstoption)
        request.dbsession.flush()
        return True,""
    except Exception as e:
        return False,str(e)

def updateOption(data,request):
    try:
        mappeData = mapToSchema(Qstoption, data)
        request.dbsession.query(Qstoption).filter(Qstoption.question_id ==data['question_id']).filter(Qstoption.value_code == data['value_code']).update(mappeData)
        return True,""
    except Exception as e:
        return False,str(e)

def updateQuestion(data,request):
    try:
        mappeData = mapToSchema(Question, data)
        request.dbsession.query(Question).filter(Question.user_name ==data['user_name']).filter(Question.question_id == data['question_id']).update(mappeData)
        return True,""
    except Exception as e:
        return False,str(e)

def deleteOption(id_question,value,request):
    try:
        request.dbsession.query(Qstoption).filter(Qstoption.question_id==id_question).filter(Qstoption.value_code==value).delete()
        return True,""
    except Exception as e:
        return False, str(e)

def deleteQuestion(data,request):
    try:
        request.dbsession.query(Question).filter(Question.question_id==data['question_id']).delete()
        return True,""
    except Exception as e:
        return False, str(e)


def UserQuestion(user, request):

    mappedData = mapFromSchema(request.dbsession.query(Question).filter(Question.user_name == user).filter(Question.question_visible == 1).all())
    result = []
    for data in mappedData:
        registry = request.dbsession.query(func.count(Registry.question_id).label("found")).filter(Registry.question_id == data['question_id']).one()
        assessment = request.dbsession.query(func.count(AssDetail.question_id).label("found")).filter(AssDetail.question_id == data['question_id']).one()
        data['assigned'] = assessment.found + registry.found
        if data['question_dtype'] == 5 or data['question_dtype'] == 6:
            options = getQuestionOptions(data['question_id'], request)
            data['num_options'] = len(options)
        result.append(data)
    return result

def QuestionsOptions(user,request):
    res = []
    subquery = request.dbsession.query(Question.question_id).filter(Question.user_name==user).filter(Question.question_dtype.in_([5,6]))
    result = mapFromSchema(request.dbsession.query(Qstoption).filter(Qstoption.question_id.in_(subquery)).all())
    return result
    # for option in result:
    #     res.append({"question_id":option.question_id,"value_code":option.value_code, "value_desc":option.value_desc.decode('utf8') })
    # return res

def getQuestionData(user,question,request):
    questionData = mapFromSchema(request.dbsession.query(Question).filter(Question.user_name == user,Question.question_id == question).first())
    if questionData:
        registry = request.dbsession.query(func.count(Registry.question_id).label("found")).filter(Registry.question_id == question).one()
        assessment = request.dbsession.query(func.count(AssDetail.question_id).label("found")).filter(AssDetail.question_id == question).one()
        total = assessment.found + registry.found
        questionData['assigned'] = total

        if total == 0:
            editable = True
        else:
            editable = False
    else:
        questionData = mapFromSchema(request.dbsession.query(Question).filter(Question.user_name == 'bioversity',Question.question_id == question).first())
        editable = False
    return questionData,editable

def getOptionData(question,value,request):
    questionData = mapFromSchema(request.dbsession.query(Qstoption).filter(Qstoption.question_id == question).filter(Qstoption.value_code == value).first())
    return questionData

def getQuestionOptions(question,request):
    return mapFromSchema(request.dbsession.query(Qstoption).filter(Qstoption.question_id == question).all())

def optionExists(question,option,request):
    res = request.dbsession.query(Qstoption).filter(Qstoption.question_id == question).filter(Qstoption.value_code == option).first()
    if res is None:
        return False
    return True

