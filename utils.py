import time

import utils
import database
import config
import intents

import random
from unicodedata import normalize
from difflib import SequenceMatcher
from operator import itemgetter
import re
import string
# Recupera sessionId do JSON de request do Dialogflow
def get_session_id(req):
	# LOGGER
	#logger = webhook_logger.get_logger(inspect.currentframe().f_code.co_name)

	sessionId = ""

	if not req:
			return sessionId

	session_info = req.get('session')
	if session_info:
			try:
					sessionId = session_info.split("/")[-1]
			except Exception as e:
					final_log = "session_info: {}".format(session_info)

	return sessionId


def build_new_context(agent_name, session_id, context_name, lifespan_count, context_params={}):
	"""Constrói um novo contexto baseado em um sessionId"""
	new_context = {}
	new_context['name'] = 'projects/{}/agent/sessions/{}/contexts/{}'.format(agent_name, session_id, context_name)
	new_context['lifespan_count'] = lifespan_count

	new_context['parameters'] = {}
	for param in context_params:
			new_context['parameters'][param] = context_params[param]

	return new_context




# Recupera nome do agente do JSON de request do Dialogflow
def get_agent_name(req):
	# LOGGER
	#logger = webhook_logger.get_logger(inspect.currentframe().f_code.co_name)

	agent_name = ""

	if not req:
			return agent_name

	session_info = req.get('session')
	if session_info:
			try:
					agent_name = session_info.split("/")[1]
			except Exception as e:
					final_log = "session_info: {}".format(session_info)

	return agent_name

# Recuperar um contexto especifico
def get_specific_context(outputContexts, contextName):
	specif_context = {}
	for i, contexts in enumerate(outputContexts):
			split_context_name = contexts.get('name').split('/')[-1]
			if split_context_name == contextName:
					specif_context = contexts
					break

	return specif_context



# Constroi response para o Dialogflow
def build_response(fulfillmentText="", followupEventInput="", outputContexts="", fulfillmentMessages="", contextsParams={} ):
	# LOGGER
	#logger = webhook_logger.get_logger(inspect.currentframe().f_code.co_name)

	data = {}

	if fulfillmentText and followupEventInput:
			data = {
					"fulfillmentText":fulfillmentText,
					"followupEventInput":{
							"name":followupEventInput
					}
			}
	elif fulfillmentText and outputContexts:
			if contextsParams:
					for param in contextsParams:
							try:
									outputContexts['parameters'][param] = contextsParams[param]
							except Exception as e:
									final_log = "fulfillmentText and outputContexts"
			if type(outputContexts) == list:
					data = {
							"fulfillmentText": fulfillmentText,
							"outputContexts": outputContexts
					}
			else:
					data = {
							"fulfillmentText": fulfillmentText,
							"outputContexts": [outputContexts]
					}
	elif followupEventInput and outputContexts:
			if contextsParams:
					for param in contextsParams:
							try:
									outputContexts['parameters'][param] = contextsParams[param]
							except Exception as e:
									final_log = "followupEventInput and outputContexts"
			if type(outputContexts) == list:
					data = {
							"outputContexts": outputContexts,
							"followupEventInput":{"name":followupEventInput}
					}
			else:
					data = {
							"outputContexts": [outputContexts],
							"followupEventInput":{"name":followupEventInput}
					}
	elif fulfillmentText:
			data = {
					"fulfillmentText": fulfillmentText
			}
	elif followupEventInput:
			data = {
					"followupEventInput":{
							"name":followupEventInput
					}
			}
	elif fulfillmentMessages and outputContexts:
			fulfillmentMessages = {
					"fulfillmentMessages": fulfillmentMessages
			}
			if contextsParams:
					for param in contextsParams:
							try:
									outputContexts['parameters'][param] = contextsParams[param]
							except Exception as e:
									final_log = "fulfillmentMessages and outputContexts"
			if type(outputContexts) == list:
					data = {
							"outputContexts": outputContexts,
							"fulfillmentText": str(fulfillmentMessages)
					}
			else:
					data = {
							"outputContexts": [outputContexts],
							"fulfillmentText": str(fulfillmentMessages)
					}
	elif fulfillmentMessages:
			fulfillmentMessages = {
					"fulfillmentMessages": fulfillmentMessages
			}
			data = {
					"fulfillmentText": str(fulfillmentMessages)
			}
	elif outputContexts:
			if contextsParams:
					for param in contextsParams:
							try:
									outputContexts['parameters'][param] = contextsParams[param]
							except Exception as e:
									final_log = "outputContexts"
			if type(outputContexts) == list:
					data = {
							"outputContexts": outputContexts
					}
			else:
					data = {
							"outputContexts": [outputContexts]
					}
	return data



def build_menu_perguntas(agent_name, session_id, assunto, db, outros_list = False):

	response = ""
	nome_tipo_prestador = ""
	tipoPrestador = ""

	nros_list = []
	perguntas = []
	ids = []

	n = int(database.get_parametro('PERGUNTAS_{}'.format(assunto), db))
	total = int(database.get_parametro('TOTAL_PERGUNTAS_{}'.format(assunto), db))
	ids_list =  database.get_faq_ids(db, assunto)
	sorteio = sorted(random.sample(ids_list, n))


	nros_list = ','.join([str(i) for i in range(1,n+3)])
	ids = ','.join([str(i) for i in sorteio])

	perguntas = database.get_perguntas(assunto, db, ids)
	perguntas.append('Outros assuntos.')
	perguntas.append('Voltar ao menu')

	#if outros_list:
	header_exemplos = "Estes são alguns assuntos que posso te responder:"
	#else: header_exemplos = str(random.choice(database.get_bot_messages('{}_INFORMACOES'.format(assunto), db)))

	menu_exemplos = ""
	for i, pergunta in enumerate(perguntas):
			menu_exemplos += "  {}. {}\n".format(i+1, pergunta)

	response = header_exemplos + '\n' + menu_exemplos

	params = {}
	params['ids'] = ids + ',X'
	params['nros_menu'] = nros_list
	params['header'] = header_exemplos
	params['response'] = response
	params['menu_exemplos'] = menu_exemplos

	new_context = utils.build_new_context(agent_name, session_id, "perguntas-context-{}".format(assunto.replace("_", "-").lower()), 5, context_params=params)
	response = utils.build_response(followupEventInput='FAQ_{}'.format(assunto), outputContexts=new_context)

	return response


def get_pergunta_from_lista(params, agent_name, session_id, assunto, db):

	user_choice = params['user_choice_faq']
	nros = params['nros_menu'].split(',')
	nros = [int(x) for x in nros]
	ids_perguntas = params['ids'].split(',')
	if ('outr' in user_choice.lower() or 'assunto' in  user_choice.lower()):
			new_context = build_new_context(agent_name, session_id, "{}-info-followup".format(assunto.replace("_", "-").lower()), 0)
			response = build_menu_perguntas(agent_name, session_id, assunto, db, outros_list = True)

	if ('menu' in user_choice.lower() or 'voltar' in  user_choice.lower()):
			response = utils.build_response(followupEventInput='MENU')			
	else:
			try:
					# tentar dar cast no nro, se falhar a resposta está escrita por extenso
					nro = int(user_choice)
					if nro and nro in nros:
							id = ids_perguntas[nro-1]
							if id == 'X':
									event = '{}_FAQ'.format(assunto)
									new_context = build_new_context(agent_name, session_id, "{}-info-followup".format(assunto.replace("_", "-").lower()), 100, context_params=params)
									response = build_menu_perguntas(agent_name, session_id, assunto, db, outros_list = True)
							else:
									params = {}
									resposta_faq = database.get_resposta(id, assunto, db)
									if assunto == "DICAS":
										link_faq = database.get_link_FAQ(id, assunto, db)
										resposta_faq = resposta_faq + "\nAcesse esse conteúdo completo em: " + link_faq
									pergunta_faq = database.get_perguntas(assunto, db, id)
									params['resposta_faq'] = resposta_faq.strip()
									params['pergunta_faq'] = pergunta_faq[0].strip()
									event = 'FAQ_{}_RESPOSTA'.format(assunto)
									new_context = build_new_context(agent_name, session_id, "{}-info-followup".format(assunto.replace("_", "-").lower()), 100, context_params=params)
									response = build_response(followupEventInput=event, outputContexts=new_context)
					else:
							# retry - número incorreto
							response = build_response(followupEventInput='FAQ_{}'.format(assunto))
			except ValueError as e:
					# busca por texto
					#id = database.get_faq_id_from_ent(user_choice, assunto, db)
					pergunta_faq = check_similaridade_perguntas(user_choice, assunto, db)
					if pergunta_faq[2]:
							resposta_faq = database.get_resposta_from_pergunta(pergunta_faq[0], assunto, db)
							params = {}
							params['resposta_faq'] = resposta_faq
							params['pergunta_faq'] = pergunta_faq[0]
							new_context = build_new_context(agent_name, session_id, "{}-info-followup".format(assunto.replace("_", "-").lower()), 100, context_params=params)
							response = build_response(followupEventInput='FAQ_{}_RESPOSTA'.format(assunto), outputContexts=new_context)
					else:
							response = build_response(followupEventInput='FAQ_{}'.format(assunto))

	return response


def check_similaridade_perguntas(user_query, assunto, db):
	similaridade_perguntas = float(database.get_parametro("SIMILARIDADE_PERGUNTAS", db))
	#similaridade_exames_utilizacao = 0.7
	voting = []
	user_query = normalizar(user_query)
	lista = database.get_perguntas(assunto, db)
	for i, pergunta in enumerate(lista):
			# [cod_ben, count, nome]
			print(lista[i])
			voting.append([lista[i], 0, lista[i]])
			similaridade = similar(normalizar_palavra(user_query), normalizar_palavra(lista[i]))
			if similaridade == 1:
					return lista[i], lista[i], True

	user_query_s = user_query.split()
	for k, query in enumerate(user_query_s):
			for i, pergunta in enumerate(lista):
					print("pergunta: {}".format(pergunta))
					lista_s = normalizar(pergunta).split()
					print("pergunta split: {}".format(lista_s))
					for n, texto_pergunta in enumerate(lista_s):
							similaridade = similar(normalizar_palavra(query), normalizar_palavra(texto_pergunta))
							if similaridade >= similaridade_perguntas:
									voting_count = voting[i][1]
									voting[i][1] += round(similaridade, 4)
	voting = sorted(voting, key=itemgetter(1), reverse=True)
	max_vote = voting[0][1]
	print("LISTA VOTING: {}".format(voting))
	if (len(voting) > 1 and float(voting[1][1]) == float(max_vote)) or (len(voting) == 1 and voting[0][1] == 0):
			return 0, 0, False
	if voting[0][1] <= 0:  return 0, 0, False
	return voting[0][0], voting[0][2], True



# Encontra similaridade entre duas strings
def similar(a, b):
	print("comparando {} com {}".format(a,b))
	return SequenceMatcher(None, a, b).ratio()

def normalizar_palavra(txt):
	txt = remover_acentos(txt)
	txt = txt.lower()
	txt = txt.strip()
	return txt


# Remove acentos de uma palavra
def remover_acentos(txt):
	return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def normalizar(text):
	"""Normalizar frase: lower case sem acentos, pontuações e caracteres especiais"""
	table = str.maketrans(string.punctuation, '                                ')
	text = remover_acentos(text)
	stripped = text.lower().translate(table)
	stripped = re.sub('\s+', ' ', stripped).strip()
	return stripped


def get_mensagem_dia(agent_name, session_id, db):
	#total = database.get_total_mensagens_dia(db)
	ids_list =  database.get_mensagens_dia_ids(db)
	sorteio = sorted(random.sample(ids_list, 1))
	ids = ','.join([str(i) for i in sorteio])
	mensagem = database.get_mensagem_dia(ids, db)
	params = {}
	params['mensagem_dia'] = mensagem
	new_context = utils.build_new_context(agent_name, session_id, "mensagem-dia-context", 5, context_params=params)
	response = utils.build_response(followupEventInput='MENSAGEM_DO_DIA', outputContexts=new_context)
	return response
