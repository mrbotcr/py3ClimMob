from pyramid.httpexceptions import HTTPFound
from .classes import privateView

from ..processes import getUserTechs,findTechInLibrary,addTechnology,getTechnology,updateTechnology,deleteTechnology

class technologies_view(privateView):
    def processView(self):
        #self.needJS("technologies")
        #self.needJS("datatables")
        #self.needCSS('datatables')
        #self.needCSS("sweet")
        #self.needJS("sweet")
        #self.needJS("delete")

        dataworking   = {}
        error_summary = {}

        return {
                    'activeUser': self.user,'dataworking': dataworking,'error_summary': error_summary,
                    'UserTechs': getUserTechs(self.user.login,self.request),
                    'ClimMobTechs': getUserTechs('bioversity',self.request)
                }


class newtechnology_view(privateView):
    def processView(self):
        error_summary = {}
        formdata = {}
        redirect = False
        formdata["tech_name"] = ""
        if (self.request.method == 'POST'):
            if 'btn_add_technology' in self.request.POST:

                formdata = self.getPostDict()
                formdata['user_name'] = self.user.login
                if formdata["tech_name"] != "":

                    formdata["user_name"] = "bioversity"
                    existInGenLibrary = findTechInLibrary(formdata,self.request)
                    if existInGenLibrary == False:

                        formdata['user_name'] = self.user.login
                        existInPersLibrary = findTechInLibrary(formdata,self.request)
                        if existInPersLibrary == False:
                            formdata["user_name"] = self.user.login
                            added, message = addTechnology(formdata, self.request)
                            if not added:
                                error_summary = {'dberror': message}
                            else:
                                redirect = True
                        else:
                            error_summary = {
                                'exists': self._("This technology already exists in your personal library")}
                    else:
                        error_summary = {'exists': self._("This technology already exists in the generic library")}
                else:
                    error_summary = {'nameempty': self._('You need to set values for the name')}

        if redirect:
            self.request.session.flash(self._('The technology was added successfully'))

        return {'activeUser': self.user, 'error_summary': error_summary, 'redirect': redirect,'formdata': self.decodeDict(formdata)}


class modifytechnology_view(privateView):
    def processView(self):
        formdata = {}
        formdata["tech_id"] =self.request.matchdict['technologyid']
        data = getTechnology(formdata,self.request)
        if self.request.method == 'GET':
            if not bool(data):
                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url('usertechnologies'))

        error_summary = {}
        redirect = False

        formdata["tech_name"] = data["tech_name"]

        if (self.request.method == 'POST'):
            if 'btn_modify_technology' in self.request.POST:

                formdata = self.getPostDict()
                formdata['user_name'] = self.user.login
                formdata["tech_id"] =self.request.matchdict['technologyid']

                if formdata["tech_name"] != "":

                    formdata["user_name"] = "bioversity"
                    existInGenLibrary = findTechInLibrary(formdata,self.request)
                    if existInGenLibrary == False:

                        formdata['user_name'] = self.user.login
                        existInPersLibrary = findTechInLibrary(formdata,self.request)
                        if existInPersLibrary == False:
                            formdata["user_name"] = self.user.login
                            update, message = updateTechnology(formdata, self.request)
                            if not update:
                                error_summary = {'dberror': message}
                            else:
                                redirect = True
                        else:
                            error_summary = {
                                'exists': self._("This technology already exists in your personal library")}
                    else:
                        error_summary = {'exists': self._("This technology already exists in the generic library")}
                else:
                    error_summary = {'nameempty': self._('You need to set values for the name')}

        if redirect:
            self.request.session.flash(self._('The technology was modified successfully'))

        return {'activeUser': self.user, 'error_summary': error_summary, 'redirect': redirect,'formdata': self.decodeDict(formdata)}


class deletetechnology_view(privateView):
    def processView(self):
        formdata = {}
        formdata["user_name"] = self.user.login
        formdata["tech_id"] =self.request.matchdict['technologyid']
        data = getTechnology(formdata,self.request)

        if self.request.method == 'GET':
            if data is None:
                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url('usertechnologies'))

        formdata["tech_name"]= data["tech_name"]
        error_summary = {}
        redirect = False

        if self.request.method == 'POST':

            dlt, message = deleteTechnology(formdata, self.request)

            if not dlt:
                error_summary = {'dberror': message}
                self.returnRawViewResult = True
                return {"status": 400, "error": message}
            else:
                self.returnRawViewResult = True
                return {"status": 200}

        if redirect:
            self.request.session.flash(self._('The technology was deleted successfully'))

        return {'activeUser': self.user, 'error_summary': error_summary,
                'redirect': redirect, 'formdata': formdata}