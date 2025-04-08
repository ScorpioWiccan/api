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

#consultar disponibilidade de quarto

@app.route('/check_avail', methods=['GET'])
def check_room_availability():
    conn = db_connection() 
    cur = conn.cursor() 
    data = request.get_json()
    if "p_q_id" not in data or "p_res_data_checkin" not in data or "p_res_data_checkout" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call verificar_disponibilidade_quarto(%s,%s,%s)",[data["p_q_id"],data["p_res_data_checkin"],data["p_res_data_checkout"]])
        rooms = [] 
        for r_tuple in cur.fetchall(): 
            r = { 
                "disponivel": r_tuple[0]
            } 
            rooms.append(r) 
        return jsonify(rooms), OK_CODE
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()

#remover quarto... INC INC INC -- sort it out on the db

#RESERVAS -- INC
#inserir reserva - verificando disponibilidade -- inc

#cancelar reserva -- penalidade
@app.route('/cancel_res', methods=['POST'])
def cancel_res():
    conn = db_connection()
    cur = conn.cursor()
    data = request.get_jason()
    if "p_res_id" not in data or "aumento_perc" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call cancelar_reserva(%s,%s);",[data["p_res_id"],data["aumento_perc"]])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

#ver reservas cliente
@app.route('/view_client_res', methods=['GET'])
def view_client_res():
    conn = db_connection()
    cur = conn.cursor()
    data = request.get_jason()
    if "p_cli_u_id" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    cur.execute("call ver_reservas_cliente(%s);",[data['p_cli_u_id']])
    res = [] 
    for r_tuple in cur.fetchall(): 
        r = { 
              "res_id": r_tuple[0],
              "q_id": r_tuple[1],
              "u_id": r_tuple[2],
              "cli_u_id": r_tuple[3],
              "res_data_reserva": r_tuple[4],
              "res_data_checkin": r_tuple[5],
              "res_data_checkout": r_tuple[6],
              "res_preco_total": r_tuple[7],
              "res_estado": r_tuple[8],
              "p_id": r_tuple[9]
            } 
        res.append(r) 
    return jsonify(res), OK_CODE

#admin - ver reservas
@app.route('/view_all_res', methods=['GET'])
def view_all_res():
    conn = db_connection()
    cur = conn.cursor()
    data = request.get_jason()
    cur.execute("call ver_reservas_cliente(%s);",[data['p_cli_u_id']])
    res = [] 
    for r_tuple in cur.fetchall(): 
        r = { 
              "res_id": r_tuple[0],
              "q_id": r_tuple[1],
              "u_id": r_tuple[2],
              "cli_u_id": r_tuple[3],
              "res_data_reserva": r_tuple[4],
              "res_data_checkin": r_tuple[5],
              "res_data_checkout": r_tuple[6],
              "res_preco_total": r_tuple[7],
              "res_estado": r_tuple[8],
              "p_id": r_tuple[9]
            } 
        res.append(r) 
    return jsonify(res), OK_CODE

#Ver detalhes certa reserva
@app.route('/reservas/<int:number>', methods=['GET'])
def view_res_id(number):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("call detalhes_reserva(%s);",[number])
    res = [] 
    for r_tuple in cur.fetchall(): 
        r = { 
              "res_id": r_tuple[0],
              "q_id": r_tuple[1],
              "u_id": r_tuple[2],
              "cli_u_id": r_tuple[3],
              "res_data_reserva": r_tuple[4],
              "res_data_checkin": r_tuple[5],
              "res_data_checkout": r_tuple[6],
              "res_preco_total": r_tuple[7],
              "res_estado": r_tuple[8],
              "p_id": r_tuple[9]
            } 
        res.append(r) 
    return jsonify(res), OK_CODE
    
#AUDITORIA -- INC

#IMAGENS DO QUARTO
#inserir imagem
@app.route('/insert_img', methods=['POST'])
def insert_img():
    conn = db_connection()
    cur = conn.cursor()
    data = request.get_jason()
    if "q_id" not in data or "iq_img" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call inserir_imagem(%s,%s);",[data["q_id"],data["iq_img"]])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE
#remover imagem
@app.route('/del_img', methods=['POST'])
def delete_img():
    conn = db_connection()
    cur = conn.cursor()
    data = request.get_jason()
    if "iq_id" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call remover_imagem(%s);",[data["iq_id"]])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

app.run()
