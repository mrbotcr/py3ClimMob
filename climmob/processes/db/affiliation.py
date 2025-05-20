from sqlalchemy import or_

from climmob.models import Affiliation
from climmob.models.schema import mapFromSchema

__all__ = ["search_affiliation", "get_all_affiliations"]


def search_affiliation(request, q, query_from, query_size):
    query = q.replace("*", "")

    result = (
        request.dbsession.query(Affiliation)
        .filter(Affiliation.affiliation_name.ilike("%" + query + "%"))
        .offset(query_from)
        .limit(query_size)
        .all()
    )

    result2 = (
        request.dbsession.query(Affiliation)
        .filter(Affiliation.affiliation_name.ilike("%" + query + "%"))
        .all()
    )

    return mapFromSchema(result), len(result2)


def get_all_affiliations(request):

    result = mapFromSchema(
        request.dbsession.query(Affiliation)
        .order_by(Affiliation.affiliation_name)
        .all()
    )

    return result
