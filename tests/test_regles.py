"""Tests des règles métier (aucune base de données nécessaire)."""

import unittest
from datetime import date

import regles


class TestRegles(unittest.TestCase):

    def test_constantes(self):
        self.assertEqual(regles.DUREE_EMPRUNT, 14)
        self.assertEqual(regles.MAX_EMPRUNTS, 3)

    def test_livre_disponible(self):
        self.assertTrue(regles.livre_disponible(False))
        self.assertFalse(regles.livre_disponible(True))

    def test_peut_emprunter(self):
        self.assertTrue(regles.peut_emprunter(0))
        self.assertTrue(regles.peut_emprunter(2))
        self.assertFalse(regles.peut_emprunter(3))

    def test_date_retour_prevue(self):
        self.assertEqual(
            regles.date_retour_prevue(date(2026, 1, 1)), date(2026, 1, 15)
        )

    def test_calculer_retard(self):
        aujourd_hui = date(2026, 1, 20)

        self.assertEqual(regles.calculer_retard("2026-01-15", aujourd_hui), 5)
        self.assertEqual(regles.calculer_retard("2026-01-20", aujourd_hui), 0)
        self.assertEqual(regles.calculer_retard("2026-02-01", aujourd_hui), 0)

    def test_calculer_retard_date_invalide(self):
        with self.assertRaises(ValueError):
            regles.calculer_retard("pas-une-date")


if __name__ == "__main__":
    unittest.main()
