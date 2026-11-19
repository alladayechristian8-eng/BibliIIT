"""Modèles de données (dataclasses) de BibliIIT."""

from dataclasses import dataclass


@dataclass
class Livre:
    """Représente un livre enregistré dans la bibliothèque."""

    code: str
    titre: str
    auteur: str
    annee: int


@dataclass
class Emprunt:
    """Représente un emprunt effectué par un étudiant."""

    matricule: str
    code_livre: str
    date_emprunt: str
    date_retour_prevue: str
    retourne: bool = False
