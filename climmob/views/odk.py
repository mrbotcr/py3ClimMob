from pyramid.response import Response

from climmob.processes import (
    isEnumeratorActive,
    getEnumeratorPassword,
    getFormList,
    getXMLForm,
    isEnumeratorinProject,
    getManifest,
    getMediaFile,
    storeSubmission,
    getAssessmentXMLForm,
    getAssessmentManifest,
    getAssessmentMediaFile,
    getTheProjectIdForOwner,
    isEnumeratorAssigned,
)
from climmob.views.classes import odkView


class FormlistView(odkView):
    def processView(self):
        userid = self.request.matchdict["userid"]
        if isEnumeratorActive(userid, self.user, self.request):
            if self.authorize(getEnumeratorPassword(userid, self.user, self.request)):
                return self.createXMLResponse(
                    getFormList(userid, self.user, self.request)
                )
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


class FormListByProjectView(odkView):
    def processView(self):
        userOwner = self.request.matchdict["user"]
        projectCod = self.request.matchdict["project"]
        userCollaborator = self.request.matchdict["collaborator"]
        if isEnumeratorActive(userCollaborator, self.user, self.request):
            if self.authorize(
                getEnumeratorPassword(userCollaborator, self.user, self.request)
            ):
                return self.createXMLResponse(
                    getFormList(
                        userCollaborator,
                        self.user,
                        self.request,
                        userOwner=userOwner,
                        projectCod=projectCod,
                    )
                )
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


class PushView(odkView):
    def processView(self):
        if self.request.method == "POST":
            userid = self.request.matchdict["userid"]
            if isEnumeratorActive(userid, self.user, self.request):
                if self.authorize(
                    getEnumeratorPassword(userid, self.user, self.request)
                ):
                    stored, error = storeSubmission(userid, self.user, self.request)
                    print("********************77")
                    print(stored)
                    print(error)
                    print("********************77")
                    if stored:
                        response = Response(status=201)
                        return response
                    else:
                        response = Response(status=error)
                        return response
                else:
                    return self.askForCredentials()
            else:
                response = Response(status=401)
                return response
        else:
            response = Response(status=404)
            return response


class SubmissionView(odkView):
    def processView(self):
        userid = self.request.matchdict["userid"]
        if self.request.method == "HEAD":
            if isEnumeratorActive(userid, self.user, self.request):
                headers = [
                    ("Location", self.request.route_url("odkpush", userid=userid))
                ]
                response = Response(headerlist=headers, status=204)
                return response
            else:
                return self.askForCredentials()
        else:
            if self.request.method == "POST":
                if isEnumeratorActive(userid, self.user, self.request):
                    if self.authorize(
                        getEnumeratorPassword(userid, self.user, self.request)
                    ):
                        stored, error = storeSubmission(userid, self.user, self.request)
                        print("********************77")
                        print(stored)
                        print(error)
                        print("********************77")
                        if stored:
                            response = Response(status=201)
                            return response
                        else:
                            response = Response(status=error)
                            return response
                    else:
                        return self.askForCredentials()
                else:
                    response = Response(status=401)
                    return response
            else:
                response = Response(status=404)
                return response


class SubmissionByProjectView(odkView):
    def processView(self):
        userOwner = self.request.matchdict["user"]
        projectCod = self.request.matchdict["project"]
        userCollaborator = self.request.matchdict["collaborator"]
        if self.request.method == "HEAD":
            if isEnumeratorActive(userCollaborator, self.user, self.request):

                activeProjectId = getTheProjectIdForOwner(
                    userOwner, projectCod, self.request
                )
                if not isEnumeratorAssigned(
                    userCollaborator, activeProjectId, self.user, self.request
                ):
                    headers = [
                        (
                            "Location",
                            self.request.route_url("odkpush", userid=userCollaborator),
                        )
                    ]
                    response = Response(headerlist=headers, status=204)
                    return response
                else:
                    return self.askForCredentials()
            else:
                return self.askForCredentials()
        else:
            if self.request.method == "POST":
                if isEnumeratorActive(userCollaborator, self.user, self.request):
                    activeProjectId = getTheProjectIdForOwner(
                        userOwner, projectCod, self.request
                    )
                    if not isEnumeratorAssigned(
                        userCollaborator, activeProjectId, self.user, self.request
                    ):

                        if self.authorize(
                            getEnumeratorPassword(
                                userCollaborator, self.user, self.request
                            )
                        ):
                            stored, error = storeSubmission(
                                userCollaborator, self.user, self.request
                            )
                            print("********************77")
                            print(stored)
                            print(error)
                            print("********************77")
                            if stored:
                                response = Response(status=201)
                                return response
                            else:
                                response = Response(status=error)
                                return response
                        else:
                            return self.askForCredentials()
                    else:
                        return self.askForCredentials()
                else:
                    response = Response(status=401)
                    return response
            else:
                response = Response(status=404)
                return response


class XMLFormView(odkView):
    def processView(self):
        user = self.request.matchdict["user"]
        projectUserOwner = self.request.matchdict["userowner"]
        projectCod = self.request.matchdict["project"]
        projectId = getTheProjectIdForOwner(projectUserOwner, projectCod, self.request)

        if isEnumeratorinProject(projectId, self.user, self.request):
            if self.authorize(getEnumeratorPassword(user, self.user, self.request)):
                return getXMLForm(projectUserOwner, projectId, projectCod, self.request)
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


class AssessmentXMLFormView(odkView):
    def processView(self):
        user = self.request.matchdict["user"]
        projectUserOwner = self.request.matchdict["userowner"]
        projectCod = self.request.matchdict["project"]
        projectId = getTheProjectIdForOwner(projectUserOwner, projectCod, self.request)
        assessmentid = self.request.matchdict["assessmentid"]

        if isEnumeratorinProject(projectId, self.user, self.request):
            if self.authorize(getEnumeratorPassword(user, self.user, self.request)):
                return getAssessmentXMLForm(
                    projectUserOwner, projectId, projectCod, assessmentid, self.request
                )
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


class ManifestView(odkView):
    def processView(self):
        user = self.request.matchdict["user"]
        projectUserOwner = self.request.matchdict["userowner"]
        projectCod = self.request.matchdict["project"]
        projectId = getTheProjectIdForOwner(projectUserOwner, projectCod, self.request)

        if isEnumeratorinProject(projectId, self.user, self.request):
            if self.authorize(getEnumeratorPassword(user, self.user, self.request)):
                return self.createXMLResponse(
                    getManifest(
                        user, projectUserOwner, projectId, projectCod, self.request
                    )
                )
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


class AssessmentManifestView(odkView):
    def processView(self):
        user = self.request.matchdict["user"]
        projectUserOwner = self.request.matchdict["userowner"]
        projectCod = self.request.matchdict["project"]
        projectId = getTheProjectIdForOwner(projectUserOwner, projectCod, self.request)
        assessmentid = self.request.matchdict["assessmentid"]

        if isEnumeratorinProject(projectId, self.user, self.request):
            if self.authorize(getEnumeratorPassword(user, self.user, self.request)):
                return self.createXMLResponse(
                    getAssessmentManifest(
                        user,
                        projectUserOwner,
                        projectId,
                        projectCod,
                        assessmentid,
                        self.request,
                    )
                )
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


class MediaFileView(odkView):
    def processView(self):
        user = self.request.matchdict["user"]
        projectUserOwner = self.request.matchdict["userowner"]
        projectCod = self.request.matchdict["project"]
        projectId = getTheProjectIdForOwner(projectUserOwner, projectCod, self.request)
        fileid = self.request.matchdict["fileid"]

        if isEnumeratorinProject(projectId, self.user, self.request):
            if self.authorize(getEnumeratorPassword(user, self.user, self.request)):
                return getMediaFile(
                    projectUserOwner, projectId, projectCod, fileid, self.request
                )
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


class AssessmentMediaFileView(odkView):
    def processView(self):
        user = self.request.matchdict["user"]
        projectUserOwner = self.request.matchdict["userowner"]
        projectCod = self.request.matchdict["project"]
        projectId = getTheProjectIdForOwner(projectUserOwner, projectCod, self.request)
        fileid = self.request.matchdict["fileid"]
        assessmentid = self.request.matchdict["assessmentid"]

        if isEnumeratorinProject(projectId, self.user, self.request):
            if self.authorize(getEnumeratorPassword(user, self.user, self.request)):
                return getAssessmentMediaFile(
                    projectUserOwner,
                    projectId,
                    projectCod,
                    assessmentid,
                    fileid,
                    self.request,
                )
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()
