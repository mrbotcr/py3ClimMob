import climmob.resources as r
import os


def createResources(apppath, config):
    # Add core fanstatic library
    r.add_library("coreresources", os.path.join(apppath, "fanstatic"), config)

    # Add core CSS and JS
    r.add_css_resource("coreresources", "bootstrap", "inspinia/css/bootstrap.css")
    r.add_css_resource(
        "coreresources", "fontawesome", "inspinia/font-awesome/css/font-awesome.css"
    )
    r.add_css_resource(
        "coreresources", "toastr", "inspinia/css/plugins/toastr/toastr.min.css"
    )
    r.add_css_resource("coreresources", "animate", "inspinia/css/animate.css")
    r.add_css_resource("coreresources", "style", "inspinia/css/style.css")

    # CSS for landing page
    r.add_css_resource("coreresources", "landing", "landing/landing.css", "style")

    # register
    r.add_css_resource(
        "coreresources", "icheck", "inspinia/css/plugins/iCheck/custom.css", "style"
    )
    r.add_css_resource(
        "coreresources",
        "select2",
        "inspinia/css/plugins/select2/select2.min.css",
        "style",
    )

    # Project
    r.add_css_resource(
        "coreresources",
        "tags",
        "inspinia/css/plugins/bootstrap-tagsinput/bootstrap-tagsinput.css",
        "style",
    )

    # Question library
    r.add_css_resource(
        "coreresources",
        "datatables",
        "inspinia/css/plugins/dataTables/datatables.min.css",
        "style",
    )

    # Add/Modify question library
    r.add_css_resource(
        "coreresources",
        "switch",
        "inspinia/css/plugins/bootstrap-switch/bootstrap-switch.css",
        "tags",
    )
    r.add_css_resource(
        "coreresources", "shuffle", "inspinia/css/plugins/shuffle/test.css", "style"
    )
    # Registry and Assessment
    r.add_css_resource(
        "coreresources",
        "nestable",
        "inspinia/css/plugins/nestable/jquery.nestable.css",
        "style",
    )

    # Project technologies and aliases
    r.add_css_resource(
        "coreresources",
        "jqueryui",
        "inspinia/css/plugins/jQueryUI/jquery-ui-1.10.4.custom.min.css",
        "style",
    )

    # JQuery Steps
    r.add_css_resource(
        "coreresources", "jquerysteps", "project/combinations/combinations.css", "style"
    )

    # EditData
    r.add_css_resource(
        "coreresources",
        "jqgrid",
        "inspinia/css/plugins/jqGrid/ui.jqgrid.css",
        "jqueryui",
    )

    r.add_css_resource(
        "coreresources",
        "sweet",
        "inspinia/css/plugins/sweetalert/sweetalert.css",
        "jqgrid",
    )

    # Upload Data
    r.add_css_resource(
        "coreresources",
        "dropzone",
        "inspinia/css/plugins/dropzone/dropzone.css",
        "jqueryui",
    )

    # Progress
    r.add_css_resource("coreresources", "c3", "inspinia/css/plugins/c3/c3.min.css")
    r.add_library("progress", os.path.join(apppath, "templates/progress"), config)
    r.add_css_resource("progress", "bootstrap2", "bootstrap.css")
    r.add_css_resource("progress", "animate2", "animate.css", "bootstrap2")
    r.add_css_resource("progress", "style2", "style.css", "bootstrap2")
    # ----------------------------------------------------------------------------------------------------------

    # Add core JS
    r.add_js_resource(
        "coreresources", "jquery", "inspinia/js/jquery-3.1.1.min.js", None
    )
    r.add_js_resource(
        "coreresources", "bootstrap", "inspinia/js/bootstrap.js", "jquery"
    )

    # JS for landing page
    r.add_js_resource(
        "coreresources",
        "metismenu",
        "inspinia/js/plugins/metisMenu/jquery.metisMenu.js",
        "bootstrap",
    )
    r.add_js_resource(
        "coreresources",
        "slimscroll",
        "inspinia/js/plugins/slimscroll/jquery.slimscroll.min.js",
        "metismenu",
    )
    r.add_js_resource(
        "coreresources", "inspinia", "inspinia/js/inspinia.js", "slimscroll"
    )
    r.add_js_resource(
        "coreresources",
        "toastr",
        "inspinia/js/plugins/toastr/toastr.min.js",
        "inspinia",
    )
    r.add_js_resource(
        "coreresources", "pace", "inspinia/js/plugins/pace/pace.min.js", "toastr"
    )
    r.add_js_resource(
        "coreresources", "wow", "inspinia/js/plugins/wow/wow.min.js", "pace"
    )
    r.add_js_resource("coreresources", "landing", "landing/landing.js", "wow")

    # Dashboard
    r.add_js_resource(
        "coreresources", "dashboard", "dashboard/dashboard.js", "bootstrap"
    )

    # Register
    r.add_js_resource(
        "coreresources",
        "icheck",
        "inspinia/js/plugins/iCheck/icheck.min.js",
        "bootstrap",
    )
    r.add_js_resource(
        "coreresources",
        "select2",
        "inspinia/js/plugins/select2/select2.full.min.js",
        "bootstrap",
    )
    r.add_js_resource("coreresources", "register", "auth/register.js", "select2")

    # Edit profile
    r.add_js_resource(
        "coreresources", "editprofile", "profile/editprofile.js", "select2"
    )

    # Add/Edit Project Information
    r.add_js_resource(
        "coreresources",
        "tags",
        "inspinia/js/plugins/bootstrap-tagsinput/bootstrap-tagsinput.js",
        "bootstrap",
    )
    r.add_js_resource("coreresources", "addproject", "project/newproject.js", "tags")

    r.add_js_resource(
        "coreresources",
        "datatables",
        "inspinia/js/plugins/dataTables/datatables.min.js",
        "bootstrap",
    )
    r.add_js_resource("coreresources", "qlibrary", "question/library.js", "datatables")
    r.add_js_resource(
        "coreresources", "qvalues", "question/values/question_values.js", "datatables"
    )

    # Add/Edit question
    r.add_js_resource(
        "coreresources",
        "switch",
        "inspinia/js/plugins/bootstrap-switch/bootstrap-switch.js",
        "tags",
    )
    r.add_js_resource(
        "coreresources", "addquestion", "question/newquestion.js", "switch"
    )
    r.add_js_resource(
        "coreresources", "addoption", "question/values/add-option.js", "switch"
    )
    r.add_js_resource(
        "coreresources", "shuffle", "inspinia/js/plugins/shuffle/shuffle.js", "pace"
    )
    # Registry and Assessment
    r.add_js_resource(
        "coreresources",
        "nestable",
        "inspinia/js/plugins/nestable/jquery.nestable.js",
        "pace",
    )
    r.add_js_resource(
        "coreresources", "registry", "project/registry/registry.js", "nestable"
    )
    r.add_js_resource(
        "coreresources",
        "newregistryquestion",
        "project/registry/newregistryquestion.js",
        "datatables",
    )

    # Project technologies and aliases
    r.add_js_resource(
        "coreresources",
        "jqueryui",
        "inspinia/js/plugins/jquery-ui/jquery-ui.min.js",
        "pace",
    )
    r.add_js_resource(
        "coreresources",
        "prjtechnologies",
        "project/technologies/technologies.js",
        "pace",
    )
    r.add_js_resource(
        "coreresources", "prjtechaliases", "project/technologies/techaliases.js", "pace"
    )

    # Enumerators
    r.add_js_resource(
        "coreresources", "enumerators", "enumerator/enumerator.js", "pace"
    )
    r.add_js_resource("coreresources", "enulibrary", "enumerator/library.js", "pace")
    r.add_js_resource("coreresources", "delete", "delete.js", "pace")
    # Project combinations
    r.add_js_resource(
        "coreresources",
        "prjcombinations",
        "project/combinations/combinations.js",
        "datatables",
    )

    # Technologies library
    r.add_js_resource(
        "coreresources", "technologies", "technologies/technologies.js", "pace"
    )

    # Alias library
    r.add_js_resource("coreresources", "alias", "technologies/alias.js", "pace")

    # ProductsList
    r.add_js_resource(
        "coreresources",
        "concurrent",
        "project/productsList/Concurrent.Thread.js",
        "pace",
    )
    r.add_js_resource(
        "coreresources", "productsList", "project/productsList/productsList.js", "pace"
    )
    r.add_js_resource(
        "coreresources", "productsListaes", "project/productsList/aes.js", "pace"
    )

    # EditData
    r.add_js_resource(
        "coreresources",
        "gridl",
        "inspinia/js/plugins/jqGrid/i18n/grid.locale-en.js",
        "slimscroll",
    )
    r.add_js_resource(
        "coreresources",
        "jqgrid",
        "inspinia/js/plugins/jqGrid/jquery.jqGrid.min.js",
        "slimscroll",
    )
    r.add_js_resource(
        "coreresources",
        "sweet",
        "inspinia/js/plugins/sweetalert/sweetalert.min.js",
        "slimscroll",
    )
    r.add_js_resource(
        "coreresources", "editDatajq", "project/editData/editData.js", "slimscroll"
    )
    r.add_js_resource(
        "coreresources", "uploadDatajq", "project/editData/uploadData.js", "slimscroll"
    )

    # Assessments
    r.add_js_resource(
        "coreresources", "assessment_form", "assessment/assessment_form.js", None
    )

    # Analysis
    r.add_js_resource(
        "coreresources", "analysisData", "project/analysis/analysisData.js", None
    )

    # Progress
    r.add_js_resource(
        "coreresources", "c3", "inspinia/js/plugins//c3/c3.min.js", "jquery"
    )
    r.add_js_resource(
        "coreresources", "d3", "inspinia/js/plugins//d3/d3.min.js", "jquery"
    )
