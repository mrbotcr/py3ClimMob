import hashlib
import paginate
from climmob.views.classes import privateView
from climmob.processes import search_affiliation


class SearchAffiliationView(privateView):
    def processView(self):

        self.returnRawViewResult = True

        q = self.request.params.get("q", "")
        current_page = self.request.params.get("page")

        if q == "":
            q = None

        if current_page is None:
            current_page = 1

        query_size = 10
        if q is not None:
            q = q.lower()
            query_result, total = search_affiliation(self.request, q, 0, query_size)
            if total > 0:
                collection = list(range(total))
                page = paginate.Page(collection, current_page, 10)
                query_result, total = search_affiliation(
                    self.request, q, page.first_item - 1, query_size
                )
                select2_result = []
                for result in query_result:
                    select2_result.append(
                        {
                            "id": result["affiliation_name"],
                            "text": result["affiliation_name"],
                        }
                    )
                with_pagination = False
                if page.page_count > 1:
                    with_pagination = True

                if not with_pagination:
                    return {"total": total, "results": select2_result}
                else:
                    return {
                        "total": total,
                        "results": select2_result,
                        "pagination": {"more": True},
                    }
            else:
                return {"total": 0, "results": []}
        else:
            return {"total": 0, "results": []}
