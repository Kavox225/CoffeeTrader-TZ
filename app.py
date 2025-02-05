from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from datetime import datetime
import pandas as pd
import os
import yfinance as yf  # Ajouter cette ligne pour utiliser yfinance

app = Flask(__name__)

# Vérifier si la base de données existe et la créer si nécessaire
if not os.path.exists("database.db"):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origine TEXT,
                quantite INTEGER,
                prix_achat REAL,
                date_achat TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commandes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client TEXT,
                quantite INTEGER,
                prix_vente REAL,
                date_commande TEXT
            )
        """)
        conn.commit()

        
# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Fonction pour récupérer les alertes
def get_alertes():
    with get_db_connection() as conn:
        alertes = []
        lots_faibles = conn.execute("SELECT * FROM lots WHERE quantite < 100").fetchall()
        for lot in lots_faibles:
            alertes.append(f"⚠️ Stock faible : {lot['origine']} ({lot['quantite']} kg restants)")

        commandes = conn.execute("SELECT * FROM commandes").fetchall()
        today = datetime.today().strftime('%Y-%m-%d')
        for commande in commandes:
            if commande['date_commande'] < today:
                alertes.append(f"⏳ Commande en retard : {commande['client']} (Date : {commande['date_commande']})")

    return alertes

# Fonction pour récupérer les statistiques
def get_statistics():
    with get_db_connection() as conn:
        stats = {}
        stats['total_stock'] = conn.execute("SELECT SUM(quantite) FROM lots").fetchone()[0] or 0
        stats['prix_moyen_achat'] = conn.execute("SELECT AVG(prix_achat) FROM lots").fetchone()[0] or 0
        stats['ventes_totales'] = conn.execute("SELECT SUM(quantite) FROM commandes").fetchone()[0] or 0
        stats['prix_moyen_vente'] = conn.execute("SELECT AVG(prix_vente) FROM commandes").fetchone()[0] or 0

    return stats

# Fonction pour récupérer le cours du café
def get_coffee_price():
    try:
        coffee = yf.Ticker("KC=F")  # KC=F est le ticker pour le café sur Yahoo Finance
        coffee_price = coffee.history(period="1d")['Close'][0]
        return round(coffee_price, 2)
    except Exception as e:
        print(f"Erreur lors de la récupération du cours du café : {e}")
        return "N/A"

# Fonction d'export en Excel
@app.route('/export_excel')
def export_excel():
    with get_db_connection() as conn:
        lots = pd.read_sql_query("SELECT * FROM lots", conn)
        commandes = pd.read_sql_query("SELECT * FROM commandes", conn)

    excel_file = "export_coffee_data.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        lots.to_excel(writer, sheet_name="Lots", index=False)
        commandes.to_excel(writer, sheet_name="Commandes", index=False)

    response = send_file(excel_file, as_attachment=True)
    os.remove(excel_file)
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    alertes = get_alertes()
    stats = get_statistics()
    coffee_price = get_coffee_price()
    return render_template('dashboard.html', alertes=alertes, stats=stats, coffee_price=coffee_price)

@app.route('/lots_commandes', methods=['GET', 'POST'])
def lots_commandes():
    with get_db_connection() as conn:
        # Gérer l'ajout d'un lot
        if request.method == 'POST' and 'origine' in request.form:
            origine = request.form['origine']
            quantite = request.form['quantite']
            prix_achat = request.form['prix_achat']
            date_achat = request.form['date_achat']

            conn.execute('INSERT INTO lots (origine, quantite, prix_achat, date_achat) VALUES (?, ?, ?, ?)',
                         (origine, quantite, prix_achat, date_achat))
            conn.commit()

        # Gérer l'ajout d'une commande
        if request.method == 'POST' and 'client' in request.form:
            client = request.form['client']
            quantite = int(request.form['quantite'])
            prix_vente = float(request.form['prix_vente'])
            date_commande = request.form['date_commande']

            conn.execute('INSERT INTO commandes (client, quantite, prix_vente, date_commande) VALUES (?, ?, ?, ?)',
                         (client, quantite, prix_vente, date_commande))
            conn.commit()

        # Récupérer les filtres depuis la requête GET
        filter_origine = request.args.get('filter_origine', '')
        filter_date = request.args.get('filter_date', '')

        # Construire la requête SQL pour les lots avec filtrage
        query_lots = "SELECT * FROM lots WHERE 1=1"
        params_lots = []
        if filter_origine:
            query_lots += " AND origine LIKE ?"
            params_lots.append(f"%{filter_origine}%")
        if filter_date:
            query_lots += " AND date_achat = ?"
            params_lots.append(filter_date)

        lots = conn.execute(query_lots, params_lots).fetchall()

        # Construire la requête SQL pour les commandes avec filtrage
        query_commandes = "SELECT * FROM commandes WHERE 1=1"
        params_commandes = []
        if filter_date:
            query_commandes += " AND date_commande = ?"
            params_commandes.append(filter_date)

        commandes = conn.execute(query_commandes, params_commandes).fetchall()

    return render_template('lots_commandes.html', lots=lots, commandes=commandes)

#route suppression lots#
@app.route('/delete_lot/<int:lot_id>', methods=['GET'])
def delete_lot(lot_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM lots WHERE id = ?', (lot_id,))
        conn.commit()
    return redirect(url_for('lots_commandes'))

#route suppression commande#
@app.route('/delete_commande/<int:commande_id>', methods=['GET'])
def delete_commande(commande_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM commandes WHERE id = ?', (commande_id,))
        conn.commit()
    return redirect(url_for('lots_commandes'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
