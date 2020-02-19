import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.txt")) as f:
    CHANGES = f.read()

requires = [
    "pyramid",
    "pyramid_jinja2",
    "pyramid_debugtoolbar",
    "pyramid_tm",
    "SQLAlchemy",
    "transaction",
    "zope.sqlalchemy",
    "waitress",
    "WebHelpers2==2.0",
    "pyutilib== 5.4.1",
    "pyramid_fanstatic",
    "mysql-connector-python",
    "PyCrypto",
    "Babel",
    "lingua",
    "xlsxwriter",
    "arrow",
    "cookiecutter",
    "formencode",
    "alembic",
    "gunicorn",
    "gevent",
    "ago",
    "numpy",
    "lxml",
    "celery",
    "pypng",
    #'zbar',
    "pillow",
    "qrtools",
    "rutter",
    "qrcode",
]


tests_require = [
    "WebTest >= 1.3.1",  # py3 compat
    "pytest",
    "pytest-cov",
]

setup(
    name="climmob",
    version="4.0",
    description="Climmob",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Bioverity Internatioanl",
    author_email="c.f.quiros@cgiar.org",
    url="http://climmob.net",
    keywords="web pyramid pylons",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={"testing": tests_require,},
    install_requires=requires,
    entry_points={
        "paste.app_factory": ["main = climmob:main",],
        "console_scripts": [
            "initialize_climmob_db = climmob.scripts.initializedb:main",
        ],
    },
)
