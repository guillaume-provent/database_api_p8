from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
db_path = 'data.db'

@app.route('/get_customer/<int:sk_id_curr>', methods=['GET'])
def get_customer(sk_id_curr):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM credits WHERE SK_ID_CURR=?", (sk_id_curr,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({"error": "Customer not found"}), 404

@app.route('/update_customer', methods=['PUT'])
def update_customer():
    data = request.json
    sk_id_curr = data.get('SK_ID_CURR')
    if sk_id_curr is None:
        return jsonify({"error": "SK_ID_CURR is required"}), 400
    
    fields = ', '.join([f"{key}=?" for key in data.keys() if key != 'SK_ID_CURR'])
    values = [value for key, value in data.items() if key != 'SK_ID_CURR']
    values.append(sk_id_curr)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"UPDATE credits SET {fields} WHERE SK_ID_CURR=?", values)
    conn.commit()
    conn.close()
    
    if cur.rowcount == 0:
        return jsonify({"error": "Customer not found"}), 404
    
    return jsonify({"message": "Customer updated successfully"})

@app.route('/create_customer', methods=['POST'])
def create_customer():
    data = request.json
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT MAX(SK_ID_CURR) FROM credits")
    max_id = cur.fetchone()[0]
    new_id = max_id + 1 if max_id else 100001  # Starting ID if table is empty
    
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    values = list(data.values())
    
    cur.execute(f"INSERT INTO credits (SK_ID_CURR, {columns}) VALUES (?, {placeholders})", [new_id] + values)
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Customer created successfully", "SK_ID_CURR": new_id})

if __name__ == '__main__':
    app.run(debug=True)