from flask import Flask, render_template, request
import mysql.connector
import pandas as pd

app = Flask(__name__)

# Configurer la connexion MySQL avec mysql.connector
def get_db_connection(db_name=None):
    return mysql.connector.connect(
        host='localhost',
        user='root',  # Remplace par ton utilisateur MySQL
        password='',  # Remplace par ton mot de passe MySQL
        database=db_name if db_name else None
    )

# Page d'accueil avec le formulaire
@app.route('/')
def index():
    return render_template('index.html')

# Route pour gérer le téléchargement et l'insertion de données
@app.route('/upload', methods=['POST'])
def upload_file():
    db_name = request.form['db_name']
    table_name = request.form['table_name']
    file = request.files['file']

    # Déterminer l'extension du fichier pour choisir la méthode de lecture
    filename = file.filename
    if filename.endswith('.csv'):
        df = pd.read_csv(file)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        return "Format de fichier non supporté !"

    # Se connecter à MySQL (sans base de données spécifiée)
    connection = get_db_connection()
    cursor = connection.cursor()

    # Créer la base de données si elle n'existe pas
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    connection.commit()

    # Se reconnecter avec la base de données créée
    connection = get_db_connection(db_name)
    cursor = connection.cursor()

    # Créer la table si elle n'existe pas en fonction des en-têtes du fichier
    columns = ', '.join([f"`{col}` TEXT" for col in df.columns])
    create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})"
    cursor.execute(create_table_query)
    connection.commit()

    # Insérer les données du fichier dans la table
    for _, row in df.iterrows():
        values = ', '.join([f"'{str(val)}'" for val in row])
        insert_query = f"INSERT INTO `{table_name}` VALUES ({values})"
        cursor.execute(insert_query)
    connection.commit()

    cursor.close()
    connection.close()

    return f"Les données ont été insérées avec succès dans la base '{db_name}', table '{table_name}'"

if __name__ == '__main__':
    app.run(debug=True)
