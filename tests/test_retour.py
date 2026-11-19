"""Tests du processus de retour."""

import unittest

from base import BaseTest
from service import EmpruntIntrouvable


class TestRetour(BaseTest):

    def test_retour_valide(self):
        """Le retour rend le livre à nouveau disponible."""
        self.service.emprunter("ETU001", "L001")

        self.assertTrue(self.service.retourner("ETU001", "L001"))

        # Le livre peut être emprunté par un autre étudiant.
        nouvel_emprunt = self.service.emprunter("ETU002", "L001")
        self.assertEqual(nouvel_emprunt.code_livre, "L001")

    def test_retour_enregistre_dans_l_historique(self):
        """Le retour est visible dans la liste des retours effectués."""
        self.service.emprunter("ETU001", "L001")
        self.service.retourner("ETU001", "L001")

        retours = self.service.liste_retours()
        self.assertEqual(len(retours), 1)
        self.assertTrue(retours[0]["date_retour_effective"])
        self.assertEqual(self.service.liste_emprunts(), [])

    def test_retour_livre_non_emprunte(self):
        """Rendre un livre qui n'est pas emprunté est refusé."""
        with self.assertRaises(EmpruntIntrouvable):
            self.service.retourner("ETU001", "L001")

    def test_retour_par_un_autre_etudiant(self):
        """Seul l'étudiant qui a emprunté le livre peut le rendre."""
        self.service.emprunter("ETU001", "L001")

        with self.assertRaises(EmpruntIntrouvable):
            self.service.retourner("ETU002", "L001")

    def test_double_retour(self):
        """Un livre déjà rendu ne peut pas être rendu une deuxième fois."""
        self.service.emprunter("ETU001", "L001")
        self.service.retourner("ETU001", "L001")

        with self.assertRaises(EmpruntIntrouvable):
            self.service.retourner("ETU001", "L001")


if __name__ == "__main__":
    unittest.main()
