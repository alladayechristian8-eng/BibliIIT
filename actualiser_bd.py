
import depot_sqlite

# Créer les tables si elles n'existent pas.
depot_sqlite.creer_tables()

# Ajouter les 50 livres.
depot_sqlite.inserer_livres_demo()

# Vérifier le catalogue.
livres = depot_sqlite.tous_les_livres()

print("Mise à jour terminée.")
print("Nombre de livres :", len(livres))

for livre in livres:
    print(livre.code, "-", livre.titre)
