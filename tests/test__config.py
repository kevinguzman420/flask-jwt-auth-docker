from flask import current_app
import pytest
from . import BaseTestClass
from app import create_app

class TestTestingConfig(BaseTestClass):

    @pytest.mark.skip(reason="only test by testing config")
    def test_app_is_testing(self):
        self.app = create_app(settings_module="config.testing")
        with self.app.app_context():
            self.assertTrue(self.app.config["DEBUG"] is True)
            self.assertTrue(self.app.config["SECRET_KEY"] is not None)
            self.assertFalse(current_app is None)
            self.assertTrue(current_app.config["SQLALCHEMY_DATABASE_URI"] == "postgresql://postgres:kevinguzman@localhost:4000/tokenbasedauthtestingdb")


class TestDevelpmentConfig(BaseTestClass):

    @pytest.mark.skip(reason="only test by dev config")
    def test_app_is_development(self):
        self.app = create_app(settings_module="config.dev")
        with self.app.app_context():
            self.assertFalse(current_app is None)
            self.assertTrue(current_app.config["SQLALCHEMY_DATABASE_URI"] == "postgresql://postgres:kevinguzman@localhost:4000/tokenbasedauthdb")
