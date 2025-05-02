import hashlib
import paginate
from climmob.views.classes import privateView
from climmob.processes import search_affiliation


class SearchAffiliationView(privateView):
    def processView(self):
        self.returnRawViewResult = True
        try:
            q = self.request.params.get("q", "") or ""
            current_page = self.request.params.get("page")
            current_page = int(current_page) if current_page else 1

            query_size = 10
            q_lower = q.lower()

            query_result, total = search_affiliation(
                self.request, q_lower, 0, query_size
            )

            if total > 0:
                collection = list(range(total))
                page = paginate.Page(collection, current_page, query_size)
                query_result, total = search_affiliation(
                    self.request, q_lower, page.first_item - 1, query_size
                )
                select2_result = [
                    {"id": r["affiliation_name"], "text": r["affiliation_name"]}
                    for r in query_result
                ]
                more_pages = page.page_count > 1
                return {
                    "total": total,
                    "results": select2_result,
                    "pagination": {"more": more_pages},
                }
            else:
                return {"total": 0, "results": []}

        except Exception as e:
            import traceback

            traceback.print_exc()
            return {"total": 0, "results": [], "error": str(e)}
