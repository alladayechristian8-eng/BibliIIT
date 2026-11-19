"""Interface console de BibliIIT (menu interactif)."""

from modeles import Livre
from service import (
    ServiceBibliotheque,
    ErreurBibliotheque
)


def afficher_menu() -> None:
    """Affiche le menu principal."""

    print("""
========== BibliIIT ==========
1. Rechercher un livre
2. Emprunter un livre
3. Retourner un livre
4. Retards
5. Emprunts en cours
6. Retours effectués
7. Afficher le catalogue
8. Afficher les livres disponibles
9. Consulter l'historique
0. Quitter
==============================
""")


def rechercher(service: ServiceBibliotheque) -> None:
    """Gère la recherche d'un livre."""

    terme = input("Titre, auteur ou code du livre : ").strip()

    try:
        livres = service.rechercher_livre(terme)

        if not livres:
            print("Aucun livre trouvé.")
            return

        print("\n--- Résultats de la recherche ---")

        for livre in livres:
            print(f"\nCode   : {livre.code}")
            print(f"Titre  : {livre.titre}")
            print(f"Auteur : {livre.auteur}")
            print(f"Année  : {livre.annee}")

    except (ValueError, ErreurBibliotheque) as erreur:
        print(f"\nErreur : {erreur}")


def emprunter(service: ServiceBibliotheque) -> None:
    """Gère l'emprunt d'un livre."""

    matricule = input("Matricule de l'étudiant : ").strip()
    code = input("Code du livre : ").strip()

    try:
        resultat = service.emprunter(matricule, code)

        print("\nEmprunt effectué avec succès.")
        print(f"Étudiant : {resultat.matricule}")
        print(f"Livre : {resultat.code_livre}")
        print(f"Date d'emprunt : {resultat.date_emprunt}")
        print(f"Retour prévu : {resultat.date_retour_prevue}")

    except (ValueError, ErreurBibliotheque) as erreur:
        print(f"\nErreur : {erreur}")


def retourner(service: ServiceBibliotheque) -> None:
    """Gère le retour d'un livre."""

    matricule = input("Matricule de l'étudiant : ").strip()
    code = input("Code du livre : ").strip()

    try:
        service.retourner(matricule, code)
        print("\nRetour effectué avec succès.")

    except (ValueError, ErreurBibliotheque) as erreur:
        print(f"\nErreur : {erreur}")


def afficher_emprunts(lignes: list[dict]) -> None:
    """Affiche une liste d'emprunts ou de retours."""

    if not lignes:
        print("\nAucun emprunt trouvé.")
        return

    print("\n========== LISTE DES EMPRUNTS ==========")

    for e in lignes:
        print(f"""
ID : {e['id']}
Matricule : {e['matricule']}
Code livre : {e['code_livre']}
Titre : {e['titre']}
Date d'emprunt : {e['date_emprunt']}
Retour prévu : {e['date_retour_prevue']}
Date de retour effective : {e.get('date_retour_effective') or 'Non rendu'}
-----------------------------------------
""")


def afficher_retards(service: ServiceBibliotheque) -> None:
    """Affiche les livres qui n'ont pas été retournés à temps."""

    try:
        retards = service.afficher_retards()

        if not retards:
            print("\nAucun livre en retard.")
            return

        print("\n======= LIVRES EN RETARD =======")

        for emprunt in retards:
            print(f"\nMatricule : {emprunt['matricule']}")
            print(f"Code livre : {emprunt['code_livre']}")
            print(f"Titre : {emprunt['titre']}")
            print(f"Retour prévu : {emprunt['date_retour_prevue']}")
            print(f"Retard : {emprunt['jours_retard']} jour(s)")

    except ErreurBibliotheque as erreur:
        print(f"\nErreur : {erreur}")


def afficher_livres(livres: list[Livre]) -> None:
    """Affiche le catalogue ou les livres disponibles."""

    if not livres:
        print("\nAucun livre trouvé.")
        return

    print("\n========== LISTE DES LIVRES ==========")

    for livre in livres:
        print(f"""
Code : {livre.code}
Titre : {livre.titre}
Auteur : {livre.auteur}
Année : {livre.annee}
-----------------------------------------
""")


def main() -> None:
    """Point d'entrée principal de l'application."""

    service = ServiceBibliotheque()

    try:
        service.initialiser()
    except Exception as erreur:
        print(f"Impossible d'initialiser la bibliothèque : {erreur}")
        return

    print("\nBienvenue dans BibliIIT !")

    while True:
        try:
            afficher_menu()
            choix = input("Votre choix : ").strip()

            if choix == "1":
                rechercher(service)

            elif choix == "2":
                emprunter(service)

            elif choix == "3":
                retourner(service)

            elif choix == "4":
                afficher_retards(service)

            elif choix == "5":
                afficher_emprunts(service.liste_emprunts())

            elif choix == "6":
                afficher_emprunts(service.liste_retours())

            elif choix == "7":
                afficher_livres(service.catalogue())

            elif choix == "8":
                afficher_livres(service.disponibles())

            elif choix == "9":
                matricule = input(
                    "Matricule (vide pour tout l'historique) : "
                ).strip()

                afficher_emprunts(
                    service.historique(matricule or None)
                )

            elif choix == "0":
                print("\nMerci d'avoir utilisé BibliIIT.")
                break

            else:
                print("\nChoix invalide. Veuillez choisir entre 0 et 9.")

        except (EOFError, KeyboardInterrupt):
            print("\n\nFermeture de BibliIIT.")
            break

        except Exception as erreur:
            print(f"\nUne erreur inattendue est survenue : {erreur}")


if __name__ == "__main__":
    main()
