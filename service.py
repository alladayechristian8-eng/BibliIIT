"""Couche métier de BibliIIT."""

import sqlite3
from datetime import date

import depot_sqlite as depot

from modeles import Emprunt, Livre
from regles import (
    MAX_EMPRUNTS,
    date_retour_prevue,
    calculer_retard
)


# ==========================================================
# 1. EXCEPTIONS MÉTIER
# ==========================================================

class ErreurBibliotheque(Exception):
    """Exception générale de la bibliothèque."""


class LivreInexistant(ErreurBibliotheque):
    """Le livre demandé n'existe pas."""


class LivreIndisponible(ErreurBibliotheque):
    """Le livre est déjà emprunté."""


class LimiteEmpruntsAtteinte(ErreurBibliotheque):
    """L'étudiant a atteint sa limite d'emprunts."""


class EmpruntIntrouvable(ErreurBibliotheque):
    """Aucun emprunt actif correspondant n'a été trouvé."""


# ==========================================================
# 2. SERVICE BIBLIOTHÈQUE
# ==========================================================

class ServiceBibliotheque:
    """Contient les opérations métier de BibliIIT."""

    def __init__(self, db_path: depot.CheminDB = None) -> None:
        self.db_path = db_path

    # ------------------------------------------------------
    # INITIALISATION
    # ------------------------------------------------------

    def initialiser(self) -> None:
        """Initialise la base de données."""

        try:
            depot.initialiser_base(self.db_path)

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Erreur d'initialisation : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # RECHERCHE
    # ------------------------------------------------------

    def rechercher_livre(self, terme: str) -> list[Livre]:
        """Recherche un livre par code, titre ou auteur."""

        if not isinstance(terme, str) or not terme.strip():
            raise ValueError("Le terme de recherche est obligatoire.")

        try:
            return depot.rechercher_livre(
                terme.strip(),
                self.db_path
            )

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Erreur lors de la recherche : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # EMPRUNTER UN LIVRE
    # ------------------------------------------------------

    def emprunter(self, matricule: str, code_livre: str) -> Emprunt:
        """Effectue un emprunt après vérification des règles."""

        if not isinstance(matricule, str) or not matricule.strip():
            raise ValueError("Le matricule est obligatoire.")

        if not isinstance(code_livre, str) or not code_livre.strip():
            raise ValueError("Le code du livre est obligatoire.")

        matricule = matricule.strip()
        code_livre = code_livre.strip().upper()

        aujourd_hui = date.today()

        emprunt = Emprunt(
            matricule=matricule,
            code_livre=code_livre,
            date_emprunt=aujourd_hui.isoformat(),
            date_retour_prevue=(
                date_retour_prevue(aujourd_hui).isoformat()
            ),
            retourne=False
        )

        try:
            resultat = depot.emprunter_livre(
                emprunt,
                self.db_path
            )

            if resultat == "livre_inexistant":
                raise LivreInexistant(
                    f"Le livre {code_livre} n'existe pas."
                )

            if resultat == "indisponible":
                raise LivreIndisponible(
                    "Ce livre est déjà emprunté."
                )

            if resultat == "limite_atteinte":
                raise LimiteEmpruntsAtteinte(
                    f"Un étudiant ne peut pas dépasser "
                    f"{MAX_EMPRUNTS} emprunts actifs."
                )

            if resultat != "ok":
                raise ErreurBibliotheque(
                    "Impossible d'effectuer cet emprunt."
                )

            return emprunt

        except ErreurBibliotheque:
            raise

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Erreur lors de l'emprunt : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # RETOURNER UN LIVRE
    # ------------------------------------------------------

    def retourner(self, matricule: str, code_livre: str) -> bool:
        """Enregistre le retour d'un livre."""

        if not isinstance(matricule, str) or not matricule.strip():
            raise ValueError("Le matricule est obligatoire.")

        if not isinstance(code_livre, str) or not code_livre.strip():
            raise ValueError("Le code du livre est obligatoire.")

        matricule = matricule.strip()
        code_livre = code_livre.strip().upper()

        try:
            # Attention à l'ordre des paramètres :
            # le dépôt attend d'abord le code, puis le matricule.

            resultat = depot.retourner_livre(
                code_livre,
                matricule,
                self.db_path
            )

            if not resultat:
                raise EmpruntIntrouvable(
                    "Aucun emprunt actif correspondant n'a été trouvé."
                )

            return True

        except ErreurBibliotheque:
            raise

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Erreur lors du retour : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # EMPRUNTS EN COURS
    # ------------------------------------------------------

    def liste_emprunts(self) -> list[dict]:
        """Retourne tous les emprunts actifs."""

        try:
            return depot.liste_emprunts_actifs(self.db_path)

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Impossible de récupérer les emprunts : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # RETOURS EFFECTUÉS
    # ------------------------------------------------------

    def liste_retours(self) -> list[dict]:
        """Retourne tous les livres déjà rendus."""

        try:
            return depot.liste_retours(self.db_path)

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Impossible de récupérer les retours : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # LIVRES EN RETARD
    # ------------------------------------------------------

    def afficher_retards(self) -> list[dict]:
        """Retourne les emprunts en retard."""

        try:
            emprunts = depot.livres_en_retard(self.db_path)

            for emprunt in emprunts:
                emprunt["jours_retard"] = calculer_retard(
                    emprunt["date_retour_prevue"]
                )

            return emprunts

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Impossible de récupérer les retards : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # CATALOGUE
    # ------------------------------------------------------

    def catalogue(self) -> list[Livre]:
        """Retourne tous les livres du catalogue."""

        try:
            return depot.tous_les_livres(self.db_path)

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Impossible de récupérer le catalogue : {erreur}"
            ) from erreur

    def afficher_catalogue(self) -> list[Livre]:
        """Alias pour afficher le catalogue."""

        return self.catalogue()

    # ------------------------------------------------------
    # LIVRES DISPONIBLES
    # ------------------------------------------------------

    def disponibles(self) -> list[Livre]:
        """Retourne uniquement les livres disponibles."""

        try:
            return depot.livres_disponibles(self.db_path)

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Impossible de récupérer les livres disponibles : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # HISTORIQUE
    # ------------------------------------------------------

    def historique(self, matricule: str | None = None) -> list[dict]:
        """Retourne l'historique général ou celui d'un étudiant."""

        if matricule is not None:
            if not isinstance(matricule, str):
                raise ValueError("Le matricule doit être une chaîne.")

            matricule = matricule.strip() or None

        try:
            return depot.historique_emprunts(
                matricule,
                self.db_path
            )

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Impossible de récupérer l'historique : {erreur}"
            ) from erreur

    # ------------------------------------------------------
    # STATISTIQUES
    # ------------------------------------------------------

    def statistiques(self) -> dict[str, int]:
        """Retourne les statistiques de la bibliothèque."""

        try:
            return depot.statistiques(self.db_path)

        except sqlite3.Error as erreur:
            raise ErreurBibliotheque(
                f"Impossible de récupérer les statistiques : {erreur}"
            ) from erreur
