from climmob.utility.project import (
    project_climmob_analytics_get_dict,
    project_active_get_dict,
)
from climmob.views.projectsSummary.column.Column import Column

options_dict = project_climmob_analytics_get_dict()
option_dict_y_n = project_active_get_dict()

DATA_COLUMNS = [
    {
        "key": "user_owner",
        "name": "User owner",
        "type": "static",
        "options": None,
        "id": 0,
        "show": True,
    },
    {
        "key": "project_id",
        "name": "ID (Internal)",
        "type": "static",
        "options": None,
        "id": 1,
        "show": True,
    },
    {
        "key": "project_cod",
        "name": "Project ID",
        "type": "static",
        "options": None,
        "id": 2,
        "show": True,
    },
    # {"key": "projectTitle", "name": "Name", "type": "static", "options": None, "id": 3, "show": True},
    # {"key": "projectDesc", "name": "Project Description", "type": "static", "options": None, "id": 4, "show": True},
    {
        "key": "project_pi",
        "name": "Trial coordinator",
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
        "show": True,
    },
    {
        "key": "project_piemail",
        "name": "Trial coordinator's email",
        "type": "static",
        "options": None,
        "id": 7,
        "show": True,
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
        "show": True,
    },
    {
        "key": "farmers_target",
        "name": "Number of farmers target",
        "type": "static",
        "options": None,
        "id": 11,
        "show": True,
    },
    {
        "key": "farmers_registered",
        "name": "Number of registered for the project",
        "type": "static",
        "options": None,
        "id": 12,
        "show": True,
    },
    {
        "key": "gender_man",
        "name": "Gender - Men",
        "type": "static",
        "options": None,
        "id": 13,
        "show": True,
    },
    {
        "key": "gender_woman",
        "name": "Gender - Women",
        "type": "static",
        "options": None,
        "id": 14,
        "show": True,
    },
    {
        "key": "gender_other",
        "name": "Gender - Other",
        "type": "static",
        "options": None,
        "id": 15,
        "show": True,
    },
    {
        "key": "gender_unreported",
        "name": "Gender - Unreported",
        "type": "static",
        "options": None,
        "id": 16,
        "show": True,
    },
    {
        "key": "crop",
        "name": "Crop",
        "type": "static",
        "options": None,
        "id": 17,
        "show": True,
    },
    {
        "key": "technology",
        "name": "Technology",
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
        "show": True,
    },
    {
        "key": "endDate",
        "name": "End date",
        "type": "static",
        "options": None,
        "id": 20,
        "show": True,
    },
    # {"key": "instance_name", "name": "Instance Name", "type": "static", "options": None, "id": 21, "show": True},
    {
        "key": "varieties_quantity",
        "name": "Varieties Quantity",
        "type": "static",
        "options": None,
        "id": 22,
        "show": True,
    },
    {
        "key": "LatitudeRegistry",
        "name": "Latitude Registry",
        "type": "static",
        "options": None,
        "id": 23,
        "show": True,
    },
    {
        "key": "LongitudeRegistry",
        "name": "Longitude Registry",
        "type": "static",
        "options": None,
        "id": 24,
        "show": True,
    },
    {
        "key": "LatitudeAssessment",
        "name": "Latitude Assessment",
        "type": "static",
        "options": None,
        "id": 25,
        "show": True,
    },
    {
        "key": "LongitudeAssessment",
        "name": "Longitude Assessment",
        "type": "static",
        "options": None,
        "id": 26,
        "show": True,
    },
    {
        "key": "project_active",
        "name": "Active",
        "type": "static",
        "options": option_dict_y_n,
        "id": 27,
        "show": True,
    },
    {
        "key": "project_continent",
        "name": "Continent",
        "type": "static",
        "options": None,
        "id": 28,
        "show": True,
    },
    {
        "key": "project_status",
        "name": "Status",
        "type": "static",
        "options": None,
        "id": 29,
        "show": True,
    },
    {
        "key": "project_type",
        "name": "Type",
        "type": "static",
        "options": None,
        "id": 30,
        "show": True,
    },
    {
        "key": "project_experimental_site",
        "name": "Experimental site",
        "type": "static",
        "options": None,
        "id": 31,
        "show": True,
    },
    {
        "key": "project_unit_of_analysis",
        "name": "Unit of analysis",
        "type": "static",
        "options": None,
        "id": 32,
        "show": True,
    },
    {
        "key": "project_objective",
        "name": "Objective",
        "type": "static",
        "options": None,
        "id": 33,
        "show": True,
    },
    {
        "key": "affiliation",
        "name": "Affiliation",
        "type": "input",
        "options": None,
        "id": 34,
        "show": True,
    },
    {
        "key": "cropname",
        "name": "Curated crop name",
        "type": "input",
        "options": None,
        "id": 35,
        "show": True,
    },
    {
        "key": "climmob_analytics",
        "name": "Dashboard",
        "type": "dropdown",
        "options": options_dict,
        "id": 36,
        "show": True,
    },
]


def get_project_summary_columns():

    keys = get_key_project_summary()

    existing_keys = set(keys)
    validated_columns = []
    errors = []
    for col_dict in DATA_COLUMNS:
        try:
            col = Column(**col_dict, existing_keys=existing_keys)
            validated_columns.append(col)
        except ValueError as e:
            errors.append(f"Error on the column '{col_dict['key']}': {e}")
    if errors:
        print("ERRORS:", errors)
        return errors

    return validated_columns


def get_key_project_summary():
    keys = []
    for key in DATA_COLUMNS:
        keys.append(key["key"])
    return keys
