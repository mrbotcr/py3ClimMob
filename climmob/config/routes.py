"""

These functions setup the routes for the host application and any plugins connected to it

"""

from ..views.basic_views import (
    home_view,
    notfound_view,
    login_view,
    register_view,
    logout_view,
    RecoverPasswordView,
)
from ..views.dashboard import dashboard_view, projectInformation_view
from ..views.profile import profile_view, editProfile_view
from ..views.project import (
    newProject_view,
    modifyProject_view,
    deleteProject_view,
    ProjectQRView,
)

from ..views.question import (
    qlibrary_view,
    categories_view,
    newQuestion_view,
    modifyQuestion_view,
    deleteQuestion_view,
    questionValues_view,
    addQuestionValue_view,
    modifyQuestionValue_view,
    deleteQuestionValue_view,
    questionCharacteristics_view,
    questionPerformance_view,
)

from ..views.registry import (
    registry_view,
    registryPreview_view,
    newRegistryQuestion_view,
    newRegistrySection_view,
    deleteRegistrySection_view,
    modifyRegistrySection_view,
    registryEnketo_view,
    cancelRegistry_view,
    closeRegistry_view,
)

from ..views.assessment import (
    assessment_view,
    assessmentPreview_view,
    newAssessmentQuestion_view,
    newAssessmentSection_view,
    deleteAssessmentSection_view,
    modifyAssessmentSection_view,
    assessmenthead_view,
    newassessmenthead_view,
    modifyassessmenthead_view,
    deleteassessmenthead_view,
    assessmentEnketo_view,
    startAssessments_view,
    closeAssessment_view,
    CancelAssessmentView,
)
from ..views.project_technologies import (
    projectTecnologies_view,
    prjTechAliases_view,
    prjTechAliasAdd_view,
    prjTechAliasDelete_view,
)
from ..views.enumerator import (
    enumerators_view,
    addEnumerator_view,
    modifyEnumerator_view,
    deleteEnumerator_view,
)
from ..views.project_combinations import projectCombinations_view
from ..views.odk import (
    formList_view,
    submission_view,
    XMLForm_view,
    manifest_view,
    mediaFile_view,
    push_view,
    assessmentXMLForm_view,
    assessmentMediaFile_view,
    assessmentManifest_view,
)

from ..views.project_enumerators import (
    projectEnumerators_view,
    addProjectEnumerators_view,
    removeProjectEnumerators_view,
)

from ..views.technologies import (
    technologies_view,
    newtechnology_view,
    modifytechnology_view,
    deletetechnology_view,
)
from ..views.techaliases import (
    alias_view,
    newalias_view,
    modifyalias_view,
    deletealias_view,
)

from ..views.test import test_view

from ..views.productsList import productsView, downloadView, downloadJsonView, dataView

from ..views.editData import editDataView, downloadDataView, uploadDataView

# -------Api-------#

from ..views.Api.projectCreation import (
    createProject_view,
    readProjects_view,
    updateProject_view,
    deleteProject_view_api,
)
from ..views.Api.enumerators import (
    createEnumerator_view,
    readEnumerators_view,
    updateEnumerator_view,
    updatePasswordEnumerator_view,
    apiDeleteEnumerator_view,
)
from ..views.Api.technologies import (
    createTechnology_view,
    readTechnologies_view,
    updateTechnology_view,
    deletetechnologyView_api,
)
from ..views.Api.techaliases import (
    createAlias_view,
    readAlias_view,
    updateAlias_view,
    deleteAliasView_api,
)
from ..views.Api.questions import (
    createQuestion_view,
    readQuestions_view,
    readQuestionValues_view,
    addQuestionValue_viewApi,
    updateQuestionValue_view,
    deleteQuestionValue_viewApi,
    updateQuestionCharacteristics_view,
    updateQuestionPerformance_view,
    updateQuestion_view,
    deleteQuestion_viewApi,
)

from ..views.Api.dashboard import readProjectDetails_view
from ..views.Api.projectEnumerators import (
    addProjectEnumerator_view,
    readProjectEnumerators_view,
    readPossibleProjectEnumerators_view,
    deleteProjectEnumerator_view,
)
from ..views.Api.projectTechnologies import (
    addProjectTechnology_view,
    readProjectTechnologies_view,
    readPossibleProjectTechnologies_view,
    deleteProjectTechnology_view,
    addProjectTechnologyAlias_view,
    readProjectTechnologiesAlias_view,
    readProjectTechnologiesAliasExtra_view,
    readPossibleProjectTechnologiesAlias_view,
    deleteProjectTechnologyAlias_view,
    addProjectTechnologyAliasExtra_view,
)
from ..views.Api.projectRegistry import (
    readProjectRegistry_view,
    readPossibleQuestionsForRegistryGroup_view,
    addRegistryGroup_view,
    updateRegistryGroup_view,
    deleteRegistryGroup_view,
    addQuestionToGroupRegistry_view,
    deleteQuestionFromGroupRegistry_view,
    orderRegistryQuestions_view,
)
from ..views.Api.projectRegistryStart import (
    readProjectCombinations_view,
    setUsableCombinations_view,
    createPackages_view,
    createProjectRegistry_view,
    cancelRegistryApi_view,
    closeRegistryApi_view,
    readRegistryStructure_view,
    pushJsonToRegistry_view,
)
from ..views.Api.projectProducts import readProducts_view, downloadApi_view
from ..views.Api.projectAssessments import (
    readProjectAssessments_view,
    addNewAssessment_view,
    updateProjectAssessment_view,
    deleteProjectAssessment_view,
    readProjectAssessmentStructure_view,
    createAssessmentGroup_view,
    updateAssessmentGroup_view,
    deleteAssessmentGroup_view,
    readPossibleQuestionForAssessmentGroup_view,
    addQuestionToGroupAssessment_view,
    deleteQuestionFromGroupAssessment_view,
    orderAssessmentQuestions_view,
)
from ..views.Api.projectAssessmentStart import (
    createProjectAssessment_view,
    cancelAssessmentApi_view,
    closeAssessmentApi_view,
    readAssessmentStructure_view,
    pushJsonToAssessment_view,
)
from ..views.Api.project_analysis import readDataOfProjectView_api

from ..views.project_analysis import analysisDataView
from ..plugins.utilities import addRoute
import climmob.plugins as p

route_list = []

# This function append or overrides the routes to the main list
def appendToRoutes(routeList):
    for new_route in routeList:
        found = False
        pos = 0
        for curr_route in route_list:
            if curr_route["path"] == new_route["path"]:
                found = True
        pos += 1
        if not found:
            route_list.append(new_route)
        else:
            route_list[pos]["name"] = new_route["name"]
            route_list[pos]["view"] = new_route["view"]
            route_list[pos]["renderer"] = new_route["renderer"]


def loadRoutes(config):

    # Custom mapping can happen here BEFORE the host maps
    for plugin in p.PluginImplementations(p.IRoutes):
        routes = plugin.before_mapping(config)
        appendToRoutes(routes)

    # These are the routes of the host application
    routes = []
    routes.append(
        {"name": "home", "path": "/", "view": home_view, "renderer": "landing.jinja2"}
    )
    routes.append(
        {
            "name": "login",
            "path": "/login",
            "view": login_view,
            "renderer": "login.jinja2",
        }
    )
    routes.append(
        {"name": "logout", "path": "/logout", "view": logout_view, "renderer": None}
    )

    # User routes
    routes.append(
        {
            "name": "register",
            "path": "/register",
            "view": register_view,
            "renderer": "register.jinja2",
        }
    )
    routes.append(
        {
            "name": "recover",
            "path": "/recover",
            "view": RecoverPasswordView,
            "renderer": "recover.jinja2",
        }
    )
    routes.append(
        {
            "name": "dashboard",
            "path": "/projects",
            "view": dashboard_view,
            "renderer": "dashboard/dashboard.jinja2",
        }
    )
    routes.append(
        {
            "name": "profile",
            "path": "/profile",
            "view": profile_view,
            "renderer": "dashboard/profile.jinja2",
        }
    )
    routes.append(
        {
            "name": "editprofile",
            "path": "/editprofile",
            "view": editProfile_view,
            "renderer": "dashboard/editprofile.jinja2",
        }
    )

    # Project routes
    routes.append(
        {
            "name": "newproject",
            "path": "/project/new",
            "view": newProject_view,
            "renderer": "project/newproject.jinja2",
        }
    )
    routes.append(
        {
            "name": "modifyproject",
            "path": "/project/{projectid}/edit",
            "view": modifyProject_view,
            "renderer": "project/modifyproject.jinja2",
        }
    )
    routes.append(
        {
            "name": "deleteproject",
            "path": "/project/{projectid}/delete",
            "view": deleteProject_view,
            "renderer": "project/deleteproject.jinja2",
        }
    )
    routes.append(
        {
            "name": "projectqr",
            "path": "/project/{projectid}/qr",
            "view": ProjectQRView,
            "renderer": None,
        }
    )

    # Question library
    routes.append(
        {
            "name": "qlibrary",
            "path": "/questions/{user_name}",
            "view": qlibrary_view,
            "renderer": "question/library.jinja2",
        }
    )
    routes.append(
        {
            "name": "categories",
            "path": "/categories",
            "view": categories_view,
            "renderer": "json",
        }
    )
    routes.append(
        {
            "name": "newquestion",
            "path": "/question/{category_id}/{category_user}/new",
            "view": newQuestion_view,
            "renderer": "question/newquestion.jinja2",
        }
    )
    routes.append(
        {
            "name": "questionvalues",
            "path": "/question/{qid}/values",
            "view": questionValues_view,
            "renderer": "question/questionvalues.jinja2",
        }
    )
    routes.append(
        {
            "name": "questioncharacteristics",
            "path": "/question/{qid}/characteristics",
            "view": questionCharacteristics_view,
            "renderer": "question/questioncharacteristics.jinja2",
        }
    )
    routes.append(
        {
            "name": "questionperformance",
            "path": "/question/{qid}/performance",
            "view": questionPerformance_view,
            "renderer": "question/questionperformance.jinja2",
        }
    )

    routes.append(
        {
            "name": "addquestionvalue",
            "path": "/question/{qid}/value/add",
            "view": addQuestionValue_view,
            "renderer": "question/addquestionvalue.jinja2",
        }
    )
    routes.append(
        {
            "name": "editquestionvalue",
            "path": "/question/{qid}/value/{valueid}/edit",
            "view": modifyQuestionValue_view,
            "renderer": "question/editquestionvalue.jinja2",
        }
    )
    routes.append(
        {
            "name": "deletequestionvalue",
            "path": "/question/{qid}/value/{valueid}/delete",
            "view": deleteQuestionValue_view,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "modifyquestion",
            "path": "/question/{qid}/edit",
            "view": modifyQuestion_view,
            "renderer": "question/modifyquestion.jinja2",
        }
    )
    routes.append(
        {
            "name": "deletequestion",
            "path": "/question/{qid}/delete",
            "view": deleteQuestion_view,
            "renderer": "json",
        }
    )

    # Enumerators
    routes.append(
        addRoute(
            "enumerators",
            "/enumerators",
            enumerators_view,
            "enumerators/enumerators.jinja2",
        )
    )
    routes.append(
        addRoute(
            "addenumerator",
            "/enumerators/add",
            addEnumerator_view,
            "enumerators/addenumerator.jinja2",
        )
    )
    routes.append(
        addRoute(
            "modifyenumerator",
            "/enumerator/{enumeratorid}/modify",
            modifyEnumerator_view,
            "enumerators/modifyenumerator.jinja2",
        )
    )
    routes.append(
        addRoute(
            "deleteenumerator",
            "/enumerator/{enumeratorid}/delete",
            deleteEnumerator_view,
            "json",
        )
    )

    # Tecnologies library
    routes.append(
        addRoute(
            "usertechnologies",
            "/technologies",
            technologies_view,
            "technologies/technologies.jinja2",
        )
    )
    routes.append(
        addRoute(
            "newusertechnology",
            "/technology/new",
            newtechnology_view,
            "technologies/newTechnology.jinja2",
        )
    )
    routes.append(
        addRoute(
            "modifyusertechnology",
            "/technology/{technologyid}/modify",
            modifytechnology_view,
            "technologies/modifyTechnology.jinja2",
        )
    )
    routes.append(
        addRoute(
            "deleteusertechnology",
            "/technology/{technologyid}/delete",
            deletetechnology_view,
            "json",
        )
    )

    routes.append(
        addRoute(
            "useralias",
            "/technology/{technologyid}/alias",
            alias_view,
            "technologies/aliases/alias.jinja2",
        )
    )
    routes.append(
        addRoute(
            "newuseralias",
            "/technology/{technologyid}/alias/new",
            newalias_view,
            "technologies/aliases/newAlias.jinja2",
        )
    )
    routes.append(
        addRoute(
            "modifyuseralias",
            "/technology/{technologyid}/alias/{aliasid}/modify",
            modifyalias_view,
            "technologies/aliases/modifyAlias.jinja2",
        )
    )
    routes.append(
        addRoute(
            "deleteuseralias",
            "/technology/{technologyid}/alias/{aliasid}/delete",
            deletealias_view,
            "json",
        )
    )

    # Project Enumerators
    routes.append(
        addRoute(
            "prjenumerators",
            "/project/{projectid}/enumerators",
            projectEnumerators_view,
            "project/enumerators/enumerators.jinja2",
        )
    )
    routes.append(
        addRoute(
            "addprjenumerators",
            "/project/{projectid}/enumerators/add",
            addProjectEnumerators_view,
            "project/enumerators/addenumerators.jinja2",
        )
    )
    routes.append(
        addRoute(
            "removeprjenumerator",
            "/project/{projectid}/enumerator/{enumeratorid}/remove",
            removeProjectEnumerators_view,
            "json",
        )
    )

    # Registry
    routes.append(
        addRoute(
            "registry",
            "/project/{projectid}/registry",
            registry_view,
            "project/registry/registry.jinja2",
        )
    )
    routes.append(
        addRoute(
            "registrypreview",
            "/project/{projectid}/registry/preview",
            registryPreview_view,
            "project/registry/previewform.jinja2",
        )
    )
    routes.append(
        addRoute(
            "registryenketo",
            "/project/{projectid}/registry/preview/{file}",
            registryEnketo_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "newregistryquestion",
            "project/{projectid}/registry/{groupid}/newquestion",
            newRegistryQuestion_view,
            "project/registry/newquestions.jinja2",
        )
    )
    routes.append(
        addRoute(
            "deleteregistrygroup",
            "project/{projectid}/registry/{groupid}/delete",
            deleteRegistrySection_view,
            "json",
        )
    )
    routes.append(
        addRoute(
            "modifyregistrygroup",
            "project/{projectid}/registry/{groupid}/modify",
            modifyRegistrySection_view,
            "project/registry/modifygroup.jinja2",
        )
    )
    routes.append(
        addRoute(
            "newregistrygroup",
            "project/{projectid}/registry/newsection",
            newRegistrySection_view,
            "project/registry/newgroup.jinja2",
        )
    )
    routes.append(
        addRoute(
            "cancelregistry",
            "/project/{projectid}/registry/cancel",
            cancelRegistry_view,
            "project/cancelregistry.jinja2",
        )
    )
    routes.append(
        addRoute(
            "closeregistry",
            "/project/{projectid}/registry/close",
            closeRegistry_view,
            "project/closepregistry.jinja2",
        )
    )

    # Assessment
    routes.append(
        addRoute(
            "assessment",
            "/project/{projectid}/assessments",
            assessmenthead_view,
            "project/assessment/assessment.jinja2",
        )
    )
    routes.append(
        addRoute(
            "newassessment",
            "/project/{projectid}/assessments/new",
            newassessmenthead_view,
            "project/assessment/newassessment.jinja2",
        )
    )
    routes.append(
        addRoute(
            "startassessments",
            "/project/{projectid}/assessments/start",
            startAssessments_view,
            "project/startassessments.jinja2",
        )
    )
    # routes.append(addRoute('cancelassessments', '/project/{projectid}/assessment/{assessmentid}/cancel', cancelAssessment_view,'project/cancelassessment.jinja2'))
    routes.append(
        addRoute(
            "modifyassessment",
            "/project/{projectid}/assessment/{assessmentid}/edit",
            modifyassessmenthead_view,
            "project/assessment/modifyassessment.jinja2",
        )
    )
    routes.append(
        addRoute(
            "deleteassessment",
            "/project/{projectid}/assessment/{assessmentid}/delete",
            deleteassessmenthead_view,
            "json",
        )
    )
    routes.append(
        addRoute(
            "closeassessment",
            "/project/{projectid}/assessment/{assessmentid}/close",
            closeAssessment_view,
            "project/closeassessment.jinja2",
        )
    )
    routes.append(
        addRoute(
            "cancelassessment",
            "/project/{projectid}/assessment/{assessmentid}/cancel",
            CancelAssessmentView,
            "project/cancelassessment.jinja2",
        )
    )

    routes.append(
        addRoute(
            "assessmentdetail",
            "/project/{projectid}/assessment/{assessmentid}",
            assessment_view,
            "project/assessment/assessmentdetail.jinja2",
        )
    )
    routes.append(
        addRoute(
            "assessmentpreview",
            "/project/{projectid}/assessment/{assessmentid}/preview",
            assessmentPreview_view,
            "project/assessment/previewform.jinja2",
        )
    )
    routes.append(
        addRoute(
            "assessmentenketo",
            "/project/{projectid}/assessment/{assessmentid}/preview/{file}",
            assessmentEnketo_view,
            None,
        )
    )

    routes.append(
        addRoute(
            "newassessmentquestion",
            "project/{projectid}/assessment/{assessmentid}/{groupid}/newquestion",
            newAssessmentQuestion_view,
            "project/assessment/newquestions.jinja2",
        )
    )
    routes.append(
        addRoute(
            "deleteassessmentgroup",
            "project/{projectid}/assessment/{assessmentid}/{groupid}/delete",
            deleteAssessmentSection_view,
            "json",
        )
    )
    routes.append(
        addRoute(
            "modifyassessmentgroup",
            "project/{projectid}/assessment/{assessmentid}/{groupid}/modify",
            modifyAssessmentSection_view,
            "project/assessment/modifygroup.jinja2",
        )
    )
    routes.append(
        addRoute(
            "newassessmentgroup",
            "project/{projectid}/assessment/{assessmentid}/newsection",
            newAssessmentSection_view,
            "project/assessment/newgroup.jinja2",
        )
    )

    # Project technologies and aliases
    routes.append(
        addRoute(
            "prjtechnologies",
            "/project/{projectid}/technologies",
            projectTecnologies_view,
            "project/technologies/technologies.jinja2",
        )
    )
    routes.append(
        addRoute(
            "prjtechaliases",
            "/project/{projectid}/technology/{tech_id}/aliases",
            prjTechAliases_view,
            "project/technologies/technologyaliases.jinja2",
        )
    )
    routes.append(
        addRoute(
            "addprjtechalias",
            "/project/{projectid}/technology/{tech_id}/addalias",
            prjTechAliasAdd_view,
            "project/technologies/addalias.jinja2",
        )
    )
    routes.append(
        addRoute(
            "deleteprjtechalias",
            "/project/{projectid}/technology/{tech_id}/alias/{alias_id}/delete",
            prjTechAliasDelete_view,
            "project/technologies/deletealias.jinja2",
        )
    )

    # Project combinations
    routes.append(
        addRoute(
            "combinations",
            "/project/{projectid}/combinations",
            projectCombinations_view,
            "project/registry/create/createregistry.jinja2",
        )
    )

    # Products
    routes.append(
        addRoute(
            "productList",
            "/productList",
            productsView,
            "project/productsList/productsList.jinja2",
        )
    )
    routes.append(addRoute("download", "/download/{product_id}", downloadView, None))
    routes.append(
        addRoute("downloadJson", "/downloadJson/{product_id}", downloadJsonView, "json")
    )
    routes.append(
        addRoute(
            "dataProductsList",
            "dataProductsList",
            dataView,
            "snippets/project/productsList/productsList.jinja2",
        )
    )

    # EditData
    routes.append(
        addRoute(
            "EditDataRegistry",
            "/project/{projectid}/form/{formid}/EditData",
            editDataView,
            "project/editData/editData.jinja2",
        )
    )
    routes.append(
        addRoute(
            "EditDataAssessment",
            "/project/{projectid}/form/{formid}/{codeid}/EditData",
            editDataView,
            "project/editData/editData.jinja2",
        )
    )

    routes.append(
        addRoute(
            "downloadDataRegistry",
            "/project/{projectid}/form/{formid}/Download",
            downloadDataView,
            "json",
        )
    )
    routes.append(
        addRoute(
            "downloadDataAssessment",
            "/project/{projectid}/form/{formid}/{codeid}/Download",
            downloadDataView,
            "json",
        )
    )

    routes.append(
        addRoute(
            "uploadDataRegistry",
            "/project/{projectid}/form/{formid}/Upload",
            uploadDataView,
            "project/editData/upload.jinja2",
        )
    )
    routes.append(
        addRoute(
            "uploadDataAssessment",
            "/project/{projectid}/form/{formid}/{codeid}/Upload",
            uploadDataView,
            "project/editData/upload.jinja2",
        )
    )

    # ODK forms
    routes.append(addRoute("odkformlist", "/{userid}/formList", formList_view, None))
    routes.append(
        addRoute("odksubmission", "/{userid}/submission", submission_view, None)
    )
    routes.append(addRoute("odkpush", "/{userid}/push", push_view, None))
    routes.append(
        addRoute("odkxmlform", "/{userid}/{projectid}/xmlform", XMLForm_view, None)
    )
    routes.append(
        addRoute("odkmanifest", "/{userid}/{projectid}/manifest", manifest_view, None)
    )
    routes.append(
        addRoute(
            "odkmediafile",
            "/{userid}/{projectid}/manifest/mediafile/{fileid}",
            mediaFile_view,
            None,
        )
    )

    routes.append(
        addRoute(
            "odkxmlformass",
            "/{userid}/{projectid}/{assessmentid}/xmlform",
            assessmentXMLForm_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "odkmanifestass",
            "/{userid}/{projectid}/{assessmentid}/manifest",
            assessmentManifest_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "odkmediafileass",
            "/{userid}/{projectid}/{assessmentid}/manifest/mediafile/{fileid}",
            assessmentMediaFile_view,
            None,
        )
    )

    # Analysis
    routes.append(
        addRoute(
            "createAnalysis",
            "/generateAnalysis",
            analysisDataView,
            "project/analysis/projectAnalysis.jinja2",
        )
    )

    routes.append(
        addRoute(
            "projectInformation",
            "/projectInformation/{id}",
            projectInformation_view,
            "progress/progressInformation.jinja2",
        )
    )
    # --------------------------------------------------------ClimMob API--------------------------------------------------------#
    """
    """
    # Create Project
    routes.append(
        addRoute("addproject_api", "/api/createProject", createProject_view, None)
    )
    routes.append(
        addRoute("readProjects_api", "/api/readProjects", readProjects_view, "json")
    )
    routes.append(
        addRoute("updateproject_api", "/api/updateProject", updateProject_view, None)
    )
    routes.append(
        addRoute(
            "deleteproject_api", "/api/deleteProject", deleteProject_view_api, None
        )
    )

    # Enumerators
    routes.append(
        addRoute(
            "addenumerator_api", "/api/createEnumerator", createEnumerator_view, None
        )
    )
    routes.append(
        addRoute(
            "readenumerators_api", "/api/readEnumerators", readEnumerators_view, None
        )
    )
    routes.append(
        addRoute(
            "updateenumerator_api", "/api/updateEnumerator", updateEnumerator_view, None
        )
    )
    routes.append(
        addRoute(
            "modifypassenumerator_api",
            "/api/updatePasswordEnumerator",
            updatePasswordEnumerator_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteenumerator_api",
            "/api/deleteEnumerator",
            apiDeleteEnumerator_view,
            None,
        )
    )

    # Tecnologies library
    routes.append(
        addRoute(
            "addusertechnology_api",
            "/api/createTechnology",
            createTechnology_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readtechnologies_api", "/api/readTecnologies", readTechnologies_view, None
        )
    )
    routes.append(
        addRoute(
            "updatetechnology_api", "/api/updateTechnology", updateTechnology_view, None
        )
    )
    routes.append(
        addRoute(
            "deletetechnology_api",
            "/api/deleteTechnology",
            deletetechnologyView_api,
            None,
        )
    )

    # Alias library
    routes.append(
        addRoute("adduseralias_api", "/api/createAlias", createAlias_view, None)
    )
    routes.append(addRoute("readalias_api", "/api/readAlias", readAlias_view, None))
    routes.append(
        addRoute("updatealias_api", "/api/updateAlias", updateAlias_view, None)
    )
    routes.append(
        addRoute("deletealias_api", "/api/deleteAlias", deleteAliasView_api, None)
    )

    # Questions
    routes.append(
        addRoute("addquestion_api", "/api/createQuestion", createQuestion_view, None)
    )
    routes.append(
        addRoute("readquestions_api", "/api/readQuestions", readQuestions_view, None)
    )
    routes.append(
        addRoute("updateQuestion_api", "/api/updateQuestion", updateQuestion_view, None)
    )
    routes.append(
        addRoute(
            "deletequestion_api", "/api/deleteQuestion", deleteQuestion_viewApi, None
        )
    )
    routes.append(
        addRoute(
            "readquestionvalues_api",
            "/api/readQuestionValues",
            readQuestionValues_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "addquestionvalues_api",
            "/api/addQuestionValues",
            addQuestionValue_viewApi,
            None,
        )
    )
    routes.append(
        addRoute(
            "updatequestionvalues_api",
            "/api/updateQuestionValues",
            updateQuestionValue_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deletequestionvalues_api",
            "/api/deleteQuestionValues",
            deleteQuestionValue_viewApi,
            None,
        )
    )
    # routes.append(addRoute('readquestionperformance_api'      , '/api/readQuestionPerformance'      , readQuestionPerformance_view      , None))
    # routes.append(addRoute('readquestioncharacteristics_api'  , '/api/readQuestionCharacteristic'   , readQuestionCharacteristic_view   , None))
    routes.append(
        addRoute(
            "updatequestionperformance_api",
            "/api/updateQuestionPerformance",
            updateQuestionPerformance_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "updatequestioncharacteristics_api",
            "/api/updateQuestionCharacteristics",
            updateQuestionCharacteristics_view,
            None,
        )
    )

    # Project Enumerators
    routes.append(
        addRoute(
            "addprjenumerators_api",
            "/api/addProjectEnumerator",
            addProjectEnumerator_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjenumerators_api",
            "/api/readProjectEnumerators",
            readProjectEnumerators_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibleenumerators_api",
            "/api/readPossibleProjectEnumerators",
            readPossibleProjectEnumerators_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteprjenumerator_api",
            "/api/deleteProjectEnumerator",
            deleteProjectEnumerator_view,
            None,
        )
    )

    # Project technologies and aliases
    routes.append(
        addRoute(
            "addprjtechnology",
            "/api/addProjectTechnology",
            addProjectTechnology_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjtechnologies",
            "/api/readProjectTechnologies",
            readProjectTechnologies_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibletechnologies",
            "/api/readPossibleProjectTechnologies",
            readPossibleProjectTechnologies_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteprjtechnology",
            "/api/deleteProjectTechnology",
            deleteProjectTechnology_view,
            None,
        )
    )

    routes.append(
        addRoute(
            "addprjtechnologyalias",
            "/api/addProjectTechnologyAlias",
            addProjectTechnologyAlias_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "addprjtechnologyaliasextra",
            "/api/addProjectTechnologyAliasExtra",
            addProjectTechnologyAliasExtra_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjtechnologiesalias",
            "/api/readProjectTechnologiesAlias",
            readProjectTechnologiesAlias_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjtechnologiesaliasextra",
            "/api/readProjectTechnologiesAliasExtra",
            readProjectTechnologiesAliasExtra_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibletechnologiesalias",
            "/api/readPossibleProjectTechnologiesAlias",
            readPossibleProjectTechnologiesAlias_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteprjtechnologyalias",
            "/api/deleteProjectTechnologyAlias",
            deleteProjectTechnologyAlias_view,
            None,
        )
    )

    # Project Registry
    routes.append(
        addRoute(
            "readprjregistry",
            "/api/readProjectRegistry",
            readProjectRegistry_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibleregistry",
            "/api/readPossibleQuestionsForRegistryGroup",
            readPossibleQuestionsForRegistryGroup_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "addregistrygroup", "/api/createRegistryGroup", addRegistryGroup_view, None
        )
    )
    routes.append(
        addRoute(
            "updateregistrygroup",
            "/api/updateRegistryGroup",
            updateRegistryGroup_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteregistrygroup2",
            "/api/deleteRegistryGroup",
            deleteRegistryGroup_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "addquestiontogroup",
            "/api/addQuestionToGroupRegistry",
            addQuestionToGroupRegistry_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deletequestionfromgroup",
            "/api/deleteQuestionFromGroupRegistry",
            deleteQuestionFromGroupRegistry_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "orderregistryquestions",
            "/api/orderRegistryQuestions",
            orderRegistryQuestions_view,
            None,
        )
    )

    # Project Combinations
    routes.append(
        addRoute(
            "readprojectcombinations",
            "/api/readProjectCombinations",
            readProjectCombinations_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "updateUsableCombinations",
            "/api/setUsableCombinations",
            setUsableCombinations_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprojectpackages", "/api/readProjectPackages", createPackages_view, None
        )
    )
    routes.append(
        addRoute(
            "createprojectregistry",
            "/api/createProjectRegistry",
            createProjectRegistry_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "cancelprojectregistry",
            "/api/cancelProjectREgistry",
            cancelRegistryApi_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "closeprojectregistry",
            "/api/closeProjectRegistry",
            closeRegistryApi_view,
            None,
        )
    )

    # Registry actions
    routes.append(
        addRoute(
            "readregistrystructure",
            "/api/readRegistryStructure",
            readRegistryStructure_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "pushjsontoregistry",
            "/api/pushJsonToRegistry",
            pushJsonToRegistry_view,
            None,
        )
    )

    # Products
    routes.append(
        addRoute("readproducts", "/api/readProducts", readProducts_view, None)
    )
    routes.append(addRoute("downloadApi", "/api/downloadApi", downloadApi_view, None))

    # Project Assessments
    routes.append(
        addRoute(
            "readprjassessments",
            "/api/readProjectAssessments",
            readProjectAssessments_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "addnewassessment", "/api/createAssessment", addNewAssessment_view, None
        )
    )
    routes.append(
        addRoute(
            "updateprjassessment",
            "/api/updateProjectAssessment",
            updateProjectAssessment_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteprjassessment",
            "/api/deleteProjectAssessment",
            deleteProjectAssessment_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "createprjassessment",
            "/api/createProjectAssessment",
            createProjectAssessment_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "cancelprojectassessment",
            "/api/cancelProjectAssessment",
            cancelAssessmentApi_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "closeprojectassessment",
            "/api/closeProjectAssessment",
            closeAssessmentApi_view,
            None,
        )
    )
    # Project Assessment groups
    routes.append(
        addRoute(
            "readprjassessmentstructure",
            "/api/readProjectAssessmentStructure",
            readProjectAssessmentStructure_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibleassessment",
            "/api/readPossibleQuestionForAssessmentGroup",
            readPossibleQuestionForAssessmentGroup_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "addassessmentgroup",
            "/api/createAssessmentGroup",
            createAssessmentGroup_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "updateassessmentgroup",
            "/api/updateAssessmentGroup",
            updateAssessmentGroup_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteassessmentgroup2",
            "/api/deleteAssessmentGroup",
            deleteAssessmentGroup_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "orderassessmentquestion",
            "/api/orderAssessmentQuestions",
            orderAssessmentQuestions_view,
            None,
        )
    )
    # Project Assessment questions
    routes.append(
        addRoute(
            "addquestiontogroupass",
            "/api/addQuestionToGroupAssessment",
            addQuestionToGroupAssessment_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deletequestionfromgroupass",
            "/api/deleteQuestionFromGroupAssessment",
            deleteQuestionFromGroupAssessment_view,
            None,
        )
    )

    # Assessments actions
    routes.append(
        addRoute(
            "readassessmentstructure",
            "/api/readAssessmentStructure",
            readAssessmentStructure_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "pushjsontoassessment",
            "/api/pushJsonToAssessment",
            pushJsonToAssessment_view,
            None,
        )
    )

    # Information of project
    routes.append(
        addRoute(
            "readDataOfProject",
            "/api/readDataOfProject",
            readDataOfProjectView_api,
            None,
        )
    )

    # Testing routes. Remove them for production
    routes.append(addRoute("testing", "/test", test_view, "json"))

    appendToRoutes(routes)

    config.add_notfound_view(notfound_view, renderer="404.jinja2")

    # Custom mapping can happen here AFTER the host maps
    for plugin in p.PluginImplementations(p.IRoutes):
        routes = plugin.after_mapping(config)
        appendToRoutes(routes)

    # Now add the routes and views to the config
    for curr_route in route_list:
        config.add_route(curr_route["name"], curr_route["path"])
        config.add_view(
            curr_route["view"],
            route_name=curr_route["name"],
            renderer=curr_route["renderer"],
        )
