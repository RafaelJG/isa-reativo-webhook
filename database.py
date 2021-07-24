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


def get_faq_ids(db, assunto):
	tabela = f"{DATABASE_NAME}.chat_faq_{assunto.lower()}"


	sql_txt = f"SELECT id FROM {tabela}"
	result = db.engine.execute(sql_txt)
	ids =[]
	for row in result:
			ids.append(row['id'])
	return ids



# Atualiza contagem da intenção
def update_intent_count(id_intent, db):
	tabela = f"{DATABASE_NAME}.chat_intents_count"

	print("ID_INTENT: {}".format(id_intent))
	# checar se intent já existe na tabela
	result = db.engine.execute(f"""SELECT * FROM {tabela} where id_intent = %s""", (id_intent, ))
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
#       result = db.engine.execute(f"""SELECT origem FROM {tabela} WHERE id_usuario = %s""", (user_id, ))
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
			result = db.engine.execute(f"""SELECT fallback_count from {tabela} WHERE session_id = %s""", (session_id, ))
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
	result = db.engine.execute(f"""SELECT valor FROM {tabela} where id_param = %s""", (id_param,))
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
	results = db.engine.execute(f"""SELECT mensagem FROM {tabela} WHERE id_msg = %s""", (id_message,))

	messages = []
	for row in results:
			messages.append(row['mensagem'])

	return messages


# Retorna as perguntas do faq do coronavírus de acordo com os ids informados
def get_perguntas(assunto, db, ids=0):
	tabela = f"{DATABASE_NAME}.chat_faq_{assunto.lower()}"
	if ids:
			result = db.engine.execute(f"SELECT pergunta FROM {tabela} where id in ({ids})")
	else:
			result = db.engine.execute(f"SELECT pergunta FROM {tabela}")
	perguntas = []
	for row in result:
			perguntas.append(row['pergunta'])
	return perguntas

def get_resposta(id, assunto, db):
	tabela = f"{DATABASE_NAME}.chat_faq_{assunto.lower()}"
	result = db.engine.execute(f"SELECT resposta FROM {tabela} where id = {id}")
	resposta = ""
	for row in result:
			resposta = row['resposta']
	return resposta

def get_resposta_from_pergunta(pergunta, assunto, db):
	tabela = f"{DATABASE_NAME}.chat_faq_{assunto.lower()}"
	result = db.engine.execute(f"SELECT resposta FROM {tabela} where pergunta = '{pergunta}'")
	resposta = ""
	for row in result:
			resposta = row['resposta']
	return resposta

def get_faq_id_from_ent(user_choice, assunto, db):
	tabela = f"{DATABASE_NAME}.chat_faq_{assunto.lower()}"
	result = db.engine.execute(f"SELECT id FROM {tabela} where faq_ent = '{user_choice}'")
	id = ""
	for row in result:
			id = row['id']
	return id

# Recupera a intent atual da sessão
def get_current_intent(session_id, db):
	tabela = f"{DATABASE_NAME}.chat_session_current_intent"
	results = db.engine.execute(f"""SELECT * FROM {tabela} WHERE session_id = '{session_id}' """)
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
	result = db.engine.execute(f"""SELECT intent_description FROM {tabela} where dialogflow = %s""", (dialogflow_intent_name,))
	rows = result.fetchone()

	intent_description = ""
	if rows:
			intent_description = rows['intent_description']

	return intent_description



# Recupera nome da intencao no Dialogflow
def get_intent_id(dialogflow_intent_name, db):
	tabela = f"{DATABASE_NAME}.chat_intents"
	result = db.engine.execute(f"""SELECT id_intent FROM {tabela} where dialogflow = %s""", (dialogflow_intent_name,))
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
	result = db.engine.execute(f"""SELECT api_url FROM {tabela} where id_api = %s""", (id_api,))
	rows = result.fetchone()

	api_url = ""
	if rows:
			api_url = rows['api_url']

	return api_url

# Consulta nome da cidade dado o codigo IBGE
def get_nome_cidade(cod, db):
	tabela = f"{DATABASE_NAME}.chat_cidades"
	nome_cidade = ""
	#sql_txt = "SELECT cidade FROM ia_chat_carol_test.chat_cidades WHERE id LIKE \'" + str(cod) + "\'"
	#sql = text(sql_txt)
	result = db.engine.execute(f"""SELECT cidade FROM {tabela} WHERE id = %s""", (str(cod),))
	rows = result.fetchone()

	if rows:
			nome_cidade = rows['cidade']

	return nome_cidade

# Consulta codigo IBGE de uma cidade pelo nome
def get_cidade(cidade, db, estado = ""):
	cod_cidade = ""
	tabela = f"{DATABASE_NAME}.chat_cidades"
	#sql_txt = "SELECT * FROM ia_chat_carol_test.chat_cidades WHERE cidade LIKE \'" + str(querry) + "\'"
	#sql = text(sql_txt)
	if estado:
			result = db.engine.execute(f"""SELECT * FROM {tabela} WHERE cidade = %s and UF = %s""", (cidade, estado))
	else:
			result = db.engine.execute(f"""SELECT * FROM {tabela} WHERE cidade = %s""", (cidade,))
	rows = result.fetchone()

	if rows:
			cod_cidade = rows['id']

	return cod_cidade

# Verifica se a cidade pertence ao estado informado
def check_cidade_estado(cidade, estado, db):
	tabela = f"{DATABASE_NAME}.chat_cidades"
	cod_cidade = ""
	result = db.engine.execute(f"""SELECT * FROM {tabela} WHERE cidade = %s and UF = %s""", (cidade, estado,))
	rows = result.fetchone()

	if rows:
			cod_cidade = rows['id']

	return cod_cidade



# Consulta protocolo do usuario
def get_protocolo(user_id, db):

	tabela = f"{DATABASE_NAME}.chat_beneficiarios_web"
	#sql_txt = "SELECT protocolo FROM ia_chat_carol_test.chat_beneficiarios_web WHERE id_usuario LIKE '{}'".format(str(user_id))
	#sql = text(sql_txt)
	result = db.engine.execute(f"""SELECT protocolo FROM {tabela} WHERE id_usuario = %s""", (user_id,))
	rows = result.fetchone()

	protocolo = ""
	if rows:
			protocolo = rows['protocolo']

	return protocolo



# Consulta protocolo do usuario
def get_preparacao_exames(busca_exame, db):

	tabela = f"{DATABASE_NAME}.chat_exames"
	#sql_txt = "SELECT protocolo FROM ia_chat_carol_test.chat_beneficiarios_web WHERE id_usuario LIKE '{}'".format(str(user_id))
	#sql = text(sql_txt)
	result = db.engine.execute("""SELECT mnemonico, nome_exame, preparacao_exame FROM {} WHERE nome_exame='{}'""".format(tabela, busca_exame))
	rows = result.fetchone()

	result = {}
	if rows:
			result['preparacao_exame'] = rows['preparacao_exame']
			result['mnemonico'] = rows['mnemonico']
			result['nome_exame'] = rows['nome_exame']

	return result

# Consulta protocolo do usuario
def get_exames(busca_exame, db):

	tabela = f"{DATABASE_NAME}.chat_exames"
	#sql_txt = "SELECT protocolo FROM ia_chat_carol_test.chat_beneficiarios_web WHERE id_usuario LIKE '{}'".format(str(user_id))
	#sql = text(sql_txt)
	sql_txt = f"SELECT mnemonico, nome_exame FROM {tabela} WHERE sinonimos_exame LIKE '%%{busca_exame}%%'"
	print("Comando SQL:{}".format(sql_txt))
	#sql = text(sql_txt)
	result = db.engine.execute(sql_txt)
	exame = [row['nome_exame'] for row in result]

	return exame


def get_detalhes_unidades(busca_bairro, db):

	tabela = f"{DATABASE_NAME}.chat_unidades"

	sql_txt = f"SELECT dados_unidade, link_maps FROM {tabela} WHERE bairros_unidade LIKE '%%{busca_bairro}%%'"
	print("Comando SQL:{}".format(sql_txt))
	#sql = text(sql_txt)
	result = db.engine.execute(sql_txt)
	unidades = [row['dados_unidade'] + "\n    " + row['link_maps'] for row in result]

	return unidades

def get_nome_unidades(busca_bairro, db):

	tabela = f"{DATABASE_NAME}.chat_unidades"

	sql_txt = f"SELECT nome_unidade FROM {tabela} WHERE bairros_unidade LIKE '%%{busca_bairro}%%'"
	print("Comando SQL:{}".format(sql_txt))
	#sql = text(sql_txt)
	result = db.engine.execute(sql_txt)
	unidades = [row['nome_unidade'] for row in result]


	return unidades















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
			result = db.engine.execute(sql)
			db.session.commit()
			sql_ok = True
	except:
			sql_ok = False
			db.session.rollback()

	db.session.close()

	if sql_ok and return_id:
			last_id = result.lastrowid
			return sql_ok, last_id

	return sql_ok