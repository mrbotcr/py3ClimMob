import argparse
import configparser
import os

from jinja2 import Environment, FileSystemLoader


def get_section(ini_file, section):
    try:
        config = configparser.ConfigParser()
        config.read(ini_file)
        return dict(config.items(section))
    except Exception as e:
        print(
            "Warning: Unable to read section {}. Empty dict was return".format(
                section, str(e)
            )
        )
        return {}


def get_ini_value(ini_file, key, default=None, section="app:climmob"):
    try:
        config = configparser.ConfigParser()
        config.read(ini_file)
        return config.get(section, key)
    except Exception as e:
        print("Warning: Unable to find key {}. {} . Default used".format(key, str(e)))
        return default


def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("ini_path", help="Path to ini file")
    parser.add_argument("climmob_path", help="Path to ClimMob")
    parser.add_argument(
        "--json_file",
        default="",
        help="JSON file to create. By default is [climmob_path/climmob/tests/test_config.json]",
    )
    args = parser.parse_args(raw_args)

    if not os.path.exists(os.path.abspath(args.ini_path)):
        print("Ini file does not exists")
        return 1
    if not os.path.exists(os.path.abspath(args.climmob_path)):
        print("Path to climmob does not exits")
        return 1

    climmob_path = os.path.abspath(args.climmob_path)

    if args.json_file == "":
        json_file = os.path.join(
            climmob_path, *["climmob", "tests", "test_config.json"]
        )
    else:
        json_file = args.json_file

    mysql_cnf = os.path.join(climmob_path, *["mysql.cnf"])
    r_scripts = os.path.join(climmob_path, *["r"])
    r_random_script = os.path.join(climmob_path, *["r", "Random.R"])

    template_environment = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(climmob_path, "templates")),
        trim_blocks=False,
    )
    sqlalchemy_url = get_ini_value(os.path.abspath(args.ini_path), "sqlalchemy.url", "")

    r_analysis_script = get_ini_value(
        os.path.abspath(args.ini_path), "r.analysis.script", ""
    )

    user_repository = get_ini_value(
        os.path.abspath(args.ini_path), "user.repository", ""
    )
    odktools_path = get_ini_value(os.path.abspath(args.ini_path), "odktools.path", "")

    mysql_host = get_ini_value(
        os.path.abspath(args.ini_path), "odktools.mysql.host", "localhost"
    )
    mysql_port = get_ini_value(
        os.path.abspath(args.ini_path), "odktools.mysql.port", "3306"
    )
    mysql_user = get_ini_value(
        os.path.abspath(args.ini_path), "odktools.mysql.user", "empty!"
    )
    mysql_password = get_ini_value(
        os.path.abspath(args.ini_path), "odktools.mysql.password", "empty!"
    )

    context = {
        "mysql_host": mysql_host,
        "mysql_port": mysql_port,
        "mysql_user": mysql_user,
        "mysql_password": mysql_password,
        "sqlalchemy_url": sqlalchemy_url,
        "user_repository": user_repository,
        "odktools_path": odktools_path,
        "mysql_cnf": mysql_cnf,
        "r_scripts": r_scripts,
        "r_random_script": r_random_script,
        "r_analysis_script": r_analysis_script,
    }

    rendered_template = template_environment.get_template("test_config.jinja2").render(
        context
    )

    with open(json_file, "w") as f:
        f.write(rendered_template)
    return 0
