import utils
import database
import config

import io
import base64
import random
import json
import inspect

from sqlalchemy import text




def preparacao_exames(busca_exame, db):

	prep_exame = []
	if busca_exame == "batata":
		prep_exame.append("prep batata")
	elif busca_exame == "banana":
		prep_exame.append("prep batata")
		prep_exame.append("prep batata")
		prep_exame.append("prep batata")

	return prep_exame



def get_dados_unidades(bairro_busca, db):

	unidades = []
	unidades = database.get_detalhes_unidades(bairro_busca, db)
	
	return unidades

def get_unidades(bairro_busca, db):

	unidades = []
	unidades = database.get_nome_unidades(bairro_busca, db)
	
	return unidades	



def get_exames(exame_busca, db):

	exames = []
	exames = database.get_exames(exame_busca, db)
	return exames
		
def get_exame_from_pergunta(escolha, exames_encontrados, db):
	print("Escolha: {}/n EXAMES ENCONTRADOS: /n{}".format(escolha, exames_encontrados))
	exame_escolhido = exames_encontrados[int(escolha)-1]
	print("Exame escolhido: {}".format(exame_escolhido))
	#prep_exame = get_prep_exames(exame_escolhido, db)

	return exame_escolhido