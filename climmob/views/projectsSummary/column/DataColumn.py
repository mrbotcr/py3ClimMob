from climmob.utility.project import (
    project_climmob_analytics_get_dict,
    project_active_get_dict,
    project_checked_get_dict,
)
from climmob.views.projectsSummary.column.Column import Column

options_dict = project_climmob_analytics_get_dict()
option_dict_y_n = project_active_get_dict()
options_dict_checked = project_checked_get_dict()

DATA_COLUMNS = [
    {
        "key": "user_owner",
        "name": "Owner",
        "type": "static",
        "options": None,
        "id": 0,
        "show": False,
    },
    {
        "key": "project_id",
        "name": "ID",
        "type": "static",
        "options": None,
        "id": 1,
        "show": True,
    },
    {
        "key": "project_cod",
        "name": "COD",
        "type": "static",
        "options": None,
        "id": 2,
        "show": False,
    },
    {
        "key": "projectTitle",
        "name": "Name",
        "type": "static",
        "options": None,
        "id": 3,
        "show": True,
    },
    # {"key": "projectDesc", "name": "Description", "type": "static", "options": None, "id": 4, "show": True},
    {
        "key": "project_pi",
        "name": "Coordinator",
        "type": "static",
        "options": None,
        "id": 5,
        "show": True,
    },
    {
        "key": "project_piorganization",
        "name": "Organization",
        "type": "static",
        "options": None,
        "id": 6,
        "show": False,
    },
    {
        "key": "project_piemail",
        "name": "Email",
        "type": "static",
        "options": None,
        "id": 7,
        "show": False,
    },
    {
        "key": "project_date",
        "name": "Date",
        "type": "static",
        "options": None,
        "id": 8,
        "show": True,
    },
    {
        "key": "project_country",
        "name": "Country",
        "type": "static",
        "options": None,
        "id": 9,
        "show": True,
    },
    {
        "key": "project_location",
        "name": "Location",
        "type": "static",
        "options": None,
        "id": 10,
        "show": False,
    },
    # {
    #     "key": "farmers_target",
    #     "name": "Target farmers",
    #     "type": "static",
    #     "options": None,
    #     "id": 11,
    #     "show": False,
    # },
    {
        "key": "farmers_registered",
        "name": "N Participants",
        "type": "static",
        "options": None,
        "id": 12,
        "show": True,
    },
    {
        "key": "gender_man",
        "name": "N man",
        "type": "static",
        "options": None,
        "id": 13,
        "show": False,
    },
    {
        "key": "gender_woman",
        "name": "N woman",
        "type": "static",
        "options": None,
        "id": 14,
        "show": False,
    },
    {
        "key": "gender_other",
        "name": "N other gender",
        "type": "static",
        "options": None,
        "id": 15,
        "show": False,
    },
    {
        "key": "gender_unreported",
        "name": "N unreported gender",
        "type": "static",
        "options": None,
        "id": 16,
        "show": False,
    },
    {
        "key": "technology",
        "name": "Technology",
        "type": "static",
        "options": None,
        "id": 17,
        "show": False,
    },
    {
        "key": "scientific_name",
        "name": "Scientific name",
        "type": "static",
        "options": None,
        "id": 18,
        "show": True,
    },
    {
        "key": "startDate",
        "name": "Start date",
        "type": "static",
        "options": None,
        "id": 19,
        "show": False,
    },
    {
        "key": "endDate",
        "name": "End date",
        "type": "static",
        "options": None,
        "id": 20,
        "show": False,
    },
    # {"key": "instance_name", "name": "Instance", "type": "static", "options": None, "id": 21, "show": False},
    {
        "key": "varieties_quantity",
        "name": "N varieties",
        "type": "static",
        "options": None,
        "id": 22,
        "show": False,
    },
    # {
    #     "key": "LatitudeRegistry",
    #     "name": "Reference latitude of trial registration location",
    #     "type": "static",
    #     "options": None,
    #     "id": 23,
    #     "show": False,
    # },
    # {
    #     "key": "LongitudeRegistry",
    #     "name": "Reference longitude of trial registration location",
    #     "type": "static",
    #     "options": None,
    #     "id": 24,
    #     "show": False,
    # },
    # {
    #     "key": "LatitudeAssessment",
    #     "name": "Reference latitude of trial implementation location",
    #     "type": "static",
    #     "options": None,
    #     "id": 25,
    #     "show": False,
    # },
    # {
    #     "key": "LongitudeAssessment",
    #     "name": "Reference longitude of trial implementation location",
    #     "type": "static",
    #     "options": None,
    #     "id": 26,
    #     "show": False,
    # },
    {
        "key": "project_status",
        "name": "Status",
        "type": "static",
        "options": None,
        "id": 27,
        "show": True,
    },
    {
        "key": "project_type",
        "name": "Type",
        "type": "static",
        "options": None,
        "id": 28,
        "show": True,
    },
    {
        "key": "project_experimental_site",
        "name": "Experimental site",
        "type": "static",
        "options": None,
        "id": 29,
        "show": False,
    },
    {
        "key": "project_unit_of_analysis",
        "name": "Unit of analysis",
        "type": "static",
        "options": None,
        "id": 30,
        "show": False,
    },
    {
        "key": "project_objective",
        "name": "Objective",
        "type": "static",
        "options": None,
        "id": 31,
        "show": False,
    },
    {
        "key": "project_active",
        "name": "Project active",
        "type": "static",
        "options": option_dict_y_n,
        "id": 32,
        "show": False,
    },
    {
        "key": "affiliation",
        "name": "Affiliation",
        "type": "input",
        "options": None,
        "id": 33,
        "show": True,
    },
    {
        "key": "cropname",
        "name": "Cropname",
        "type": "input",
        "options": None,
        "id": 34,
        "show": True,
    },
    {
        "key": "climmob_analytics",
        "name": "Dashboard",
        "type": "dropdown",
        "options": options_dict,
        "id": 35,
        "show": True,
    },
    {
        "key": "project_checked",
        "name": "Revised",
        "type": "static",
        "options": options_dict_checked,
        "id": 36,
        "show": True,
    },
    {
        "key": "admin_user_name",
        "name": "Last update by",
        "type": "static",
        "options": None,
        "id": 37,
        "show": False,
    },
    {
        "key": "admin_update_date",
        "name": "Date modification",
        "type": "static",
        "options": None,
        "id": 38,
        "show": False,
    },
]


class DataColumn:
    def get_project_summary_columns(self):

        keys = DataColumn.get_key_project_summary(self)

        existing_keys = set(keys)
        keys_seen = set()
        validated_columns = []
        errors = []
        for col_dict in DATA_COLUMNS:
            key = col_dict.get("key")
            if key in keys_seen:
                errors.append(f"Duplicate key found: '{key}'")
                continue
            keys_seen.add(key)
            try:
                col = Column(**col_dict, existing_keys=existing_keys)
                validated_columns.append(col)
            except ValueError as e:
                errors.append(f"Error on the column '{col_dict['key']}': {e}")
        if errors:
            raise ValueError("\n".join(errors))

        return validated_columns

    def get_key_project_summary(self):
        keys = []
        for key in DATA_COLUMNS:
            keys.append(key["key"])
        return keys
