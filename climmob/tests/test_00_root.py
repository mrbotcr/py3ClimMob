import datetime
import json
import os
import unittest
import pkg_resources


"""
This testing module test all routes. It launch start the server and test all the routes and processes
We allocated all in one massive test because separating them in different test functions load 
the environment processes multiple times and crash ClimMob.
   
"""


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        pkg_resources.require("climmob")
        if os.environ.get("CLIMMOB_PYTEST_RUNNING", "false") == "false":
            raise ValueError(
                "Environment variable CLIMMOB_PYTEST_RUNNING must be true. "
                "Do 'export CLIMMOB_PYTEST_RUNNING=true' before running PyTest"
            )
        # config_file = os.path.join(
        #     os.path.dirname(os.path.abspath(__file__)), *["test_config.json"]
        # )
        with open(
            "/home/cquiros/data/projects2017/climmob/software/py3ClimMob/climmob/tests/test_config.json"
        ) as json_file:
            server_config = json.load(json_file)

        from climmob import main

        from pathlib import Path

        home = str(Path.home())

        paths2 = ["climmob_pytest"]
        working_dir = os.path.join(home, *paths2)
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)

        print("***************Before")
        app = main(None, **server_config)
        print("***************After")
        from webtest import TestApp

        self.testapp = TestApp(app)
        self.randonLogin = ""
        self.randonLoginKey = ""
        self.server_config = server_config
        self.path = (
            "/home/cquiros/data/projects2017/climmob/software/py3ClimMob/climmob/tests"
        )
        self.working_dir = working_dir

    def test_all(self):
        def test_root():
            # Test the root urls
            self.testapp.get("/", status=200)

        def test_login():
            self.testapp.get("/login", status=200)

        start_time = datetime.datetime.now()
        print("Testing root")
        test_root()
        test_login()

        end_time = datetime.datetime.now()
        time_delta = end_time - start_time
        total_seconds = time_delta.total_seconds()
        minutes = total_seconds / 60
        print("Finished in {} minutes".format(minutes))
