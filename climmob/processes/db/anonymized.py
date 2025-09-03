import re
from datetime import datetime, date

from climmob.models.repository import sql_execute
from climmob.processes.db.anonymization_params import get_anonymization_params_as_dict
from climmob.processes.db.question import (
    get_sensitive_questions_anonymity_by_project_id,
)
from climmob.utility import (
    get_question_by_field_name,
    QuestionAnonymity,
    add_noise_to_gps_coordinates,
    QuestionType,
)

__all__ = [
    "anonymize_questions",
    "delete_anonymized_values_by_form_id",
    "delete_anonymized_values_by_form_id_and_reg_id",
    "update_anonymized",
    "anonymize_project",
    "is_project_anonymized",
]


def anonymize_project(user_owner, project_id, project_code, request):
    from climmob.processes import getJSONResult

    questions = get_sensitive_questions_anonymity_by_project_id(project_id, request)

    project_collected_data = getJSONResult(
        user_owner, project_id, project_code, request
    )["data"]

    schema = user_owner + "_" + project_code

    pattern = r"(REG|(ASS(.+?)))_(.*)"
    for entry in project_collected_data:
        reg_id = entry["REG_qst162"]
        to_anonymize = []
        for key in entry.keys():
            if entry[key] is None:
                continue
            match = re.match(pattern, key)
            if match is None:
                continue
            question = get_question_by_field_name(match.group(4), questions)
            if (
                question
                and question.question_anonymity != QuestionAnonymity.REMOVE.value
            ):
                if match.group(1) == "REG":
                    form_id = "-"
                else:
                    form_id = match.group(3)
                to_anonymize.append(
                    {
                        "field_name": match.group(4),
                        "value": entry[key],
                        "question": question,
                        "form_id": form_id,
                    }
                )

        for field in to_anonymize:
            anonymize_field_value(field, reg_id, request)
            success, msg = insert_anonymized_field(
                field, field["form_id"], reg_id, schema
            )
            if not success:
                if msg.startswith("Duplicate entry for package"):
                    # To ignore entries that are already anonymized
                    continue
                return False, msg

    return project_collected_data


def anonymize_questions(request, form, form_id, project_id, user_owner, project_cod):
    questions = get_sensitive_questions_anonymity_by_project_id(project_id, request)

    registry_id = None

    schema = user_owner + "_" + project_cod

    pattern = r"grp_\d+/(.+)"
    to_anonymize = []

    for key in form.keys():
        match = re.fullmatch(pattern, key)
        if not match:
            continue
        field_name = match.group(1)

        if field_name == "QST162" or field_name == "QST163":
            match = re.fullmatch(rf"({user_owner}-)?(\d+)(-{project_cod}~)?", form[key])
            if not match:
                return False, "Could not anonymize"
            registry_id = match.group(2)
            continue

        question = get_question_by_field_name(field_name, questions)
        if question and question.question_anonymity != QuestionAnonymity.REMOVE.value:
            to_anonymize.append(
                {"field_name": field_name, "value": form[key], "question": question}
            )

    if not to_anonymize:
        return True

    for field in to_anonymize:
        anonymize_field_value(field, registry_id, request)
        success, msg = insert_anonymized_field(field, form_id, registry_id, schema)
        if not success:
            return False, msg

    return True, ""


def anonymize_field_value(field, registry_id, request):
    params = get_anonymization_params_as_dict(field["question"].question_id, request)
    if field["question"].question_anonymity == QuestionAnonymity.PSEUDONYM.value:
        field["value"] = params["pseudonym"].replace("{}", registry_id)
    elif field["question"].question_anonymity == QuestionAnonymity.RANGE.value:
        if field["question"].question_dtype == QuestionType.INTEGER.value:
            parser = int
        else:
            parser = float

        field["value"] = parser(field["value"])
        params["lower_bound"] = parser(params["lower_bound"])
        params["upper_bound"] = parser(params["upper_bound"])
        params["interval"] = parser(params["interval"])

        if field["value"] < params["lower_bound"]:
            field["value"] = f'<{params["lower_bound"]}'
        elif field["value"] > params["upper_bound"]:
            field["value"] = f'>{params["upper_bound"]}'
        else:
            i = params["lower_bound"]
            while i < params["upper_bound"]:
                if i <= field["value"] < (i + params["interval"]):
                    field["value"] = f'{i}-{i + params["interval"]}'
                    break
                i += params["interval"]
    elif field["question"].question_anonymity == QuestionAnonymity.MONTH_YEAR.value:
        dt = datetime.fromisoformat(field["value"])
        field["value"] = dt.strftime("%Y-%m")
    elif field["question"].question_anonymity == QuestionAnonymity.NOISE.value:
        geo_point = field["value"].split()
        geo_point[0], geo_point[1] = add_noise_to_gps_coordinates(
            float(geo_point[0]), float(geo_point[1]), 3000
        )
        if geo_point[0] == "Error" or geo_point[1] == "Error":
            return False, "Could not anonymize GeoPoint"
        field["value"] = " ".join(geo_point)

    return True, ""


def insert_anonymized_field(field, form_id, registry_id, schema):
    sql_insert_value = (
        f"("
        f"'{form_id}', "
        f"'{registry_id}', "
        f"'{field['field_name']}', "
        f"'{field['value']}'"
        f")"
    )
    sql = f"INSERT INTO {schema}.anonymized VALUES {sql_insert_value}"
    try:
        sql_execute(sql)
        return True, ""
    except Exception as e:
        match = re.search(rf"Duplicate entry '({form_id})-(\d+)-(.+?)'", str(e))
        if match:
            form_name = "registry" if form_id == "-" else f"assessment '{form_id}'"
            msg = f"Duplicate entry for package '{match.group(2)}' in {form_name}"
            return False, msg
        return False, ""


def update_anonymized(to_anonymize, schema, form_id, registry_id, request, current):
    for field in to_anonymize:
        db_type = type(current[field["field_name"]])
        if db_type == date:
            new_value = date.fromisoformat(field["value"])
        elif db_type == datetime:
            new_value = datetime.fromisoformat(field["value"])
        else:
            new_value = db_type(field["value"])
        if current[field["field_name"]] == new_value:
            # Only changed values will be updated to avoid recalculating anonymizations
            continue
        anonymize_field_value(field, registry_id, request)
        success, msg = update_anonymized_field(field, form_id, registry_id, schema)
        if not success:
            return False, msg
    return True, ""


def update_anonymized_field(field, form_id, registry_id, schema):
    sql = (
        f"UPDATE {schema}.anonymized SET value='{field['value']}' "
        f"WHERE form_id='{form_id}' "
        f"AND reg_id='{registry_id}' "
        f"AND col_name='{field['field_name']}'"
    )
    try:
        sql_execute(sql)
        return True, ""
    except Exception as e:
        return False, str(e)


def delete_anonymized_values_by_form_id(schema, form_id):
    sql = f"DELETE FROM {schema}.anonymized where form_id='{form_id}'"
    sql_execute(sql)


def delete_anonymized_values_by_form_id_and_reg_id(schema, form_id, reg_id):
    query = (
        f"DELETE FROM {schema}.anonymized "
        f"WHERE form_id='{form_id}' "
        f"AND reg_id='{reg_id}'"
    )
    sql_execute(query)


def is_project_anonymized(schema):
    query = f"""
    SELECT 
        (SELECT 
                COUNT(DISTINCT reg_id) AS count 
            FROM 
                {schema}.anonymized 
            WHERE 
                form_id = '-') = (SELECT 
                COUNT(qst162) AS count 
            FROM 
                {schema}.REG_geninfo) AS count_matches """

    result = sql_execute(query).first()
    return result["count_matches"] == 1
