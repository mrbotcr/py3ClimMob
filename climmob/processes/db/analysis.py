from climmob.models.schema import mapFromSchema,mapToSchema
from climmob.models import AssDetail,Asssection,Assessment,Question, Regsection, Registry
from climmob.processes.db.project import numberOfCombinationsForTheProject
from sqlalchemy import or_
from jinja2 import Environment
import json
__all__ = [
    'getQuestionsByType','getQuestionsStructure'
]

def getQuestionsByType(user, project,request):
    data = []

    dic = {}
    dic["Characteristics"] = []
    dic["Performance"]     = []
    dic["Explanatory"]     = []

    sections = mapFromSchema(request.dbsession.query(Regsection).filter(Regsection.user_name == user).filter(Regsection.project_cod == project).all())
    for section in sections:

        questions = mapFromSchema(request.dbsession.query(Registry).filter(Registry.user_name == user).filter(Registry.project_cod == project).filter(Registry.section_id == section["section_id"]).all())
        for question in questions:
            questInfo = {}
            questionData = mapFromSchema(request.dbsession.query(Question).filter(Question.question_id == question["question_id"]).first())

            if questionData["question_dtype"] == 5:
                questInfo["name"] = questionData["question_desc"]
                questInfo["id"]   = questionData["question_id"]
                questInfo["vars"] = "REG_"+questionData['question_code'].lower()
                dic["Explanatory"].append(questInfo)

    #ASSESSMENTS
    assessments = mapFromSchema(request.dbsession.query(Assessment).filter(Assessment.user_name == user).filter(Assessment.project_cod == project).filter(or_(Assessment.ass_status == 1,Assessment.ass_status == 2)).all())
    for assessment in assessments:
        sections = mapFromSchema(request.dbsession.query(Asssection).filter(Asssection.user_name == user).filter(Asssection.project_cod == project).filter(Asssection.ass_cod == assessment["ass_cod"]).order_by(Asssection.section_order).all())
        numComb = numberOfCombinationsForTheProject(user, project, request)

        for section in sections:

            questions = mapFromSchema(request.dbsession.query(AssDetail).filter(AssDetail.user_name == user).filter(AssDetail.project_cod == project).filter(AssDetail.ass_cod == assessment["ass_cod"]).filter(AssDetail.section_id == section['section_id']).order_by(AssDetail.question_order).all())
            for question in questions:
                questInfo = {}
                questionData = mapFromSchema(request.dbsession.query(Question).filter(Question.question_id == question["question_id"]).first())

                if questionData["question_dtype"] == 9 or questionData["question_dtype"] == 10:

                    questInfo["name"] = questionData["question_desc"]
                    questInfo["id"]   = questionData["question_id"]
                    questInfo["vars"] = []
                    if questionData["question_dtype"] == 9:

                        if numComb == 2:
                            varsData = {}
                            varsData["name"] = "ASS"+assessment["ass_cod"]+ "_char_" +questionData['question_code'].lower()
                            questInfo["vars"].append(varsData)

                        if numComb == 3:
                            varsData = {}
                            # The possitive
                            varsData["name"] = "ASS"+assessment["ass_cod"] + "_char_" + questionData['question_code'].lower() + "_pos"
                            questInfo["vars"].append(varsData)

                            varsData = {}
                            # The negative
                            varsData["name"] = "ASS"+assessment["ass_cod"] + "_char_" + questionData['question_code'].lower() + "_neg"
                            questInfo["vars"].append(varsData)

                        if numComb >= 4:
                            for opt in range(0, numComb):
                                varsData = {}
                                varsData["name"] =  "ASS"+assessment["ass_cod"] + "_char_" + questionData["question_code"].lower() + "_stmt_" + str(opt + 1)
                                questInfo["vars"].append(varsData)

                        dic["Characteristics"].append(questInfo)

                    if questionData["question_dtype"] == 10:
                        for opt in range(0, numComb):
                            varsData = {}
                            varsData["name"] = "ASS"+assessment["ass_cod"] + "_perf_" + questionData['question_code'].lower() + "_" + str(opt + 1)
                            questInfo["vars"].append(varsData)

                        dic["Performance"].append(questInfo)



    return dic

def getQuestionsStructure(user,project,ass_cod,request):
    data = []

    dic = []

    sections = mapFromSchema(request.dbsession.query(Asssection).filter(Asssection.user_name == user).filter(
        Asssection.project_cod == project).filter(Asssection.ass_cod == ass_cod).order_by(
        Asssection.section_order).all())
    numComb = numberOfCombinationsForTheProject(user, project, request)

    for section in sections:

        questions = mapFromSchema(request.dbsession.query(AssDetail).filter(AssDetail.user_name == user).filter(
            AssDetail.project_cod == project).filter(AssDetail.ass_cod == ass_cod).filter(
            AssDetail.section_id == section['section_id']).order_by(AssDetail.question_order).all())
        for question in questions:
            questInfo = {}
            questionData = mapFromSchema(
                request.dbsession.query(Question).filter(Question.question_id == question["question_id"]).first())

            if questionData["question_dtype"] == 9 or questionData["question_dtype"] == 10:

                questInfo["name"] = questionData["question_desc"]
                questInfo["id"] = questionData["question_id"]
                questInfo["vars"] = []
                if questionData["question_dtype"] == 9:

                    if numComb == 2:
                        varsData = {}
                        varsData["name"] = "char_" + questionData['question_code']
                        varsData["validation"] = ""
                        questInfo["vars"].append(varsData)

                    if numComb == 3:
                        varsData = {}
                        # The possitive
                        varsData["name"]       = "char_" + questionData['question_code'] + "_pos"
                        varsData["validation"] = "char_" + questionData['question_code'] + "_neg"
                        questInfo["vars"].append(varsData)

                        varsData = {}
                        # The negative
                        varsData["name"]       = "char_" + questionData['question_code'] + "_neg"
                        varsData["validation"] = "char_" + questionData['question_code'] + "_pos"
                        questInfo["vars"].append(varsData)

                    if numComb >= 4:
                        for opt in range(0, numComb):
                            #--------------#
                            validationString = ""
                            for optval in range(0, numComb):

                                if str(opt + 1) != str(optval + 1):
                                    validationString += "char_" + questionData["question_code"] + "_stmt_" + str(optval + 1)+"*****"
                            #--------------#
                            varsData = {}
                            varsData["name"]       = "char_" + questionData["question_code"] + "_stmt_" + str(opt + 1)
                            varsData["validation"] = validationString[:len(validationString)-5]
                            questInfo["vars"].append(varsData)

                    dic.append(questInfo)

                if questionData["question_dtype"] == 10:
                    for opt in range(0, numComb):
                        varsData = {}
                        varsData["name"]       = "perf_" + questionData['question_code'] + "_" + str(opt + 1)
                        varsData["validation"] = ""
                        questInfo["vars"].append(varsData)

                    dic.append(questInfo)
            else:
                questInfo["name"] = questionData["question_desc"]
                questInfo["id"] = questionData["question_id"]
                questInfo["vars"] = [{"name":questionData['question_code'],"validation":""}]

                dic.append(questInfo)
    return dic