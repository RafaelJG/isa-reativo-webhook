import time

import utils
import database
import config
#import intents

from flask_sqlalchemy import SQLAlchemy

from flask import Flask, jsonify, request, make_response
from flask_cors import CORS, cross_origin
from six.moves import http_client
from flask_basicauth import BasicAuth

app = Flask(__name__)
CORS(app)

#Recuperaçãp de username e password utilizados na autenticação basic dos endpoints
app.config['BASIC_AUTH_USERNAME'] = config.BASIC_AUTH_NAME
app.config['BASIC_AUTH_PASSWORD'] = config.BASIC_AUTH_PASSWORD


#Configurações do banco
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

#Configuração da autenticação dos endpoints
basic_auth = BasicAuth(app)

@app.route('/dialogflow', methods=['POST'])
@basic_auth.required
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def dialogflow_webhook():


	tempo_start = time.time()
	response = ""
	# REMOTE CALLER IP
	try:
			ip = request.remote_addr
	except Exception as e:
			print("{}".format(e))

	req = request.get_json(force=True)
	print()
	print("-INICIO-------------------------------------------------------")
	print("REQUISICAO: {}".format(req))

	source = req.get('originalDetectIntentRequest').get('source')
	queryResult = req.get('queryResult')
	queryText = queryResult.get('queryText')
	outputContexts = queryResult.get('outputContexts')
	parameters = queryResult.get('parameters')
	intentName = queryResult.get('intent').get('displayName')
	agent_name =  utils.get_agent_name(req)
	limite_fallback = int(database.get_parametro('FALLBACK_COUNT_LIMITE', db))

	# SESSION ID
	sessionId = utils.get_session_id(req)


	# AGENT NAME
	agentName = utils.get_agent_name(req)

	id_intent = database.get_intent_id(intentName, db)
	sql_ok, inserted_id = database.insert_session_intent(id_intent, sessionId, db)
	print("INTENT ID: {}".format(id_intent))

	if id_intent:
			if id_intent != 'DEFAULT_FALLBACK' and "RETRY" not in id_intent :
					database.update_fallback_count(sessionId,db, reset=True)
			#else:
			#       response = utils.build_response(followupEventInput='DEFAULT_FALLBACK')
	if id_intent == 'DEFAULT_FALLBACK':
			if queryText != 'DEFAULT_FALLBACK':
					print("\nAconteceu um fallback\n")
					_ , count =  database.update_fallback_count(sessionId,db)
					print("Countagem fallback: {}".format(count))
					print("LIMITE FALLBACK: {}".format(limite_fallback))
					if count >= limite_fallback:
							response= utils.build_response(followupEventInput="TRANSBORDO")
	elif id_intent == 'MENU_INICIO' or id_intent == 'MENU':
			escolha = parameters.get('escolha-menu',"")
			if id_intent == 'MENU_INICIO':
				joinvasc = parameters.get('joinvasc',"")
				database.insert_joinvasc(sessionId, joinvasc, db)
			print('Opção do menu: {}'.format(parameters.get('escolha-menu',"")))
			if escolha == '1':
					# montar resposta para ir para a intencao de exames
					response = utils.build_response(followupEventInput='TRIAGEM_INICIO')
			elif escolha == '2':
					# montar resposta para ir para a intencao de exames
					response = utils.build_menu_perguntas(agent_name, sessionId, "AVC", db)
			elif escolha == '3':
					# montar resposta para ir para a intencao de exames
					response = utils.build_menu_perguntas(agent_name, sessionId, "POS_AVC", db)
			elif escolha == '4':
					# montar resposta para ir para a intencao de exames
					response = utils.build_menu_perguntas(agent_name, sessionId, "MEDICACAO", db)
			elif escolha == '5':
					# montar resposta para ir para a intencao de exames
					response = utils.build_menu_perguntas(agent_name, sessionId, "DICAS", db)
			elif escolha == '6':
					# montar resposta para ir para a intencao de exames
					response = utils.get_mensagem_dia(agent_name, sessionId, db)					
			elif escolha == '7':
					# montar resposta para ir para a intencao de exames
					response = utils.build_response(followupEventInput='SOBRE_ISA')
			elif escolha != '':
					#fallback normal, aceito pela entidade
					print("Escolha não vazia!!!!!!!")
					_, count = database.update_fallback_count(sessionId,db, reset=False)
					print("CONTAGEM FALLBACK: {}".format(count))
					print("LIMITE FALLBACK: {}".format(limite_fallback))
					if count >= int(limite_fallback):
							response = utils.build_response(followupEventInput='TRANSBORDO')
					else:
							response = utils.build_response(followupEventInput='MENU_RETRY')
			else:
					# não foi aceito pela entidade, entrou por evento ou entrou na funcionalidade por gatilho
					print("Escolha vazia!!!!!!!")
					detection_confidence = float(queryResult.get('intentDetectionConfidence', -1))
					print("DETECTION CONFIDENCE: {}".format(detection_confidence))
					if(queryText != 'MENU_RETRY' and detection_confidence < 0.3): #entrou por evento ou entrou por gatilho
							print("Entrou no if")
							_, count = database.update_fallback_count(sessionId,db, reset=False)  # se não foi nenhum desses casos, é realmente um fallback
							print("CONTAGEM FALLBACK: {}".format(count))
							print("LIMITE FALLBACK: {}".format(limite_fallback))
							if count >= int(limite_fallback):
									response = utils.build_response(followupEventInput='TRANSBORDO')
							else:
									response = utils.build_response(followupEventInput='MENU_RETRY')
					else:
							print("qualquer coisa")
	elif id_intent == 'TRIAGEM_INICIO':
			triagem_context = utils.get_specific_context(outputContexts, "inicio-triagem")
			params = triagem_context.get("parameters", {})
			escolha_triagem = params.get("escolha-triagem", "")
			if escolha_triagem == "continuar":
					response = utils.build_response(followupEventInput='TRIAGEM_SAMU')
			elif escolha_triagem == "emergencia":
					response = utils.build_response(followupEventInput='CHAMOU_EMERGENCIA')
	elif id_intent == 'CHAMOU_EMERGENCIA':
			emergencia_context = utils.get_specific_context(outputContexts, "chamou-emergencia")
			params = emergencia_context.get("parameters", {})
			ajudar_mais = params.get("ajudar-mais", "")
			if ajudar_mais == "sim":
					response = utils.build_response(followupEventInput='MENU')
			elif ajudar_mais == "não":
					response = utils.build_response(followupEventInput='ENCERRAMENTO')
	elif id_intent == 'FAQ_AVC':
			avc_context = utils.get_specific_context(outputContexts, "perguntas-context-avc")
			params = avc_context.get("parameters")
			response = utils.get_pergunta_from_lista(params, agent_name, sessionId, "AVC", db)
	elif id_intent == 'FAQ_DICAS':
		print("DICAS")
		avc_context = utils.get_specific_context(outputContexts, "perguntas-context-dicas")
		params = avc_context.get("parameters")
		response = utils.get_pergunta_from_lista(params, agent_name, sessionId, "DICAS", db)			
	elif id_intent == 'FAQ_POS_AVC':
			avc_context = utils.get_specific_context(outputContexts, "perguntas-context-pos-avc")
			params = avc_context.get("parameters")
			response = utils.get_pergunta_from_lista(params, agent_name, sessionId, "POS_AVC", db)
	elif id_intent == 'FAQ_MEDICACAO':
			avc_context = utils.get_specific_context(outputContexts, "perguntas-context-medicacao")
			params = avc_context.get("parameters")
			response = utils.get_pergunta_from_lista(params, agent_name, sessionId, "MEDICACAO", db)
	elif id_intent == 'SOBRE_ISA':
		context = utils.get_specific_context(outputContexts, "sobre-isa-context")
		params = context.get("parameters")
		ajudar_mais = params.get("escolha-ajudar-mais", "")
		print("ajudar mais: {}".format(ajudar_mais))
		if ajudar_mais == "sim":
				response = utils.build_response(followupEventInput='MENU')
		elif ajudar_mais == "não":
				response = utils.build_response(followupEventInput='ENCERRAMENTO')					
	elif id_intent == 'MENSAGEM_DO_DIA':
		context = utils.get_specific_context(outputContexts, "mensagem-dia-context")
		params = context.get("parameters")
		ajudar_mais = params.get("escolha-ajudar-mais", "")
		print("ajudar mais: {}".format(ajudar_mais))

		pesquisa = params.get("pesquisa", "")
		print("pesquisa: {}".format(pesquisa))
		print("Pesquisa context")
		print(context)
		pergunta = "blahhh"
		database.insert_pesquisa(sessionId, pergunta, pesquisa, db)
		if ajudar_mais == "sim":
				response = utils.build_response(followupEventInput='MENU')
		elif ajudar_mais == "não":
				response = utils.build_response(followupEventInput='ENCERRAMENTO')						
	elif id_intent == 'FAQ_AVC_RESPOSTA':
			avc_context = utils.get_specific_context(outputContexts, "perguntas-context-avc")
			params = avc_context.get("parameters")
			ajudar_mais = params.get("escolha-ajudar-mais", "")
			print("ajudar mais: {}".format(ajudar_mais))
			if ajudar_mais == "sim":
					response = utils.build_menu_perguntas(agent_name, sessionId, "AVC", db)
			elif ajudar_mais == "não":
					response = utils.build_response(followupEventInput='PESQUISA')
	elif id_intent == 'FAQ_POS_AVC_RESPOSTA':
			avc_context = utils.get_specific_context(outputContexts, "perguntas-context-pos-avc")
			params = avc_context.get("parameters")
			ajudar_mais = params.get("escolha-ajudar-mais", "")
			print("ajudar mais: {}".format(ajudar_mais))
			if ajudar_mais == "sim":
					response = utils.build_menu_perguntas(agent_name, sessionId, "POS_AVC", db)
			elif ajudar_mais == "não":
					response = utils.build_response(followupEventInput='PESQUISA')
	elif id_intent == 'FAQ_DICAS_RESPOSTA':
			avc_context = utils.get_specific_context(outputContexts, "perguntas-context-dicas")
			params = avc_context.get("parameters")
			ajudar_mais = params.get("escolha-ajudar-mais", "")
			print("ajudar mais: {}".format(ajudar_mais))
			if ajudar_mais == "sim":
					response = utils.build_menu_perguntas(agent_name, sessionId, "DICAS", db)
			elif ajudar_mais == "não":
					response = utils.build_response(followupEventInput='PESQUISA')					
	elif id_intent == 'FAQ_MEDICACAO_RESPOSTA':
			avc_context = utils.get_specific_context(outputContexts, "perguntas-context-medicacao")
			params = avc_context.get("parameters")
			ajudar_mais = params.get("escolha-ajudar-mais", "")
			print("ajudar mais: {}".format(ajudar_mais))
			if ajudar_mais == "sim":
					response = utils.build_menu_perguntas(agent_name, sessionId, "MEDICACAO", db)
			elif ajudar_mais == "não":
					response = utils.build_response(followupEventInput='PESQUISA')

	elif id_intent == 'TRIAGEM_SAMU':
			triagem_context = utils.get_specific_context(outputContexts, "triagem-followup")
			params = triagem_context.get("parameters", {})
			abraco = params.get("abraco", "")
			sorriso = params.get("sorriso", "")
			musica = params.get("musica", "")
			triagem = 0
			if abraco == "sim":
					triagem += 1
			if sorriso == "sim":
					triagem += 1
			if musica == "sim":
					triagem += 1
			if triagem <= 1:
					response = utils.build_response(followupEventInput='TRIAGEM_GERAL')
			else:
					response = utils.build_response(followupEventInput='TRIAGEM_EMERGENCIA')
	elif id_intent == 'TRIAGEM_GERAL':
			triagem_context = utils.get_specific_context(outputContexts, "triagem-followup")
			params = triagem_context.get("parameters", {})
			abraco = params.get("abraco", "")
			sorriso = params.get("sorriso", "")
			musica = params.get("musica", "")
			tontura = params.get("tontura", "")
			formigamento = params.get("formigamento", "")
			visao = params.get("visao", "")
			dorcabeca = params.get("dorcabeca", "")
			triagem = 0
			if tontura == "sim":
					triagem += 1
			if formigamento == "sim":
					triagem += 1
			if visao == "sim":
					triagem += 1
			if abraco == "sim":
					triagem += 3
			if sorriso == "sim":
					triagem += 3
			if musica == "sim":
					triagem += 3
			if dorcabeca == "sim":
					triagem += 1
			if triagem <= 5:
					response = utils.build_response(followupEventInput='TRIAGEM_24H')
			else:
					response = utils.build_response(followupEventInput='TRIAGEM_EMERGENCIA')
	elif id_intent == 'TRIAGEM_24H':
			triagem_context = utils.get_specific_context(outputContexts, "triagem-followup")
			params = triagem_context.get("parameters", {})
			triagem_ait = params.get("triagem_ait", "")
			if triagem_ait == "sim":
					response = utils.build_response(followupEventInput='TRIAGEM_AIT_FOLLOW')
			else:
					response = utils.build_response(followupEventInput='TRIAGEM_NO_AIT')
	elif id_intent == 'TRIAGEM_EMERGENCIA':
			print("emergencia samu")
			emergencia_context = utils.get_specific_context(outputContexts, "emergencia")
			params = emergencia_context.get("parameters", {})
			ajudar_mais = params.get("ajudar-mais", "")
			print("ajudar mais: {}".format(ajudar_mais))
			pesquisa = params.get("pesquisa", "")
			print("pesquisa: {}".format(pesquisa))
			print("Pesquisa context")
			print(emergencia_context)
			pergunta = "blahhh"
			database.insert_pesquisa(sessionId, pergunta, pesquisa, db)
			if ajudar_mais == "sim":
					response = utils.build_response(followupEventInput='MENU')
			elif ajudar_mais == "não":
					response = utils.build_response(followupEventInput='ENCERRAMENTO')

	elif id_intent == 'AJUDAR_MAIS':
			print("ajudar mais")
			ajudar_mais_context = utils.get_specific_context(outputContexts, "ajudar-mais")
			params = ajudar_mais_context.get("parameters", {})
			ajudar_mais = params.get("ajudar-mais", "")
			print("ajudar mais: {}".format(ajudar_mais))
			if ajudar_mais == "sim":
					response = utils.build_response(followupEventInput='MENU')
			elif ajudar_mais == "não":
					response = utils.build_response(followupEventInput='ENCERRAMENTO')
	elif id_intent == 'PESQUISA':
			print("pesquisa de satisfação")
			pesquisa_context = utils.get_specific_context(outputContexts, "pesquisa-satisfacao")
			params = pesquisa_context.get("parameters", {})
			pesquisa = params.get("pesquisa", "")
			print("pesquisa: {}".format(pesquisa))
			print("Pesquisa context")
			print(pesquisa_context)
			pergunta = "blahhh"
			database.insert_pesquisa(sessionId, pergunta, pesquisa, db)
			response = utils.build_response(followupEventInput='AJUDAR_MAIS')					









	print("RESPOSTA: {}".format(response))
	#logger.info("dialogflow response: {}".format(response))
	tempo_fim = time.time()
	print("TEMPO TOTAL: {}".format(tempo_fim-tempo_start))
	print("-FIM-------------------------------------------------------")
	print()

	return make_response(jsonify(response))

# Tratamento de erros de requisicao
@app.errorhandler(http_client.INTERNAL_SERVER_ERROR)
def unexpected_error(e):
	msg = format(e)
	print(msg)

	return response

if __name__ == '__main__':
	#app.run(host='127.0.0.1', port=8030, debug=True)
	app.run(host='0.0.0.0', debug=True)