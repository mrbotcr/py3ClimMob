import sys
import os
from jinja2 import Environment, FileSystemLoader

def main():
    if len(sys.argv) == 2:
        climmob_path = os.path.dirname(os.path.abspath(sys.argv[1]))
        climmob_ini_file = os.path.join(climmob_path,os.path.basename(sys.argv[1]))
        climmob_celery_app = os.path.join(climmob_path,*['climmob','config','celery_app.py'])

        PATH = os.path.dirname(os.path.abspath(__file__))
        TEMPLATE_ENVIRONMENT = Environment(autoescape=False,
                                           loader=FileSystemLoader(os.path.join(PATH, 'templates')),
                                           trim_blocks=False)

        context = {
            'CLIMMOB_INI_FILE': climmob_ini_file
        }

        rendered_template = TEMPLATE_ENVIRONMENT.get_template('celery_app_template.py').render(context)

        with open(climmob_celery_app, 'w') as f:
            f.write(rendered_template)

if __name__ == "__main__":
    main()