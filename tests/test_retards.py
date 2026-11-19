"""Tests de l'affichage des retards."""

import unittest
from datetime import date, timedelta

import depot_sqlite as depot
from base import BaseTest


class TestRetards(BaseTest):

    def _emprunt_ancien(self, jours: int) -> None:
        """Insère directement un emprunt daté d'il y a `jours` jours."""
        debut = date.today() - timedelta(days=jours)
        prevue = debut + timedelta(days=14)

        with depot.connexion(self.db) as cn:
            cn.execute(
                "INSERT INTO EMPRUNTS (matricule, code_livre, date_emprunt, "
                "date_retour_prevue, retourne) VALUES (?, ?, ?, ?, 0)",
                ("ETU001", "L001", debut.isoformat(), prevue.isoformat()),
            )

    def test_aucun_retard(self):
        """Un emprunt récent n'est pas en retard."""
        self.service.emprunter("ETU001", "L001")

        self.assertEqual(self.service.afficher_retards(), [])

    def test_retard_calcule(self):
        """Un emprunt vieux de 20 jours a 6 jours de retard."""
        self._emprunt_ancien(20)

        retards = self.service.afficher_retards()

        self.assertEqual(len(retards), 1)
        self.assertEqual(retards[0]["code_livre"], "L001")
        self.assertEqual(retards[0]["jours_retard"], 6)

    def test_livre_rendu_n_est_plus_en_retard(self):
        """Une fois rendu, le livre disparaît de la liste des retards."""
        self._emprunt_ancien(20)
        self.service.retourner("ETU001", "L001")

        self.assertEqual(self.service.afficher_retards(), [])


if __name__ == "__main__":
    unittest.main()
