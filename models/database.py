import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Création de la table des lots de café
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origine TEXT NOT NULL,
        quantite INTEGER NOT NULL,
        prix_achat REAL NOT NULL,
        date_achat TEXT NOT NULL
    )
''')

# Création de la table des commandes
cursor.execute('''
    CREATE TABLE IF NOT EXISTS commandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client TEXT NOT NULL,
        quantite INTEGER NOT NULL,
        prix_vente REAL NOT NULL,
        date_commande TEXT NOT NULL,
        profit REAL DEFAULT 0
    )
''')

conn.commit()
conn.close()

print("Base de données initialisée et mise à jour avec succès !")
