"""Tests de la recherche de livres."""

import unittest

from base import BaseTest


class TestRecherche(BaseTest):

    def test_recherche_existante(self):
        """Un titre existant est trouvé une seule fois."""
        resultats = self.service.rechercher_livre("Soleils")

        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0].code, "L004")

    def test_recherche_par_code(self):
        """La recherche fonctionne aussi avec le code du livre."""
        resultats = self.service.rechercher_livre("L001")

        self.assertEqual([livre.code for livre in resultats], ["L001"])

    def test_recherche_insensible_accents_et_casse(self):
        """« RESEAUX informatiques » trouve « Réseaux informatiques »."""
        resultats = self.service.rechercher_livre("RESEAUX informatiques")

        self.assertEqual([livre.code for livre in resultats], ["L002"])

    def test_recherche_plusieurs_resultats(self):
        """Plusieurs livres peuvent correspondre au même mot."""
        codes = {livre.code for livre in self.service.rechercher_livre("Python")}

        self.assertIn("L001", codes)
        self.assertGreater(len(codes), 1)

    def test_recherche_inexistante(self):
        """Un livre inexistant donne une liste vide."""
        resultats = self.service.rechercher_livre("Livre totalement inexistant")

        self.assertEqual(resultats, [])

    def test_recherche_caracteres_speciaux(self):
        """Les jokers SQL (% et _) sont cherchés comme du texte simple."""
        self.assertEqual(self.service.rechercher_livre("%"), [])
        self.assertEqual(self.service.rechercher_livre("_"), [])

    def test_recherche_vide(self):
        """Un terme vide est refusé avec un message clair."""
        with self.assertRaises(ValueError):
            self.service.rechercher_livre("   ")


if __name__ == "__main__":
    unittest.main()
