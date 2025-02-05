import sys
import threading
import webbrowser
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from flask import Flask, render_template

# Importer ton app Flask
from app import app

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CoffeeTrader TZ")
        self.setGeometry(100, 100, 1200, 800)

        # Création d'un widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Création d'un layout vertical
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Création d'un navigateur intégré avec PyQt5
        self.browser = QWebEngineView()
        from PyQt5.QtCore import QUrl  # Ajoute cette ligne en haut du fichier

        # Remplace la ligne de chargement de l'URL par :
        self.browser.setUrl(QUrl("http://127.0.0.1:5000"))

        layout.addWidget(self.browser)

def run_flask():
    """Démarrer Flask en arrière-plan"""
    app.run(debug=False, host="127.0.0.1", port=5000)

if __name__ == "__main__":
    # Lancer Flask dans un thread séparé
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Lancer l'application PyQt5
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

