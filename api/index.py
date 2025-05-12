from flask import Flask, jsonify , request
import psycopg2
import os
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET")

OK_CODE = 200
BAD_REQUEST_CODE = 400


#token = jwt.encode({'user_id': 2, 'user_bd': 'tarefaA','exp': datetime.utcnow() + timedelta(hours=1)},app.config['SECRET_KEY'], 'HS256')
token = jwt.encode({'user_id': 3, 'user_bd': 'tarefaB','exp': datetime.utcnow() + timedelta(hours=1)},app.config['SECRET_KEY'], 'HS256')

def db_connection(): 
    db = psycopg2.connect(database=os.environ.get("BD_NAME"),
        user=os.environ.get("USERNAME"),
        password=os.environ.get("PASSWORD"),
        host=os.environ.get("HOST"),
        port=os.environ.get("PORT")) 
    return db

@app.route("/")
def welcome():
    return "<p>Welcome to the Black Lotus Resort!</p>"

#REGISTO
@app.route("/auth/register", methods=["POST"])
def register():
  #db connection
  conn = db_connection()
  cur = conn.cursor()
  #parse input data as JSON
  data = request.get_json()

  #if parameters do not correspond
  if "u_username" not in data or "u_password" not in data or "u_nome" not in data or "u_contacto" not in data or "u_nif" not in data or "u_nivel_privilegio" not in data:
    return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

  try:
    cur.execute("call registar_utilizador(%s,%s,%s,%s,%s,%s);",[data["u_username"], data["u_password"], data["u_nome"], data["u_contacto"], data["u_nif"], data["u_nivel_privilegio"]])
    user = cur.fetchall()
    conn.commit()
  except Exception as e:
    d = {"mensagem": str(e)}
    return jsonify(d), 500
  finally:
    cur.close()
    conn.close()
  
  return jsonify(user), OK_CODE

#QUARTOS -- INC
@app.route('/disponibilidade', methods=['POST'])
def verificar_disponibilidade():
    conn = db_connection() 
    cur = conn.cursor() 
    data = request.get_json()
    if "p_q_id" not in data or "p_res_data_checkin" not in data or "p_res_data_checkout" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("select verificar_disponibilidade_quarto(%s,%s,%s);", [data["p_q_id"],data["p_res_data_checkin"],data["p_res_data_checkout"]])
        disponibilidade = cur.fetchall()
        conn.commit()
        data_user=jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        cur.execute("call inserir_auditoria(%s,%s,%s);",[data_user['user_id'],"Viu Disponibilidade Quarto",data_user['user_bd']])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return disponibilidade, OK_CODE

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

#remover quarto... INC INC INC -- maybe add an attribute "q_removido" that could be true or false

#RESERVAS -- INC
#Criar Nova Reserva -- ENUNCIADO
@app.route('/reservas', methods=['POST'])
def inserir_reserva():
    conn = db_connection()
    cur = conn.cursor()
    data = request.get_json()
    if "p_q_id" not in data or "p_u_id" not in data or "p_cli_u_id" not in data or "p_res_data_checkin" not in data or "p_res_data_checkout" not in data or "p_res_preco_total" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call inserir_reserva(%s,%s,%s,%s,%s,%s)",[data["p_q_id"],data["p_u_id"],data["p_cli_u_id"],data["p_res_data_checkin"],data["p_res_data_checkout"],data["p_res_preco_total"]])
        conn.commit()
        data_user=jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        cur.execute("call inserir_auditoria(%s,%s,%s)",[data_user['user_id'],"Inseriou Reserva",data_user['user_bd']])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

#Consultar Detalhes de uma Reserva -- ENUNCIADO -- check if this is how it is done, the int in the thingy -- check class exercises
@app.route('/reservas/<int:id>', methods=['GET'])
def consultar_reserva(id):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM view_reserva WHERE res_id=%s;",[id]) 
    rs = [] 
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
        rs.append(r) 
    return jsonify(rs), OK_CODE
    
#Cancelar Uma Reserva, Aplicando Regras de negócio -- ENUNCIADO -- work on this one
@app.route('/reservas/<int:id>', methods=['POST'])
def cancelar_reserva(id):
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.execute("call cancelar_reserva(%s,10)",[id])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

#AUDITORIA -- INC

#IMAGENS DO QUARTO -- INC
#Upload de imagens dos quartos -- ENUNCIADO
@app.route('/upload-imagem', methods=['POST'])
def upload_imagem():
    conn = db_connection()
    cur = conn.cursor()
    data = request.get_json()
    if "p_q_id" not in data or "p_img_b64" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call inserir_imagem(%s,%s)",[data["p_q_id"],data["p_img_b64"]])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE

#Recuperar Imagens de um quarto
@app.route('/quartos/<int:id>/imagem', methods=['GET'])
def ver_imagens(id):
    conn = db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM view_imagens_quarto WHERE q_id=%s;",[id]) 
    rs = [] 
    for r_tuple in cur.fetchall(): 
        r = { 
            "iq_id": r_tuple[0],
            "q_id": r_tuple[1], 
            "iq_img": r_tuple[2]
        } 
        rs.append(r) 
    return jsonify(rs), OK_CODE



#inserir pagamento
@app.route("/pagamento", methods = ["POST"])
def pagamento():
    conn = db_connection()
    cur = conn.cursor()
    data = request.get_json()
    if "p_r_id" not in data or "p_p_metodo" not in data:
        return jsonify({"error": "invalid request"}), BAD_REQUEST_CODE
    try:
        cur.execute("call inserir_pagamento(%s,%s)",[data["p_r_id"],data["p_p_metodo"]])
        conn.commit()
        data_user=jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        cur.execute("call inserir_auditoria(%s,%s,%s)",[data_user['user_id'],"Pagou Reserva",data_user['user_bd']])
        conn.commit()
    except Exception as e:
        d = {"mensagem": str(e)}
        return jsonify(d), 500
    finally:
        cur.close()
        conn.close()
    return "Sucesso", OK_CODE



if __name__ == "__main__":
    app.run()
