from sqlalchemy import or_

from climmob.models import Affiliation
from climmob.models.schema import mapFromSchema

__all__ = [
    "search_affiliation",
]


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
