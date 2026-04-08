import logging
import re
from datetime import datetime, date

from climmob.processes import (
    getRegistryQuestions,
    getProjectAssessments,
    getAssessmentQuestions,
)

log = logging.getLogger(__name__)

from climmob.models.repository import sql_execute, sql_fetch_all

from climmob.processes.db.project import (
    get_project_cod_by_id,
    getProjectData,
)
from climmob.processes.db.userproject import (
    get_owner_user_name_by_project_id,
)
from climmob.processes.db.anonymization_params import get_anonymization_params_as_dict
from climmob.processes.db.question import (
    get_sensitive_questions_anonymity_by_project_id,
)
from climmob.processes.db.results import (
    getJSONResult,
    get_registry_submission_count,
    get_assessment_submission_count,
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
    "get_anonymized_count",
    "get_anonymization_percentage",
]


def add_to_anonymization_summary(summary: dict, field, reg_id: str, ignored: bool):
    field_name = field["form_name"] + "_" + field["field_name"]
    if field_name not in summary:
        summary[field_name] = {"anonymized": [], "ignored": []}
    if ignored:
        summary[field_name]["ignored"].append(reg_id)
    else:
        summary[field_name]["anonymized"].append(reg_id)


def reduce_anonymization_summary(summary: dict):
    for field_name, info in summary.items():
        info["anonymized"] = summarize_int_list(info["anonymized"])
        info["ignored"] = summarize_int_list(info["ignored"])


def summarize_int_list(lst: list):
    if not lst:
        return None
    lst = sorted(lst, key=lambda x: int(x))
    summarized = []
    start = lst[0]
    end = lst[0]
    for i in range(1, len(lst)):
        if int(lst[i]) == int(end) + 1:
            end = lst[i]
        else:
            if start == end:
                summarized.append(str(start))
            else:
                summarized.append(f"{start}-{end}")
            start = lst[i]
            end = lst[i]
    if start == end:
        summarized.append(str(start))
    else:
        summarized.append(f"{start}-{end}")
    return ", ".join(summarized)


def show_anonymization_summary(summary: dict, project_code, project_id, user_owner):
    print(
        f"Anonymization summary for project {user_owner}/{project_code} ({project_id}):"
    )
    for field_name, info in summary.items():
        print(
            f'"{field_name}"\t\tanonymized: {info["anonymized"]}; \t\tignored: {info["ignored"]}'
        )


def anonymize_project(project_id, request):
    project_code = get_project_cod_by_id(project_id, request)
    user_owner = get_owner_user_name_by_project_id(project_id, request)
    questions = get_sensitive_questions_anonymity_by_project_id(project_id, request)

    matches = {q.question_code: False for q in questions}

    project_collected_data = getJSONResult(
        user_owner, project_id, project_code, request
    )["data"]

    schema = user_owner + "_" + project_code

    summary = {}

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

            if not question:
                continue

            matches[question.question_code] = True

            if question.question_anonymity == QuestionAnonymity.REMOVE.value:
                continue

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
                    "form_name": match.group(1),
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
                    add_to_anonymization_summary(summary, field, reg_id, True)
                    continue
                return False, msg
            add_to_anonymization_summary(summary, field, reg_id, False)

    for q_code, matched in matches.items():
        if not matched:
            log.warning(
                f"Question with code {q_code} was not matched with any field in the collected data."
            )

    reduce_anonymization_summary(summary)
    show_anonymization_summary(summary, project_code, project_id, user_owner)

    return True, ""


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
        return True, ""

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
            float(geo_point[0]), float(geo_point[1]), 2000, 5000
        )
        field["value"] = " ".join([str(p) for p in geo_point])

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


def get_anonymized_count(schema):
    query = f"""
    SELECT 
        COUNT(*) AS count 
    FROM 
        {schema}.anonymized
    """

    result = sql_fetch_all(query)
    return result[0]["count"]


def get_anonymization_percentage(project_id: str, request) -> float:
    """
    Checks against form structure to calculate percentage based on number
    of fields that should be anonymized.
    Also considers that some fields might be anonymized and others not,
    so it calculates the percentage based on the number of fields that are
    anonymized vs the total number of fields that should be anonymized.
    """
    project_code = get_project_cod_by_id(project_id, request)
    user_owner = get_owner_user_name_by_project_id(project_id, request)

    projectDetails = getProjectData(project_id, request)

    if projectDetails["project_regstatus"] == 0:
        print("Registry not started yet. Anonymization percentage is 0%.")
        return 0

    reg_count = get_registry_submission_count(user_owner, project_code)

    counts = {"-": reg_count}

    expected_count = 0

    projectLabels = [
        projectDetails["project_label_a"],
        projectDetails["project_label_b"],
        projectDetails["project_label_c"],
    ]
    registry_questions = getRegistryQuestions(
        user_owner,
        project_id,
        request,
        projectLabels,
        onlyShowTheBasicQuestions=True,
    )
    questions = []
    for q in registry_questions:
        if not q["question_sensitive"] or q["question_sensitive"] == 0:
            continue
        new = {
            "form_id": "-",
            "question_code": q["question_code"],
        }
        questions.append(new)
        if q["question_anonymity"] != QuestionAnonymity.REMOVE.value:
            expected_count += reg_count

    assessments = getProjectAssessments(project_id, request)

    for assessment in assessments:
        if assessment["ass_status"] == 0:
            continue
        code = assessment["ass_cod"]
        count = get_assessment_submission_count(user_owner, project_code, code)
        counts[code] = count
        assessment_questions = getAssessmentQuestions(
            user_owner,
            project_id,
            code,
            request,
            projectLabels,
            onlyShowTheBasicQuestions=True,
        )

        for q in assessment_questions:
            if not q["question_sensitive"] or q["question_sensitive"] == 0:
                continue
            new = {
                "form_id": code,
                "question_code": q["question_code"],
            }
            questions.append(new)
            if q["question_anonymity"] != QuestionAnonymity.REMOVE.value:
                expected_count += count
    found_count = get_anonymized_count(user_owner + "_" + project_code)
    return found_count / expected_count * 100 if expected_count > 0 else 0
