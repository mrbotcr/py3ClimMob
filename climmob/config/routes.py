"""

These functions setup the routes for the host application and any plugins connected to it

"""

import climmob.plugins as p
from climmob.plugins.utilities import addRoute
from climmob.views.Api.enumerators import (
    CreateEnumeratorView,
    ReadEnumeratorsView,
    UpdateEnumeratorView,
    UpdatePasswordEnumeratorView,
    ApiDeleteEnumeratorView,
)
from climmob.views.Api.projectAssessmentStart import (
    createProjectAssessment_view,
    cancelAssessmentApi_view,
    closeAssessmentApi_view,
    readAssessmentStructure_view,
    pushJsonToAssessment_view,
    assessmentDataCleaning_view,
    readAssessmentData_view,
)
from climmob.views.Api.projectAssessments import (
    ReadProjectAssessmentsView,
    AddNewAssessmentView,
    UpdateProjectAssessmentView,
    DeleteProjectAssessmentView,
    ReadProjectAssessmentStructureView,
    CreateAssessmentGroupView,
    UpdateAssessmentGroupView,
    DeleteAssessmentGroupView,
    ReadPossibleQuestionForAssessmentGroupView,
    AddQuestionToGroupAssessmentView,
    DeleteQuestionFromGroupAssessmentView,
    OrderAssessmentQuestionsView,
)
from climmob.views.Api.projectCreation import (
    CreateProjectView,
    ReadProjectsView,
    updateProject_view,
    DeleteProjectViewApi,
    ReadListOfCountriesView,
    ReadListOfTemplatesView,
    ReadCollaboratorsView,
    AddCollaboratorView,
    DeleteCollaboratorView,
    ReadListOfLocationsView,
    ReadListOfUnitOfAnalysisView,
    ReadListOfObjectivesView,
)
from climmob.views.Api.projectEnumerators import (
    addProjectEnumerator_view,
    readProjectEnumerators_view,
    readPossibleProjectEnumerators_view,
    deleteProjectEnumerator_view,
)
from climmob.views.Api.projectProducts import readProducts_view, downloadApi_view
from climmob.views.Api.projectRegistry import (
    ReadProjectRegistryView,
    ReadPossibleQuestionsForRegistryGroupView,
    AddRegistryGroupView,
    UpdateRegistryGroupView,
    DeleteRegistryGroupView,
    AddQuestionToGroupRegistryView,
    DeleteQuestionFromGroupRegistryView,
    OrderRegistryQuestionsView,
)
from climmob.views.Api.projectRegistryStart import (
    readProjectCombinations_view,
    setUsableCombinations_view,
    setAvailabilityCombination_view,
    createPackages_view,
    createProjectRegistry_view,
    cancelRegistryApi_view,
    closeRegistryApi_view,
    readRegistryStructure_view,
    pushJsonToRegistry_view,
    registryDataCleaning_view,
    readRegistryData_view,
)
from climmob.views.Api.projectTechnologies import (
    AddProjectTechnologyView,
    ReadProjectTechnologiesView,
    ReadPossibleProjectTechnologiesView,
    DeleteProjectTechnologyView,
    AddProjectTechnologyAliasView,
    ReadProjectTechnologiesAliasView,
    ReadProjectTechnologiesAliasExtraView,
    ReadPossibleProjectTechnologiesAliasView,
    deleteProjectTechnologyAlias_view,
    AddProjectTechnologyAliasExtraView,
)
from climmob.views.Api.project_analysis import (
    ReadDataOfProjectViewApi,
    ReadVariablesForAnalysisViewApi,
    GenerateAnalysisByApiViewApi,
)
from climmob.views.Api.questions import (
    CreateQuestionView,
    ReadQuestionsView,
    ReadQuestionValuesView,
    AddQuestionValueViewApi,
    UpdateQuestionValueView,
    DeleteQuestionValueViewApi,
    UpdateQuestionCharacteristicsView,
    UpdateQuestionPerformanceView,
    UpdateQuestionView,
    DeleteQuestionViewApi,
    MultiLanguageQuestionView,
    ReadMultiLanguagesFromQuestionView,
)
from climmob.views.Api.questionsGroups import (
    readGroupsOfQuestions_view,
    createGroupOfQuestion_view,
    updateGroupOfQuestion_view,
    deleteGroupOfQuestion_view,
)
from climmob.views.Api.techaliases import (
    createAlias_view,
    readAlias_view,
    updateAlias_view,
    deleteAliasView_api,
)
from climmob.views.Api.technologies import (
    createTechnology_view,
    readTechnologies_view,
    updateTechnology_view,
    deletetechnologyView_api,
)
from climmob.views.Bot.bot import sendFeedbackToBot_view, readFeedback_view
from climmob.views.Share.projectShare import (
    projectShare_view,
    API_users_view,
    API_all_users_view,
    removeprojectShare_view,
)
from climmob.views.Affiliation import SearchAffiliationView
from climmob.views.assessment import (
    assessment_view,
    deleteAssessmentSection_view,
    getAssessmentDetails_view,
    assessmenthead_view,
    deleteassessmenthead_view,
    startAssessments_view,
    closeAssessment_view,
    CancelAssessmentView,
    assessmentFormCreation_view,
    assessmentSectionActions_view,
    getAssessmentSection_view,
)
from climmob.views.basic_views import (
    home_view,
    HealthView,
    notfound_view,
    login_view,
    register_view,
    logout_view,
    RecoverPasswordView,
    ResetPasswordView,
    StoreCookieView,
    TermsView,
    PrivacyView,
)
from climmob.views.cleanErrorLogs import CleanErrorLogsView
from climmob.views.cloneProjects.cloneProjects import cloneProjects_view
from climmob.views.dashboard import dashboard_view, projectInformation_view
from climmob.views.editData import (
    editDataView,
    downloadDataView,
    downloadErroLogDocument_view,
)
from climmob.views.enumerator import (
    getEnumeratorDetails_view,
    enumerators_view,
    deleteEnumerator_view,
)
from climmob.views.mapForProjectVisualization.mapForProjectVisualization import (
    showMapForProjectVisualization_view,
)
from climmob.views.odk import (
    FormlistView,
    FormListByProjectView,
    SubmissionView,
    SubmissionByProjectView,
    XMLFormView,
    ManifestView,
    MediaFileView,
    PushView,
    AssessmentXMLFormView,
    AssessmentMediaFileView,
    AssessmentManifestView,
)
from climmob.views.productsList import (
    productsView,
    generateProductView,
    downloadView,
    dataView,
)
from climmob.views.profile import profile_view, editProfile_view
from climmob.views.project import (
    newProject_view,
    getTemplatesByTypeOfProject_view,
    modifyProject_view,
    deleteProject_view,
    projectList_view,
    CurationOfProjects_view,
    GetUnitOfAnalysisByLocationView,
    GetObjectivesByLocationAndUnitOfAnalysisView,
)
from climmob.views.projectHelp.projectHelp import projectHelp_view
from climmob.views.project_analysis import analysisDataView
from climmob.views.project_combinations import projectCombinations_view
from climmob.views.project_enumerators import (
    projectEnumerators_view,
    removeProjectEnumerators_view,
)
from climmob.views.project_technologies import projectTecnologies_view
from climmob.views.question import (
    qlibrary_view,
    getUserQuestionDetails_view,
    getUserQuestionPreview_view,
    getUserCategoryDetails_view,
    categories_view,
    deleteQuestion_view,
    questionsActions_view,
    getUserLanguages_view,
    addUserLanguage_view,
    changeDefaultLanguage_view,
    deleteUserLanguage_view,
    getUserLanguagesPreview_view,
)
from climmob.views.registry import (
    RegistryView,
    DeleteRegistrySectionView,
    CancelRegistryView,
    CloseRegistryView,
    RegistryFormCreationView,
    RegistrySectionActionsView,
    GetRegistrySectionView,
    ChangeProjectMainLanguage_view,
)
from climmob.views.techaliases import deletealias_view
from climmob.views.technologies import (
    technologies_view,
    CurationOfTechnologies_view,
    deletetechnology_view,
    getUserTechnologyDetails_view,
    getUserTechnologyAliasDetails_view,
    APICropsView,
)
from climmob.views.metadata import (
    MetadataForms_view,
    MetadataFormDetails_view,
    DownloadMetadataForm_view,
    DeleteMetadataForms_view,
)
from climmob.views.test import test_view, sentry_debug_view

from climmob.views.questionTranslations import (
    QuestionTranslationsView,
    APILanguagesView,
    ChangeDefaultQuestionLanguageView,
)

from climmob.views.otherLanguages import (
    OtherLanguagesView,
    SaveOtherLanguagesView,
    GetOtherLanguagesView,
    requestLanguageTranslation_view,
)

from climmob.views.Api.languages import (
    ReadListOfLanguagesView,
    AddLanguageForUseView,
    DeleteLanguageView,
    ReadListOfUnusedLanguagesView,
    ReadAllGeneralPhrasesView,
    ChangeGeneralPhrasesView,
)
from climmob.views.projectsSummary.projectsSummary import (
    projectsSummary_view,
    downloadProjectsSummary_view,
)

from climmob.views.extra_form import ExtraFormPostView

from climmob.views.project_metadata import (
    ProjectMetadataForm_view,
    ShowMetadataForm_view,
)

# -------Api-------#

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
            "name": "health",
            "path": "/health",
            "view": HealthView,
            "renderer": "json",
        }
    )
    routes.append(
        {
            "name": "store_cookie",
            "path": "/cookie",
            "view": StoreCookieView,
            "renderer": None,
        }
    )
    routes.append(
        {
            "name": "terms",
            "path": "/terms",
            "view": TermsView,
            "renderer": "terms.jinja2",
        }
    )
    routes.append(
        {
            "name": "privacy",
            "path": "/privacy",
            "view": PrivacyView,
            "renderer": "privacy.jinja2",
        }
    )
    routes.append(
        {
            "name": "usage",
            "path": "/usage",
            "view": PrivacyView,
            "renderer": "usage.jinja2",
        }
    )
    routes.append(
        {
            "name": "APICrops",
            "path": "/crops",
            "view": APICropsView,
            "renderer": "json",
        }
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
        addRoute(
            "reset_password",
            "/reset/{reset_key}/password",
            ResetPasswordView,
            "reset_password.jinja2",
        )
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
            "name": "projectList",
            "path": "/projectList",
            "view": projectList_view,
            "renderer": "project/projectList.jinja2",
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
    # Other languages
    routes.append(
        addRoute(
            "otherLanguages",
            "/otherLanguages",
            OtherLanguagesView,
            "otherLanguages/otherLanguages.jinja2",
        )
    )
    routes.append(
        addRoute(
            "saveOtherLanguages",
            "/saveOtherLanguages",
            SaveOtherLanguagesView,
            "json",
        )
    )

    routes.append(
        addRoute(
            "getOtherLanguage",
            "/language/{language}/getOtherLanguage",
            GetOtherLanguagesView,
            "string",
        )
    )

    routes.append(
        addRoute(
            "requestLanguageTranslation",
            "/requestLanguageTranslation",
            requestLanguageTranslation_view,
            "json",
        )
    )
    # Project routes
    routes.append(
        addRoute(
            "getTemplatesByTypeOfProject",
            "/projectType/{typeid}",
            getTemplatesByTypeOfProject_view,
            "json",
        )
    )

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
            "path": "/user/{user}/project/{project}/edit",
            "view": modifyProject_view,
            "renderer": "project/modifyproject.jinja2",
        }
    )
    routes.append(
        {
            "name": "deleteproject",
            "path": "/user/{user}/project/{project}/delete",
            "view": deleteProject_view,
            "renderer": "json",
        }
    )
    routes.append(
        {
            "name": "getunitofanalysisbylocation",
            "path": "/location/{locationid}/getUnitOfAnalysis",
            "view": GetUnitOfAnalysisByLocationView,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "getobjectivesbylocationandunitofanalysis",
            "path": "/location/{locationid}/unitOfAnalysis/{unitofanalysisid}/getObjectives",
            "view": GetObjectivesByLocationAndUnitOfAnalysisView,
            "renderer": "json",
        }
    )

    # Question library
    routes.append(
        addRoute(
            "getUserQuestionDetails",
            "/user/{user}/question/{questionid}",
            getUserQuestionDetails_view,
            "json",
        )
    )

    routes.append(
        addRoute(
            "sentry-debug",
            "/sentry-debug",
            sentry_debug_view,
            None,
        )
    )

    routes.append(
        addRoute(
            "getUserQuestionPreview",
            "/user/{user}/question/{questionid}/Preview",
            getUserQuestionPreview_view,
            "string",
        )
    )

    routes.append(
        addRoute(
            "getUserCategoryDetails",
            "/user/{user}/category/{categoryid}",
            getUserCategoryDetails_view,
            "json",
        )
    )

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
            "name": "questionActions",
            "path": "/questionActions",
            "view": questionsActions_view,
            "renderer": "json",
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
            "name": "deletequestion",
            "path": "/question/{qid}/delete",
            "view": deleteQuestion_view,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "questionTranslations",
            "path": "/user/{user}/question/{questionid}/questionTranslations",
            "view": QuestionTranslationsView,
            "renderer": "question/translations.jinja2",
        }
    )

    routes.append(
        {
            "name": "changeDefaultQuestionLanguage",
            "path": "/user/{user}/question/{questionid}/changeDefaultQuestionLanguage",
            "view": ChangeDefaultQuestionLanguageView,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "getUserLanguages",
            "path": "/user/{user}/getUserLanguages",
            "view": getUserLanguages_view,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "getUserLanguagesPreview",
            "path": "/getUserLanguagesPreview",
            "view": getUserLanguagesPreview_view,
            "renderer": "string",
        }
    )

    routes.append(
        {
            "name": "addUserLanguage",
            "path": "/addUserLanguage",
            "view": addUserLanguage_view,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "changeDefaultLanguage",
            "path": "/changeDefaultLanguage",
            "view": changeDefaultLanguage_view,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "deleteUserLanguage",
            "path": "/language/{lang}/delete",
            "view": deleteUserLanguage_view,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "APIlanguages",
            "path": "/user/{user}/languages",
            "view": APILanguagesView,
            "renderer": "json",
        }
    )

    routes.append(
        {
            "name": "APIlanguagesClimMob",
            "path": "/languages",
            "view": APILanguagesView,
            "renderer": "json",
        }
    )

    # routes.append(
    #     {
    #         "name": "getQuestionTranslations",
    #         "path": "/question/{questionid}/language/{lang}/getQuestionTranslations",
    #         "view": getQuestionTranslations_view,
    #         "renderer": "json",
    #     }
    # )

    # Enumerators
    routes.append(
        addRoute(
            "getEnumeratorDetails",
            "/user/{user}/enumerator/{enumid}",
            getEnumeratorDetails_view,
            "json",
        )
    )

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
            "deleteenumerator",
            "/enumerator/{enumeratorid}/delete",
            deleteEnumerator_view,
            "json",
        )
    )

    # Tecnologies library
    routes.append(
        addRoute(
            "getUserTechnologyDetails",
            "/user/{user}/technology/{technologyid}",
            getUserTechnologyDetails_view,
            "json",
        )
    )

    routes.append(
        addRoute(
            "getUserTechnologyAliasDetails",
            "/user/{user}/technology/{technologyid}/alias/{aliasid}",
            getUserTechnologyAliasDetails_view,
            "json",
        )
    )

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
            "curationoftechnologies",
            "/CurationOfTechnologies",
            CurationOfTechnologies_view,
            "technologies/curationoftechnologies.jinja2",
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
            "deleteuseralias",
            "/technology/{technologyid}/alias/{aliasid}/delete",
            deletealias_view,
            "json",
        )
    )

    # Metadata library

    routes.append(
        addRoute(
            "librarymetadata",
            "/metadata",
            MetadataForms_view,
            "Metadata/metadata.jinja2",
        )
    )

    routes.append(
        addRoute(
            "metadataFormDetails",
            "/metadataform/{metadataform}/metadataFormDetails",
            MetadataFormDetails_view,
            "json",
        )
    )

    routes.append(
        addRoute(
            "downloadMetadataForm",
            "/metadataform/{metadataform}/download",
            DownloadMetadataForm_view,
            None,
        )
    )

    routes.append(
        addRoute(
            "deletemetadataform",
            "/metadataform/{metadataform}/delete",
            DeleteMetadataForms_view,
            "json",
        )
    )

    # Project

    routes.append(
        addRoute(
            "curationofprojects",
            "/CurationOfProjects",
            CurationOfProjects_view,
            "project/curationofprojects.jinja2",
        )
    )

    # Project Enumerators
    routes.append(
        addRoute(
            "prjenumerators",
            "/user/{user}/project/{project}/enumerators",
            projectEnumerators_view,
            "project/enumerators/enumerators.jinja2",
        )
    )
    routes.append(
        addRoute(
            "removeprjenumerator",
            "/user/{user}/project/{project}/enumerator/{enumeratorid}/remove",
            removeProjectEnumerators_view,
            "json",
        )
    )

    # Registry
    routes.append(
        addRoute(
            "registry",
            "/user/{user}/project/{project}/registry",
            RegistryView,
            "project/registry/registry.jinja2",
        )
    )
    routes.append(
        addRoute(
            "getRegistrySection",
            "/user/{user}/project/{project}/section/{section}/getRegistrySection",
            GetRegistrySectionView,
            "json",
        )
    )
    routes.append(
        addRoute(
            "registrySaveChanges",
            "/user/{user}/project/{project}/registry/savechanges",
            RegistryFormCreationView,
            "string",
        )
    )

    routes.append(
        addRoute(
            "deleteregistrygroup",
            "/user/{user}/project/{project}/registry/{groupid}/delete",
            DeleteRegistrySectionView,
            "json",
        )
    )
    routes.append(
        {
            "name": "registrySectionActions",
            "path": "/user/{user}/project/{project}/registrySectionActions",
            "view": RegistrySectionActionsView,
            "renderer": "json",
        }
    )
    routes.append(
        {
            "name": "changeprojectmainlanguage",
            "path": "/ChangeProjectMainLanguage",
            "view": ChangeProjectMainLanguage_view,
            "renderer": "json",
        }
    )
    routes.append(
        addRoute(
            "cancelregistry",
            "/user/{user}/project/{project}/registry/cancel",
            CancelRegistryView,
            "project/cancelregistry.jinja2",
        )
    )
    routes.append(
        addRoute(
            "closeregistry",
            "/user/{user}/project/{project}/registry/close",
            CloseRegistryView,
            "project/closepregistry.jinja2",
        )
    )

    # Assessment
    routes.append(
        addRoute(
            "getAssessmentDetails",
            "/user/{user}/project/{project}/assessment/{assessmentid}/details",
            getAssessmentDetails_view,
            "json",
        )
    )
    routes.append(
        addRoute(
            "assessment",
            "/user/{user}/project/{project}/assessments",
            assessmenthead_view,
            "project/assessment/assessment.jinja2",
        )
    )
    routes.append(
        addRoute(
            "startassessments",
            "/user/{user}/project/{project}/assessments/start",
            startAssessments_view,
            "project/startassessments.jinja2",
        )
    )
    routes.append(
        addRoute(
            "deleteassessment",
            "/user/{user}/project/{project}/assessment/{assessmentid}/delete",
            deleteassessmenthead_view,
            "json",
        )
    )
    routes.append(
        addRoute(
            "closeassessment",
            "/user/{user}/project/{project}/assessment/{assessmentid}/close",
            closeAssessment_view,
            "project/closeassessment.jinja2",
        )
    )
    routes.append(
        addRoute(
            "cancelassessment",
            "/user/{user}/project/{project}/assessment/{assessmentid}/cancel",
            CancelAssessmentView,
            "project/cancelassessment.jinja2",
        )
    )

    routes.append(
        addRoute(
            "assessmentdetail",
            "/user/{user}/project/{project}/assessment/{assessmentid}",
            assessment_view,
            "project/assessment/assessmentdetail.jinja2",
        )
    )
    routes.append(
        addRoute(
            "assessmentdetailSaveChanges",
            "/user/{user}/project/{project}/assessment/{assessmentid}/savechanges",
            assessmentFormCreation_view,
            "string",
        )
    )

    routes.append(
        addRoute(
            "deleteassessmentgroup",
            "/user/{user}/project/{project}/assessment/{assessmentid}/{groupid}/delete",
            deleteAssessmentSection_view,
            "json",
        )
    )
    routes.append(
        {
            "name": "assessmentSectionActions",
            "path": "/user/{user}/project/{project}/assessment/{assessmentid}/assessmenrSectionActions",
            "view": assessmentSectionActions_view,
            "renderer": "json",
        }
    )
    routes.append(
        addRoute(
            "getAssessmentSection",
            "/user/{user}/project/{project}/assessment/{assessmentid}/section/{section}/getAssessmentSection",
            getAssessmentSection_view,
            "json",
        )
    )
    # Project technologies and aliases
    routes.append(
        addRoute(
            "prjtechnologies",
            "/user/{user}/project/{project}/technologies",
            projectTecnologies_view,
            "project/technologies/technologies.jinja2",
        )
    )

    # Project share
    routes.append(
        addRoute(
            "shareProject",
            "/user/{user}/project/{project}/share",
            projectShare_view,
            "project/share/share.jinja2",
        )
    )

    routes.append(
        addRoute(
            "api_select2_users",
            "/user/{user}/project/{project}/api/select2_user",
            API_users_view,
            "json",
        )
    )

    routes.append(
        addRoute(
            "api_select2_all_users",
            "/api/select2_user",
            API_all_users_view,
            "json",
        )
    )

    routes.append(
        addRoute(
            "searchaffiliation",
            "/api/search_affiliation",
            SearchAffiliationView,
            "json",
        )
    )

    routes.append(
        addRoute(
            "removeprjshare",
            "/user/{user}/project/{project}/share/{collaborator}/remove",
            removeprojectShare_view,
            "json",
        )
    )

    # Project combinations
    routes.append(
        addRoute(
            "combinations",
            "/user/{user}/project/{project}/combinations",
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
    routes.append(
        addRoute(
            "generateProduct",
            "/user/{user}/project/{project}/{productid}/{processname}/generateProduct",
            generateProductView,
            None,
        )
    )

    routes.append(
        addRoute(
            "download", "/download/{celery_taskid}/{product_id}", downloadView, None
        )
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
            "/user/{user}/project/{project}/form/{formid}/EditData",
            editDataView,
            "project/editData/editData.jinja2",
        )
    )
    routes.append(
        addRoute(
            "EditDataAssessment",
            "/user/{user}/project/{project}/form/{formid}/{codeid}/EditData",
            editDataView,
            "project/editData/editData.jinja2",
        )
    )

    routes.append(
        addRoute(
            "downloadDataRegistry",
            "/user/{user}/project/{project}/form/{formid}/format/{formatid}/Download",
            downloadDataView,
            "json",
        )
    )
    routes.append(
        addRoute(
            "downloadDataAssessment",
            "/user/{user}/project/{project}/form/{formid}/{codeid}/format/{formatid}/Download",
            downloadDataView,
            "json",
        )
    )

    # Errors reviews
    routes.append(
        addRoute(
            "CleanErrorLogs",
            "/user/{user}/project/{project}/form/{formid}/CleanErrorLogs",
            CleanErrorLogsView,
            "project/CleanErrors/clean.jinja2",
        )
    )

    routes.append(
        addRoute(
            "CleanErrorLogsDetails",
            "/user/{user}/project/{project}/form/{formid}/logId/{logid}/CleanErrorLogs",
            CleanErrorLogsView,
            "project/CleanErrors/clean.jinja2",
        )
    )

    routes.append(
        addRoute(
            "downloadErrorLogDocumentRegistry",
            "/user/{user}/project/{project}/form/{formid}/DownloadErrorLogDocument",
            downloadErroLogDocument_view,
            "json",
        )
    )

    routes.append(
        addRoute(
            "CleanErrorLogsAssessment",
            "/user/{user}/project/{project}/form/{formid}/{codeid}/CleanErrorLogs",
            CleanErrorLogsView,
            "project/CleanErrors/clean.jinja2",
        )
    )

    routes.append(
        addRoute(
            "CleanErrorLogsDetailsAssessment",
            "/user/{user}/project/{project}/form/{formid}/{codeid}/logId/{logid}/CleanErrorLogs",
            CleanErrorLogsView,
            "project/CleanErrors/clean.jinja2",
        )
    )

    routes.append(
        addRoute(
            "downloadErrorLogDocumentAssessment",
            "/user/{user}/project/{project}/form/{formid}/{codeid}/DownloadErrorLogDocument",
            downloadErroLogDocument_view,
            "json",
        )
    )

    routes.append(
        addRoute(
            "map",
            "/map",
            showMapForProjectVisualization_view,
            "mapForProjectVisualization/mapForVisualization.jinja2",
        )
    )

    # ODK forms
    routes.append(addRoute("odkformlist", "/{userid}/formList", FormlistView, None))

    routes.append(
        addRoute(
            "odkFormlistByProject",
            "/user/{user}/project/{project}/collaborator/{collaborator}/formList",
            FormListByProjectView,
            None,
        )
    )

    routes.append(
        addRoute("odksubmission", "/{userid}/submission", SubmissionView, None)
    )

    routes.append(
        addRoute(
            "odkSubmissionByProject",
            "/user/{user}/project/{project}/collaborator/{collaborator}/submission",
            SubmissionByProjectView,
            None,
        )
    )

    routes.append(addRoute("odkpush", "/{userid}/push", PushView, None))
    routes.append(
        addRoute(
            "odkxmlform", "/{user}/{userowner}/{project}/xmlform", XMLFormView, None
        )
    )
    routes.append(
        addRoute(
            "odkmanifest", "/{user}/{userowner}/{project}/manifest", ManifestView, None
        )
    )
    routes.append(
        addRoute(
            "odkmediafile",
            "/{user}/{userowner}/{project}/manifest/mediafile/{fileid}",
            MediaFileView,
            None,
        )
    )

    routes.append(
        addRoute(
            "odkxmlformass",
            "/{user}/{userowner}/{project}/{assessmentid}/xmlform",
            AssessmentXMLFormView,
            None,
        )
    )
    routes.append(
        addRoute(
            "odkmanifestass",
            "/{user}/{userowner}/{project}/{assessmentid}/manifest",
            AssessmentManifestView,
            None,
        )
    )
    routes.append(
        addRoute(
            "odkmediafileass",
            "/{user}/{userowner}/{project}/{assessmentid}/manifest/mediafile/{fileid}",
            AssessmentMediaFileView,
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

    # Project Metadata

    routes.append(
        addRoute(
            "Metadata",
            "/user/{user}/project/{project}/metadata",
            ProjectMetadataForm_view,
            "project/metadata/metadata.jinja2",
        )
    )

    routes.append(
        addRoute(
            "ShowMetadataForm",
            "/user/{user}/project/{project}/metadataform/{metadataform}/ShowMetadata",
            ShowMetadataForm_view,
            "string",
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

    # Extra form

    routes.append(
        addRoute(
            "extraFormPOST",
            "/extraFormPOST",
            ExtraFormPostView,
            None,
        )
    )

    # Specific functions

    routes.append(
        {
            "name": "projectHelp",
            "path": "/projectHelp",
            "view": projectHelp_view,
            "renderer": "projectHelp/projectHelp.jinja2",
        }
    )

    routes.append(
        {
            "name": "cloneProject",
            "path": "/cloneProject",
            "view": cloneProjects_view,
            "renderer": "cloneProjects/cloneProjects.jinja2",
        }
    )

    routes.append(
        {
            "name": "projectsSummary",
            "path": "/projectsSummary",
            "view": projectsSummary_view,
            "renderer": "projectsSummary/projectsSummary.jinja2",
        }
    )

    routes.append(
        addRoute(
            "downloadProjectsSummary",
            "/download/{celery_taskid}/{product_id}/downloadProjectsSummary",
            downloadProjectsSummary_view,
            None,
        )
    )

    # --------------------------------------------------------ClimMob API--------------------------------------------------------#

    # Languages
    routes.append(
        addRoute(
            "readListOfLanguages",
            "/api/readListOfLanguages",
            ReadListOfLanguagesView,
            None,
        )
    )

    routes.append(
        addRoute(
            "readListOfUnusedLanguages",
            "/api/readListOfUnusedLanguages",
            ReadListOfUnusedLanguagesView,
            None,
        )
    )

    routes.append(
        addRoute(
            "addLanguageForUse", "/api/addLanguageForUse", AddLanguageForUseView, None
        )
    )

    routes.append(
        addRoute("deleteLanguage", "/api/deleteLanguage", DeleteLanguageView, None)
    )

    # Create Project
    routes.append(
        addRoute(
            "readListOfCountries",
            "/api/readListOfCountries",
            ReadListOfCountriesView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readListOfExperimentSide",
            "/api/readListOfExperimentSide",
            ReadListOfLocationsView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readListOfUnitOfAnalysis",
            "/api/readListOfUnitOfAnalysis",
            ReadListOfUnitOfAnalysisView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readListOfObjectives",
            "/api/readListOfObjectives",
            ReadListOfObjectivesView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readListOfTemplates",
            "/api/readListOfTemplates",
            ReadListOfTemplatesView,
            None,
        )
    )
    routes.append(
        addRoute("addproject_api", "/api/createProject", CreateProjectView, None)
    )
    routes.append(
        addRoute("readProjects_api", "/api/readProjects", ReadProjectsView, "json")
    )
    routes.append(
        addRoute("updateproject_api", "/api/updateProject", updateProject_view, None)
    )
    routes.append(
        addRoute("deleteproject_api", "/api/deleteProject", DeleteProjectViewApi, None)
    )

    # Share project
    routes.append(
        addRoute(
            "readcollaborators_api",
            "/api/readCollaborators",
            ReadCollaboratorsView,
            "json",
        )
    )
    routes.append(
        addRoute(
            "addcollaborator_api", "/api/addCollaborator", AddCollaboratorView, None
        )
    )
    routes.append(
        addRoute(
            "deletecollaborator_api",
            "/api/deleteCollaborator",
            DeleteCollaboratorView,
            None,
        )
    )

    # Enumerators
    routes.append(
        addRoute(
            "addenumerator_api", "/api/createEnumerator", CreateEnumeratorView, None
        )
    )
    routes.append(
        addRoute(
            "readenumerators_api", "/api/readEnumerators", ReadEnumeratorsView, None
        )
    )
    routes.append(
        addRoute(
            "updateenumerator_api", "/api/updateEnumerator", UpdateEnumeratorView, None
        )
    )
    routes.append(
        addRoute(
            "modifypassenumerator_api",
            "/api/updatePasswordEnumerator",
            UpdatePasswordEnumeratorView,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteenumerator_api",
            "/api/deleteEnumerator",
            ApiDeleteEnumeratorView,
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
    # Groups
    routes.append(
        addRoute(
            "readcategoriesofquestions_api",
            "/api/readCategoriesOfQuestions",
            readGroupsOfQuestions_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "createcategoryofquestions_api",
            "/api/createCategoryOfQuestions",
            createGroupOfQuestion_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "updatecategoryofquestions_api",
            "/api/updateCategoryOfQuestions",
            updateGroupOfQuestion_view,
            None,
        )
    )
    routes.append(
        addRoute(
            "deletecategoryofquestions_api",
            "/api/deleteCategoryOfQuestions",
            deleteGroupOfQuestion_view,
            None,
        )
    )

    # Questions
    routes.append(
        addRoute("addquestion_api", "/api/createQuestion", CreateQuestionView, None)
    )
    routes.append(
        addRoute("readquestions_api", "/api/readQuestions", ReadQuestionsView, None)
    )
    routes.append(
        addRoute("updateQuestion_api", "/api/updateQuestion", UpdateQuestionView, None)
    )
    routes.append(
        addRoute(
            "deletequestion_api", "/api/deleteQuestion", DeleteQuestionViewApi, None
        )
    )
    routes.append(
        addRoute(
            "readquestionvalues_api",
            "/api/readQuestionValues",
            ReadQuestionValuesView,
            None,
        )
    )
    routes.append(
        addRoute(
            "addquestionvalues_api",
            "/api/addQuestionValues",
            AddQuestionValueViewApi,
            None,
        )
    )
    routes.append(
        addRoute(
            "updatequestionvalues_api",
            "/api/updateQuestionValues",
            UpdateQuestionValueView,
            None,
        )
    )
    routes.append(
        addRoute(
            "deletequestionvalues_api",
            "/api/deleteQuestionValues",
            DeleteQuestionValueViewApi,
            None,
        )
    )

    routes.append(
        addRoute(
            "updatequestionperformance_api",
            "/api/updateQuestionPerformance",
            UpdateQuestionPerformanceView,
            None,
        )
    )
    routes.append(
        addRoute(
            "updatequestioncharacteristics_api",
            "/api/updateQuestionCharacteristics",
            UpdateQuestionCharacteristicsView,
            None,
        )
    )

    routes.append(
        addRoute(
            "readMultiLanguagesFromQuestion",
            "/api/readMultiLanguagesFromQuestion",
            ReadMultiLanguagesFromQuestionView,
            None,
        )
    )

    routes.append(
        addRoute(
            "multiLanguageQuestion",
            "/api/multiLanguageQuestion",
            MultiLanguageQuestionView,
            None,
        )
    )

    # General phrases

    routes.append(
        addRoute(
            "readAllGeneralPhrases",
            "/api/readAllGeneralPhrases",
            ReadAllGeneralPhrasesView,
            None,
        )
    )

    routes.append(
        addRoute(
            "changeGeneralPhrases",
            "/api/changeGeneralPhrases",
            ChangeGeneralPhrasesView,
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
            AddProjectTechnologyView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjtechnologies",
            "/api/readProjectTechnologies",
            ReadProjectTechnologiesView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibletechnologies",
            "/api/readPossibleProjectTechnologies",
            ReadPossibleProjectTechnologiesView,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteprjtechnology",
            "/api/deleteProjectTechnology",
            DeleteProjectTechnologyView,
            None,
        )
    )

    routes.append(
        addRoute(
            "addprjtechnologyalias",
            "/api/addProjectTechnologyAlias",
            AddProjectTechnologyAliasView,
            None,
        )
    )
    routes.append(
        addRoute(
            "addprjtechnologyaliasextra",
            "/api/addProjectTechnologyAliasExtra",
            AddProjectTechnologyAliasExtraView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjtechnologiesalias",
            "/api/readProjectTechnologiesAlias",
            ReadProjectTechnologiesAliasView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjtechnologiesaliasextra",
            "/api/readProjectTechnologiesAliasExtra",
            ReadProjectTechnologiesAliasExtraView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibletechnologiesalias",
            "/api/readPossibleProjectTechnologiesAlias",
            ReadPossibleProjectTechnologiesAliasView,
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
            ReadProjectRegistryView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibleregistry",
            "/api/readPossibleQuestionsForRegistryGroup",
            ReadPossibleQuestionsForRegistryGroupView,
            None,
        )
    )
    routes.append(
        addRoute(
            "addregistrygroup", "/api/createRegistryGroup", AddRegistryGroupView, None
        )
    )
    routes.append(
        addRoute(
            "updateregistrygroup",
            "/api/updateRegistryGroup",
            UpdateRegistryGroupView,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteregistrygroup2",
            "/api/deleteRegistryGroup",
            DeleteRegistryGroupView,
            None,
        )
    )
    routes.append(
        addRoute(
            "addquestiontogroup",
            "/api/addQuestionToGroupRegistry",
            AddQuestionToGroupRegistryView,
            None,
        )
    )
    routes.append(
        addRoute(
            "deletequestionfromgroup",
            "/api/deleteQuestionFromGroupRegistry",
            DeleteQuestionFromGroupRegistryView,
            None,
        )
    )
    routes.append(
        addRoute(
            "orderregistryquestions",
            "/api/orderRegistryQuestions",
            OrderRegistryQuestionsView,
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
            "updateAvailabilityCombinations",
            "/api/setAvailabilityCombination",
            setAvailabilityCombination_view,
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

    routes.append(
        addRoute(
            "registrydatacleaning",
            "/api/registryDataCleaning",
            registryDataCleaning_view,
            None,
        )
    )

    routes.append(
        addRoute(
            "readregistrydata",
            "/api/readRegistryData",
            readRegistryData_view,
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
            ReadProjectAssessmentsView,
            None,
        )
    )
    routes.append(
        addRoute(
            "addnewassessment", "/api/createAssessment", AddNewAssessmentView, None
        )
    )
    routes.append(
        addRoute(
            "updateprjassessment",
            "/api/updateProjectAssessment",
            UpdateProjectAssessmentView,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteprjassessment",
            "/api/deleteProjectAssessment",
            DeleteProjectAssessmentView,
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
            ReadProjectAssessmentStructureView,
            None,
        )
    )
    routes.append(
        addRoute(
            "readprjpossibleassessment",
            "/api/readPossibleQuestionForAssessmentGroup",
            ReadPossibleQuestionForAssessmentGroupView,
            None,
        )
    )
    routes.append(
        addRoute(
            "addassessmentgroup",
            "/api/createAssessmentGroup",
            CreateAssessmentGroupView,
            None,
        )
    )
    routes.append(
        addRoute(
            "updateassessmentgroup",
            "/api/updateAssessmentGroup",
            UpdateAssessmentGroupView,
            None,
        )
    )
    routes.append(
        addRoute(
            "deleteassessmentgroup2",
            "/api/deleteAssessmentGroup",
            DeleteAssessmentGroupView,
            None,
        )
    )
    routes.append(
        addRoute(
            "orderassessmentquestion",
            "/api/orderAssessmentQuestions",
            OrderAssessmentQuestionsView,
            None,
        )
    )
    # Project Assessment questions
    routes.append(
        addRoute(
            "addquestiontogroupass",
            "/api/addQuestionToGroupAssessment",
            AddQuestionToGroupAssessmentView,
            None,
        )
    )
    routes.append(
        addRoute(
            "deletequestionfromgroupass",
            "/api/deleteQuestionFromGroupAssessment",
            DeleteQuestionFromGroupAssessmentView,
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

    routes.append(
        addRoute(
            "assessmentdatacleaning",
            "/api/assessmentDataCleaning",
            assessmentDataCleaning_view,
            None,
        )
    )

    routes.append(
        addRoute(
            "readassessmentdata",
            "/api/readAssessmentData",
            readAssessmentData_view,
            None,
        )
    )

    # Information of project
    routes.append(
        addRoute(
            "readDataOfProject",
            "/api/readDataOfProject",
            ReadDataOfProjectViewApi,
            None,
        )
    )

    # Information analyzes
    routes.append(
        addRoute(
            "readvariablesforanalysis",
            "/api/readVariablesForAnalysis",
            ReadVariablesForAnalysisViewApi,
            None,
        )
    )

    routes.append(
        addRoute(
            "createanalysisbyapi",
            "/api/generateAnalysisByApi",
            GenerateAnalysisByApiViewApi,
            None,
        )
    )

    # --------------------------------------------------------ClimMob Bot--------------------------------------------------------#

    # Chat
    routes.append(
        addRoute(
            "sendFeedbackToBot", "/bot/sendFeedbackToBot", sendFeedbackToBot_view, None
        )
    )

    routes.append(
        addRoute("readFeedback", "/bot/readFeedback", readFeedback_view, None)
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
