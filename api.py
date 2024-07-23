from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
db_path = 'data.db'

# Méthode : Obtenir les données d'un dossier :
@app.route('/get_app/<int:sk_id_curr>', methods=['GET'])
def get_app(sk_id_curr):
    # Connexion à la BDD :
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Sélection du dossier dans la BDD :
    cur.execute("SELECT * FROM applications WHERE SK_ID_CURR=?", (sk_id_curr,))
    row = cur.fetchone()
    conn.close()

    # Renvoi des données du dossier :
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({"error": "Dossier non trouvé"}), 404

# Méthode : Mettre à jour les données d'un dossier existant :
@app.route('/update_app', methods=['PUT'])
def update_app():
    # Lecture des données en entrée :
    data = request.json
    sk_id_curr = data.get('SK_ID_CURR')
    if sk_id_curr is None:
        return jsonify({"error": "SK_ID_CURR requis"}), 400
    fields = ', '.join([f"{key}=?" for key in data.keys() if key != 'SK_ID_CURR'])
    values = [value for key, value in data.items() if key != 'SK_ID_CURR']
    values.append(sk_id_curr)

    # Connexion à la BDD :
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Mise à jour des données du dossier :
    cur.execute(f"UPDATE applications SET {fields} WHERE SK_ID_CURR=?", values)
    conn.commit()
    conn.close()

    # Confirmation ou non de la mise à jour :
    if cur.rowcount == 0:
        return jsonify({"error": "Dossier non trouvé"}), 404
    
    return jsonify({"message": "Dossier mis à jour"})

# Méthode : Enregistrer un nouveau dossier :
@app.route('/create_app', methods=['POST'])
def create_app():
    # Lecture des données en entrée :
    data = request.json

    # Connexion à la BDD :
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT MAX(SK_ID_CURR) FROM applications")
    
    # Dé&termination du n° du nouveau dossier :
    max_id = cur.fetchone()[0]
    new_id = max_id + 1
    
    # Préparation des données pour l'enregistrement :
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    values = list(data.values())

    # ENregistrement des données :
    cur.execute(f"INSERT INTO applications (SK_ID_CURR, {columns}) VALUES (?, {placeholders})", [new_id] + values)
    conn.commit()
    conn.close()

    # Retour du n° du nouveau dossier :
    return jsonify({"message": "Dossier créé avec succès", "SK_ID_CURR": new_id})

if __name__ == '__main__':
    app.run(debug=True)
