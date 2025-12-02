# On importe la bibliothèque Python "re" qui sert à utiliser les expressions régulières.
import re

# On importe Flask et les fonctions nécessaires pour créer des pages et lire les formulaires.
from flask import Flask, render_template

# On importe les blueprints définis dans les fichiers séparés.
from validation_routes import validation_bp
from extraction_routes import extraction_bp
from transformation_routes import transformation_bp

# On crée une instance de l'application Flask.
app = Flask(__name__)

# On enregistre les blueprints : cela "branche" les routes définies dans
# les autres fichiers sur cette application principale.
app.register_blueprint(validation_bp)
app.register_blueprint(extraction_bp)
app.register_blueprint(transformation_bp)


# 3. ROUTE : Page d'accueil


# @app.route("/") signifie : quand un utilisateur visite "/", on exécute index().

@app.route("/")
def index():
    # On retourne la page HTML "index.html".
    return render_template("index.html")



# -----------------------------------------------------------------------------
# 7. Lancement de l'application Flask
# -----------------------------------------------------------------------------

# Ce bloc s'exécute seulement si on lance ce fichier directement.
if __name__ == "__main__":
    # debug=True : le serveur se recharge automatiquement et affiche les erreurs.
    app.run(debug=True)
