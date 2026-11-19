"""Outils communs aux tests : une base SQLite temporaire par test."""

import os
import tempfile
import unittest

from service import ServiceBibliotheque


class BaseTest(unittest.TestCase):
    """Crée un service branché sur une base temporaire, supprimée après le test."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.temp.name, "test.db")
        self.service = ServiceBibliotheque(self.db)
        self.service.initialiser()

    def tearDown(self) -> None:
        self.temp.cleanup()
