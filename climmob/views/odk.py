from .classes import odkView,publicView
from ..processes import isEnumeratorActive,getEnumeratorPassword,getFormList,getXMLForm,\
    isEnumeratorinProject,getManifest,getMediaFile,storeSubmission,getAssessmentXMLForm,\
    getAssessmentManifest,getAssessmentMediaFile
from pyramid.response import Response



class formList_view(odkView):
    def processView(self):
        userid = self.request.matchdict['userid']
        if isEnumeratorActive(userid,self.user,self.request):
            if self.authorize(getEnumeratorPassword(userid,self.user,self.request)):
                return self.createXMLResponse(getFormList(userid,self.user,self.request))
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


class push_view(odkView):
    def processView(self):
        if self.request.method == "POST":
            userid = self.request.matchdict['userid']
            if isEnumeratorActive(userid, self.user, self.request):
                if self.authorize(getEnumeratorPassword(userid, self.user, self.request)):
                    stored,error = storeSubmission(userid,self.user,self.request)
                    print ("********************77")
                    print (stored)
                    print (error)
                    print ("********************77")
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

class submission_view(odkView):
    def processView(self):
        userid = self.request.matchdict['userid']
        if self.request.method == 'HEAD':
            if isEnumeratorActive(userid,self.user,self.request):
                headers = [('Location', self.request.route_url('odkpush', userid=userid))]
                response = Response(headerlist=headers, status=204)
                return response
            else:
                return self.askForCredentials()
        else:
            response = Response(status=404)
            return response

class XMLForm_view(odkView):
    def processView(self):
        projectid = self.request.matchdict['projectid']
        userid = self.request.matchdict['userid']
        if isEnumeratorinProject(userid,projectid,self.user,self.request):
            if self.authorize(getEnumeratorPassword(userid,self.user,self.request)):
                return getXMLForm(userid,projectid,self.request)
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()

class assessmentXMLForm_view(odkView):
    def processView(self):
        projectid = self.request.matchdict['projectid']
        userid = self.request.matchdict['userid']
        assessmentid = self.request.matchdict['assessmentid']
        if isEnumeratorinProject(userid,projectid,self.user,self.request):
            if self.authorize(getEnumeratorPassword(userid,self.user,self.request)):
                return getAssessmentXMLForm(userid,projectid,assessmentid,self.request)
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()

class manifest_view(odkView):
    def processView(self):
        projectid = self.request.matchdict['projectid']
        userid = self.request.matchdict['userid']
        if isEnumeratorinProject(userid,projectid,self.user,self.request):
            if self.authorize(getEnumeratorPassword(userid,self.user,self.request)):
                return self.createXMLResponse(getManifest(userid,projectid,self.request))
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()

class assessmentManifest_view(odkView):
    def processView(self):
        projectid = self.request.matchdict['projectid']
        userid = self.request.matchdict['userid']
        assessmentid = self.request.matchdict['assessmentid']
        if isEnumeratorinProject(userid,projectid,self.user,self.request):
            if self.authorize(getEnumeratorPassword(userid,self.user,self.request)):
                return self.createXMLResponse(getAssessmentManifest(userid,projectid,assessmentid,self.request))
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()

class mediaFile_view(odkView):
    def processView(self):
        projectid = self.request.matchdict['projectid']
        userid = self.request.matchdict['userid']
        fileid = self.request.matchdict['fileid']
        if isEnumeratorActive(userid,self.user,self.request):
            if self.authorize(getEnumeratorPassword(userid,self.user,self.request)):
                return getMediaFile(userid,projectid,fileid,self.request)
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()

class assessmentMediaFile_view(odkView):
    def processView(self):
        projectid = self.request.matchdict['projectid']
        userid = self.request.matchdict['userid']
        fileid = self.request.matchdict['fileid']
        assessmentid = self.request.matchdict['assessmentid']
        if isEnumeratorActive(userid,self.user,self.request):
            if self.authorize(getEnumeratorPassword(userid,self.user,self.request)):
                return getAssessmentMediaFile(userid,projectid,assessmentid,fileid,self.request)
            else:
                return self.askForCredentials()
        else:
            return self.askForCredentials()


