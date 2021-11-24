from ..classes import privateView
from ...processes import (
    getActiveProject,
    projectExists,
    query_for_users,
    getTheProjectIdForOwner,
    add_project_collaborator,
    get_collaborators_in_project,
    remove_collaborator,
)
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import paginate
import urllib
import hashlib


class projectShare_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        error_summary = {}

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )

        activeProject = getActiveProject(self.user.login, self.request)
        if activeProject["project_template"] == 1:
            self.returnRawViewResult = True
            return HTTPFound(
                location=self.request.route_url(
                    "dashboard",
                    _query={
                        "user": activeProjectUser,
                        "project": activeProjectCod,
                    },
                )
            )

        if self.request.method == "POST":
            dataworking = self.getPostDict()
            dataworking["project_id"] = activeProjectId

            if "btnShareProject" in dataworking.keys():
                added, error = add_project_collaborator(self.request, dataworking)

                if added:
                    self.request.session.flash(
                        self._("The project was successfully shared with the user")
                    )
                else:
                    error_summary = {"dberror": error}

        return {
            "usersCollaborators": get_collaborators_in_project(
                self.request, activeProjectId
            ),
            "activeProject": activeProject,
            "error_summary": error_summary,
        }


class API_users_view(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()

        activeProjectId = getTheProjectIdForOwner(
            activeProjectUser, activeProjectCod, self.request
        )

        self.returnRawViewResult = True

        q = self.request.params.get("q", "")
        include_me = self.request.params.get("include_me", "False")
        current_page = self.request.params.get("page")

        if include_me == "False":
            include_me = False
        else:
            include_me = True
        if q == "":
            q = None

        if current_page is None:
            current_page = 1

        query_size = 10
        if q is not None:
            q = q.lower()
            query_result, total = query_for_users(
                self.request, q, 0, query_size, activeProjectId
            )
            if total > 0:
                collection = list(range(total))
                page = paginate.Page(collection, current_page, 10)
                query_result, total = query_for_users(
                    self.request, q, page.first_item - 1, query_size, activeProjectId
                )
                select2_result = []
                for result in query_result:
                    if result["user_name"] != self.user.login:
                        default = "identicon"
                        size = 45
                        gravatar_url = (
                            "http://www.gravatar.com/avatar/"
                            + hashlib.md5(
                                result["user_email"].lower().encode("utf8")
                            ).hexdigest()
                            + "?"
                        )
                        gravatar_url += urllib.parse.urlencode(
                            {"d": default, "s": str(size)}
                        )
                        select2_result.append(
                            {
                                "id": result["user_name"],
                                "text": result["user_name"]
                                + " - "
                                + result["user_fullname"],
                                "user_email": result["user_email"],
                                "gravatar": gravatar_url,
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


class removeprojectShare_view(privateView):
    def processView(self):

        collaborator = self.request.matchdict["collaborator"]
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            if self.request.method == "POST":
                deleted, message = remove_collaborator(
                    self.request, activeProjectId, collaborator, self
                )
                if not deleted:
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    self.returnRawViewResult = True
                    return {"status": 200}

        return {}
