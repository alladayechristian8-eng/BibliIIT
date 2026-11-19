"""Règles métier de BibliIIT (aucune requête SQL ici)."""

from datetime import date, timedelta


DUREE_EMPRUNT = 14
MAX_EMPRUNTS = 3


def livre_disponible(emprunte: bool) -> bool:
    """Indique si un livre est disponible."""
    return not emprunte


def peut_emprunter(nombre_emprunts: int) -> bool:
    """Vérifie si un étudiant peut effectuer un nouvel emprunt."""
    return 0 <= nombre_emprunts < MAX_EMPRUNTS


def date_retour_prevue(date_emprunt: date | None = None) -> date:
    """Calcule la date de retour prévue après 14 jours."""
    if date_emprunt is None:
        date_emprunt = date.today()

    return date_emprunt + timedelta(days=DUREE_EMPRUNT)


def calculer_retard(date_prevue: str, aujourd_hui: date | None = None) -> int:
    """
    Calcule le nombre de jours de retard.

    Retourne 0 si le livre n'est pas en retard.
    """
    try:
        date_limite = date.fromisoformat(date_prevue)
    except (ValueError, TypeError) as erreur:
        raise ValueError("Date de retour prévue invalide.") from erreur

    if aujourd_hui is None:
        aujourd_hui = date.today()

    retard = (aujourd_hui - date_limite).days

    return max(0, retard)
