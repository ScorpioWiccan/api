from flask import Flask, jsonify , request
import psycopg2

app = Flask(__name__)

OK_CODE = 200
BAD_REQUEST_CODE = 400

def db_connection(): 
    db = psycopg2.connect("host=localhost dbname=hotel_tester2 user=postgres password=123") 
    return db

@app.route("/")
def welcome():
    return "<p>Welcome to the Black Lotus Resort!</p>"

#QUARTOS -- INC
@app.route('/view_rooms', methods=['GET'])  
def view_rooms(): 
    conn = db_connection() 
    cur = conn.cursor() 
    cur.execute("SELECT * FROM view_quarto;") 
    rooms = [] 
    for r_tuple in cur.fetchall(): 
        r = { 
            "q_id": r_tuple[0], 
            "q_num": r_tuple[1], 
            "q_capacidade": r_tuple[2],
            "q_preco_noite": r_tuple[3],
            "q_descricao": r_tuple[4],
            "q_estado": r_tuple[5]
        } 
        rooms.append(r) 
    return jsonify(rooms), OK_CODE

@app.route('/insert_room', methods=['POST'])
def insert_room():
    conn = db_connection() 
    cur = conn.cursor() 
    data = request.get_json()
    if "q_num" not in data or "q_capacidade" not in data or "q_preco_noite" not in data or "q_descricao" not in data or "q_estado" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call inserir_quarto(%s,%s,%s,%s,%s)", [data["q_num"],data["q_capacidade"],data["q_preco_noite"],data["q_descricao"],data["q_estado"]])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

@app.route('/update_room_price', methods=['POST'])
def update_room_price():
    conn = db_connection() 
    cur = conn.cursor() 
    data = request.get_json()
    if "q_id" not in data or "q_factor" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call atualizar_preco_quarto(%s,%s)",[data["q_id"],data["q_factor"]])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

@app.route('/update_room_capacity', methods=['POST'])
def update_room_capacity():
    conn = db_connection() 
    cur = conn.cursor() 
    data = request.get_json()
    if "q_id" not in data or "q_capacidade" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call atualizar_capacidade_quarto(%s,%s)",[data["q_id"],data["q_capacidade"]])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

@app.route('/raise_room_price_per_capacity', methods=['POST'])
def raise_room_price_per_capacity():
    conn = db_connection() 
    cur = conn.cursor() 
    data = request.get_json()
    if "perc_aumento" not in data or "p_capacidade" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call aumentar_preco_quarto(%s,%s)",[data["perc_aumento"],data["p_capacidade"]])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

#remover quarto... INC INC INC

#RESERVAS -- INC

#AUDITORIA -- INC

#IMAGENS DO QUARTO -- INC

app.run()
