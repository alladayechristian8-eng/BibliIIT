"""Tests du processus d'emprunt."""

import unittest

from base import BaseTest
from service import LimiteEmpruntsAtteinte, LivreInexistant, LivreIndisponible


class TestEmprunt(BaseTest):

    def test_emprunt_valide(self):
        """Un emprunt valide est enregistré avec ses dates."""
        emprunt = self.service.emprunter("ETU001", "L001")

        self.assertEqual(emprunt.matricule, "ETU001")
        self.assertEqual(emprunt.code_livre, "L001")
        self.assertFalse(emprunt.retourne)
        self.assertTrue(emprunt.date_emprunt)
        self.assertTrue(emprunt.date_retour_prevue)

        actifs = self.service.liste_emprunts()
        self.assertEqual(len(actifs), 1)
        self.assertEqual(actifs[0]["code_livre"], "L001")

    def test_emprunt_refuse(self):
        """Un livre déjà emprunté est refusé."""
        self.service.emprunter("ETU001", "L001")

        with self.assertRaises(LivreIndisponible):
            self.service.emprunter("ETU002", "L001")

    def test_limite_emprunts(self):
        """Un étudiant ne peut pas avoir plus de 3 emprunts actifs."""
        for code in ("L001", "L002", "L003"):
            self.service.emprunter("ETU001", code)

        with self.assertRaises(LimiteEmpruntsAtteinte):
            self.service.emprunter("ETU001", "L004")

    def test_livre_inexistant(self):
        """Un code inconnu est refusé."""
        with self.assertRaises(LivreInexistant):
            self.service.emprunter("ETU001", "L999")

    def test_matricule_vide(self):
        """Le matricule est obligatoire."""
        with self.assertRaises(ValueError):
            self.service.emprunter("   ", "L001")

    def test_code_vide(self):
        """Le code du livre est obligatoire."""
        with self.assertRaises(ValueError):
            self.service.emprunter("ETU001", "")

    def test_code_en_minuscules(self):
        """« l001 » est accepté comme « L001 »."""
        emprunt = self.service.emprunter("ETU001", "l001")

        self.assertEqual(emprunt.code_livre, "L001")


if __name__ == "__main__":
    unittest.main()
