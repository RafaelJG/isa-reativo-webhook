import config
import base64
import uuid
import datetime

from sqlalchemy import text

DATABASE_NAME = config.DATABASE_NAME




# Salva intent id pela session
def insert_session_intent(id_intent, session_id, db):
	tabela = f"{DATABASE_NAME}.chat_session_intents"
	sql_txt = f"INSERT INTO {tabela} (session_id, id_intent) VALUES ('{session_id}', '{id_intent}')"

	sql = text(sql_txt)
	sql_ok, lastrowid = db_execute_sql(sql, db, return_id=True)

	return sql_ok, lastrowid


def insert_pesquisa(session_id, pergunta, resposta, db):
	tabela = f"{DATABASE_NAME}.chat_pesquisa"
	sql_txt = f"INSERT INTO {tabela} (session_id, pergunta, resposta) VALUES ('{session_id}', '{pergunta}', '{resposta}')"

	sql = text(sql_txt)
	sql_ok, lastrowid = db_execute_sql(sql, db, return_id=True)

	return sql_ok, lastrowid

def insert_joinvasc(session_id, joinvasc, db):
	tabela = f"{DATABASE_NAME}.chat_joinvasc_info"
	sql_txt = f"INSERT INTO {tabela} (session_id, joinvasc) VALUES ('{session_id}', '{joinvasc}')"

	sql = text(sql_txt)
	sql_ok, lastrowid = db_execute_sql(sql, db, return_id=True)

	return sql_ok, lastrowid	


# Salva intent id pela session
def get_mensagem_dia(id_mensagem, db):
	tabela = f"{DATABASE_NAME}.chat_mensagem_dia"
	result = db.execute(f"SELECT mensagem FROM {tabela} where id = {id_mensagem}")
	resposta = ""
	for row in result:
			resposta = row['mensagem']
	return resposta

def get_mensagens_dia_ids(db):
	tabela = f"{DATABASE_NAME}.chat_mensagem_dia"


	sql_txt = f"SELECT id FROM {tabela}"
	result = db.execute(sql_txt)
	ids =[]
	for row in result:
			ids.append(row['id'])
	return ids

def get_last_msg(session_id, db):
	tabela = f"{DATABASE_NAME}.chat_historico"
	result = db.execute(f"SELECT mensagem FROM {tabela} where session_id = '{session_id}' AND origem = 'BOT'")
	msg = ""
	for row in result:
			msg = row['mensagem']
	return msg


def get_faq_ids(db):
	tabela = f"{DATABASE_NAME}.chat_faq_avc"


	sql_txt = f"SELECT id FROM {tabela}"
	result = db.execute(sql_txt)
	ids =[]
	for row in result:
			ids.append(row['id'])
	return ids



# Atualiza contagem da intenção
def update_intent_count(id_intent, db):
	tabela = f"{DATABASE_NAME}.chat_intents_count"

	print("ID_INTENT: {}".format(id_intent))
	# checar se intent já existe na tabela
	result = db.execute(f"""SELECT * FROM {tabela} where id_intent = %s""", (id_intent, ))
	rows = result.fetchone()
	intent_count = 1
	if rows:
			intent_count = int(rows['count']) + 1
			sql_txt = f"UPDATE {tabela} SET count = {intent_count} WHERE id_intent = '{id_intent}'"
	else:
			sql_txt = f"INSERT INTO {tabela} (id_intent, count) VALUES ('{id_intent}', {intent_count})"

	sql = text(sql_txt)
	sql_ok = db_execute_sql(sql, db)

	return sql_ok

# Consulta session origem
## Origem pode ser: webchat, aplicatico ou whatsapp
# def get_origem(user_id, db):

#       tabela = f"{DATABASE_NAME}.chat_session_origem"
#       #sql_txt = f"SELECT origem FROM {tabela} WHERE id_usuario = '{}'".format(tabela, user_id)
#       #sql = text(sql_txt)
#       result = db.execute(f"""SELECT origem FROM {tabela} WHERE id_usuario = %s""", (user_id, ))
#       rows = result.fetchone()

#       origem = ""
#       if rows:
#               origem = rows['origem']

#       return origem

# Recupera fallback count pelo session_id
def get_fallback_count(session_id, db):
	fallback_count = 0
	session_exists = False
	if session_id:
			tabela = f"{DATABASE_NAME}.chat_session_fallbacks"
			#sql_txt = f"SELECT fallback_count from {tabela} WHERE session_id = '{}'".format(session_id)

			#sql = text(sql_txt)
			result = db.execute(f"""SELECT fallback_count from {tabela} WHERE session_id = %s""", (session_id, ))
			rows = result.fetchone()

			if rows:
					session_exists = True
					fallback_count = rows['fallback_count']

	return fallback_count, session_exists

# Atualizar fallback count
def update_fallback_count(session_id, db, reset=False):
	tabela = f"{DATABASE_NAME}.chat_session_fallbacks"
	fallback_count, session_exists = get_fallback_count(session_id, db)
	if reset:
			print("RESET COUNT TRANSBORDOS")
			if not session_exists:
					fallback_count = 0
					sql_txt_user = "INSERT into {} (session_id, fallback_count) VALUES ('{}', 0)".format(tabela, session_id)
			else:
					sql_txt_user = "UPDATE {} SET fallback_count = 0 WHERE session_id = '{}'".format(tabela, session_id)
	else:
			if not session_exists:
					fallback_count = 1
					sql_txt_user = "INSERT into {} (session_id, fallback_count) VALUES ('{}', 1)".format(tabela, session_id)
			else:
					fallback_count += 1
					sql_txt_user = "UPDATE {} SET fallback_count = {} WHERE session_id = '{}'".format(tabela, fallback_count, session_id)

	sql_user = text(sql_txt_user)
	sql_ok = db_execute_sql(sql_user, db)
	print("FALLBACK_COUNT: {}".format(fallback_count))
	return sql_ok, fallback_count


# Recupera a parametrizacao dado um ID especifico
def get_parametro(id_param, db):
	tabela = f"{DATABASE_NAME}.chat_parametrizacoes"
	#sql_txt = "SELECT valor FROM ia_chat_carol_test.chat_parametrizacoes where id_param = '{}'".format(id_param)
	#sql = text(sql_txt)
	result = db.execute(f"""SELECT valor FROM {tabela} where id_param = %s""", (id_param,))
	rows = result.fetchone()

	valor = ""
	if rows:
			valor = rows['valor']

	return valor

# Recupera a lista de mensagens dado um ID especifico
def get_bot_messages(id_message, db):
	tabela = f"{DATABASE_NAME}.chat_mensagens"
	#sql_txt = "SELECT mensagem FROM ia_chat_carol_test.chat_mensagens WHERE id_msg = '{}'".format(id_message)
	#sql = text(sql_txt)
	results = db.execute(f"""SELECT mensagem FROM {tabela} WHERE id_msg = %s""", (id_message,))

	messages = []
	for row in results:
			messages.append(row['mensagem'])

	return messages


# Retorna as perguntas do faq do coronavírus de acordo com os ids informados
def get_perguntas(db, ids=0):
	tabela = f"{DATABASE_NAME}.chat_faq_avc"
	if ids:
			result = db.execute(f"SELECT pergunta FROM {tabela} where id in ({ids})")
	else:
			result = db.execute(f"SELECT pergunta FROM {tabela}")
	perguntas = []
	for row in result:
			perguntas.append(row['pergunta'])
	return perguntas

def get_resposta(id, db):
	tabela = f"{DATABASE_NAME}.chat_faq_todos"
	result = db.execute(f"SELECT resposta FROM {tabela} where id = {id}")
	resposta = ""
	for row in result:
			resposta = row['resposta']
	return resposta

def get_pergunta(id, db):
	tabela = f"{DATABASE_NAME}.chat_faq_todos"
	result = db.execute(f"SELECT pergunta FROM {tabela} where id = {id}")
	pergunta = ""
	for row in result:
			pergunta = row['pergunta']
	return pergunta

def get_link_FAQ(id, db):
	tabela = f"{DATABASE_NAME}.chat_faq_avc"
	result = db.execute(f"SELECT link_short FROM {tabela} where id = {id}")
	resposta = ""
	for row in result:
			resposta = row['link_short']
	return resposta	

def get_resposta_from_pergunta(pergunta, db):
	tabela = f"{DATABASE_NAME}.chat_faq_avc"
	result = db.execute(f"SELECT resposta FROM {tabela} where pergunta = '{pergunta}'")
	resposta = ""
	for row in result:
			resposta = row['resposta']
	return resposta

def get_faq_id_from_ent(user_choice, db):
	tabela = f"{DATABASE_NAME}.chat_faq_avc"
	result = db.execute(f"SELECT id FROM {tabela} where faq_ent = '{user_choice}'")
	id = ""
	for row in result:
			id = row['id']
	return id

# Recupera a intent atual da sessão
def get_current_intent(session_id, db):
	tabela = f"{DATABASE_NAME}.chat_session_current_intent"
	results = db.execute(f"""SELECT * FROM {tabela} WHERE session_id = '{session_id}' """)
	row = results.fetchone()

	current_intent = ''
	session_exists = ''
	if row:
			current_intent = row['current_intent_id']
			session_exists =  row['session_id']
	return current_intent, session_exists

# Atualiza no banco a intent atual da sessão
def update_current_intent(session_id, intent, db):
	tabela = f"{DATABASE_NAME}.chat_session_current_intent"
	_ , session_exists = get_current_intent(session_id, db)
	if session_exists:
			#"UPDATE {tabela} SET count = {intent_count} WHERE id_intent = '{id_intent}'"
			sql_text = f"""UPDATE  {tabela} SET current_intent_id = '{intent}' WHERE session_id = '{session_id}'"""
	else:
			sql_text = f"""INSERT INTO  {tabela} (session_id, current_intent_id) VALUES ('{session_id}','{intent}')"""
	sql = text(sql_text)
	sql_ok = db_execute_sql(sql, db)
	return sql_ok


# Recupera descricao de intencao para a funcionalidade de alterar dependente
def get_intent_description(dialogflow_intent_name, db):
	tabela = f"{DATABASE_NAME}.chat_intents"
	#sql_txt = "SELECT intent_description FROM ia_chat_carol_test.chat_intents where dialogflow = '{}'".format(dialogflow_intent_name)
	#sql = text(sql_txt)
	result = db.execute(f"""SELECT intent_description FROM {tabela} where dialogflow = %s""", (dialogflow_intent_name,))
	rows = result.fetchone()

	intent_description = ""
	if rows:
			intent_description = rows['intent_description']

	return intent_description



# Recupera nome da intencao no Dialogflow
def get_intent_id(dialogflow_intent_name, db):
	tabela = f"{DATABASE_NAME}.chat_intents"
	result = db.execute(f"""SELECT id_intent FROM {tabela} where dialogflow = %s""", (dialogflow_intent_name,))
	rows = result.fetchone()

	id_intent = ""
	if rows:
			id_intent = rows['id_intent']

	return id_intent

# Recupera URL de uma determinada API
def get_api_url(id_api, db):
	tabela = f"{DATABASE_NAME}.chat_apis"
	#sql_txt = "SELECT api_url FROM ia_chat_carol_test.chat_apis where id_api = '{}' and ambiente = '{}'".format(id_api, ambiente)
	#sql = text(sql_txt)
	result = db.execute(f"""SELECT api_url FROM {tabela} where id_api = %s""", (id_api,))
	rows = result.fetchone()

	api_url = ""
	if rows:
			api_url = rows['api_url']

	return api_url


def get_lista_perguntas(db):
	tabela = f"{DATABASE_NAME}.chat_faq_avc"
	result = db.execute(f"SELECT id, pergunta FROM {tabela}")
	# Converte a tupla para a lista no formato desejado
	lista_formatada = [f"{item[0]} - {item[1]}" for item in result]
	return str(lista_formatada)


def get_init_text(db):
	msg = get_bot_messages("INIT_GEMINI", db)
	lista = get_lista_perguntas(db)

	msg_init = msg + lista

	return msg_init




# Recupera a lista de mensagens dado um ID especifico
def get_gemini_keys(db):
	tabela = f"{DATABASE_NAME}.auth_gemini"
	results = db.execute(f"""SELECT key FROM {tabela}""")
	keys = []
	for row in results:
			keys.append(row['key'])

	return keys








# def update_info_sessao(session_id, codigo_ben, nome_ben, protocolo, phone_ben, db):
#       """Atualiza plataforma de origem do usuário (web/app/whats)"""
#       # Consulta prataforma de origem da sessão
#       tabela = f"{DATABASE_NAME}.chat_session_info"

#       if phone_ben:
#               sql_txt = f"INSERT INTO {tabela} (session_id, codigo_ben, nome_ben, protocolo, phone_ben) VALUES ('{session_id}', '{codigo_ben}', '{nome_ben}', '{protocolo}', '{phone_ben}')"
#       else:
#               sql_txt = f"INSERT INTO {tabela} (session_id, codigo_ben, nome_ben, protocolo) VALUES ('{session_id}', '{codigo_ben}', '{nome_ben}', '{protocolo}')"
#       sql = text(sql_txt)
#       sql_ok = db_execute_sql(sql, db)

#       return sql_ok

# Executa comando SQL
def db_execute_sql(sql, db, return_id=False):
	sql_ok = False
	try:
			result = db.execute(sql)
			sql_ok = True
	except:
			sql_ok = False

	if sql_ok and return_id:
			last_id = result.lastrowid
			return sql_ok, last_id

	return sql_ok