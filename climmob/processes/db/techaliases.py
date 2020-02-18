from climmob.models.climmobv4 import Techalia, Prjalia
from sqlalchemy import func
from ...models.schema import mapFromSchema,mapToSchema

__all__ = [
    'getTechsAlias','findTechalias','addTechAlias','getAlias','updateAlias','removeAlias','existAlias','getAliasAssigned'
]

def getTechsAlias(idtech,request):
    res=[]
    result = request.dbsession.query(Techalia,request.dbsession.query(func.count(Prjalia.alias_id)).filter(Techalia.alias_id==Prjalia.alias_used).label("quantity")).filter(Techalia.tech_id==idtech).all()

    for techalias in result:
        res.append({"tech_id":techalias[0].tech_id,"alias_id":techalias[0].alias_id,'alias_name':techalias[0].alias_name,'quantity': techalias.quantity})

    return res

def findTechalias(data,request):
    if data["alias_id"] is None:
        result = request.dbsession.query(Techalia).filter(Techalia.tech_id==data['tech_id'], Techalia.alias_name==data['alias_name']).all()
    else:
        result = request.dbsession.query(Techalia).filter(Techalia.tech_id==data['tech_id'], Techalia.alias_name==data['alias_name'], Techalia.alias_id != data["alias_id"]).all()
    if not result:
        return False
    else:
        return result

def addTechAlias(data, request,_from=""):
    max_id = request.dbsession.query(func.ifnull(func.max(Techalia.alias_id),0).label("id_max")).one()
    data["alias_id"] = max_id.id_max+1
    mappedData = mapToSchema(Techalia,data)
    newTechalias = Techalia(**mappedData)
    try:
        request.dbsession.add(newTechalias)
        if _from=="":
            return True,""
        else:
            return True,getAlias(data,request)

    except Exception as e:
        return False,e

def getAlias(data, request):
    return mapFromSchema(request.dbsession.query(Techalia).filter(Techalia.alias_id ==data["alias_id"]).filter(Techalia.tech_id==data["tech_id"]).one())

def getAliasAssigned(data,request):
    result = request.dbsession.query(func.count(Prjalia.alias_id).label("quantity")).filter(Prjalia.project_cod == data["project_cod"]).filter(Prjalia.user_name == data["user_name"]).filter(Prjalia.alias_used == data["alias_id"]).filter(Prjalia.tech_used == data["tech_id"]).one()
    #print "_____________________________________________________44"
    #print result
    #print "_____________________________________________________44"
    if result.quantity == 0:
        return False
    else:
        return True

def existAlias(data, request):
    result = request.dbsession.query(Techalia).filter(Techalia.alias_id ==data["alias_id"]).filter(Techalia.tech_id==data["tech_id"]).all()

    if not result:
        return False
    else:
        return True

def updateAlias(data,request):
    try:
        mappedData = mapToSchema(Techalia, data)
        request.dbsession.query(Techalia).filter(Techalia.alias_id == data['alias_id']).update(mappedData)
        return True,""
    except Exception as e:
        return False,e

def removeAlias(data,request):
    try:
        request.dbsession.query(Techalia).filter(Techalia.alias_id == data['alias_id']).delete()
        return True,""
    except Exception as e:
        return False, e