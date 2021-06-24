"""This is a set of configuration classes, one of which is selected by the APP_ENV variable."""

class BaseConfig():
	"""configuração default"""
	BASIC_AUTH_NAME = "uvn-chatbot-ia"
	BASIC_AUTH_PASSWORD = "uvn-chatbot-ia-secret-key"
	LOGSTASH_CLIENTE = "unimedfederacaopr"
	LOGSTASH_CHAT = "carol"
	LOGSTASH_INSTANCIA = "ia"
	LOGSTASH_SERVICO = "webhook"
	#DATABASE_NAME = "ia_chat_terapias"



class DevConfig(BaseConfig):
	"""configuração ambiente de desenvolvimento"""
	FLASK_ENV = 'dev'
	LOGSTASH_AMBIENTE = "test"
	LOGSTASH_EXTRA = {
		"appName": "chatbot-ia-laboratorios-webhook",
		"profile": "test"
	}
	URL_ADMIN = "https://adm-test.appunimed.com" 
	DATABASE_NAME = "isa_reativo"
	SQLALCHEMY_DATABASE_URI =  "mysql://chatbot_isa:chatbot-isa-secret-key@host.docker.internal:3316/isa_reativo"
	LOGSTASH_HOST = "10.128.0.10"
	AUTHORIZATION = "Y2hhdGJvdC1pYTpjaGF0Ym90LWlhLXNlY3JldC1rZXk="
	API_TIMEOUT_LIMIT = 5

class HomConfig(BaseConfig):
	"""configuração ambiente de homologação"""
	FLASK_ENV = 'hom'
	LOGSTASH_AMBIENTE = "hom"
	LOGSTASH_EXTRA = {
		"appName": "chatbot-ia-laboratorios-webhook",
		"profile": "hom"
	}
	URL_ADMIN = "https://adm-test.appunimed.com" 
	DATABASE_NAME = "ia_chat_laboratorios_hom"
	SQLALCHEMY_DATABASE_URI =  "mysql://iaunivision:ia-univision-secret-key@sql-proxy:3311/ia_chat_laboratorios_hom"
	LOGSTASH_HOST = "10.128.0.10"
	AUTHORIZATION = "Y2hhdGJvdC1pYTpjaGF0Ym90LWlhLXNlY3JldC1rZXk="
	API_TIMEOUT_LIMIT = 5



class ProductionConfig(BaseConfig):
	"""configuração ambiente de produção"""
	FLASK_ENV = 'production'
	LOGSTASH_AMBIENTE = "prod"
	LOGSTASH_EXTRA = {
		"appName": "chatbot-ia-laboratorios-webhook",
		"profile": "prod"
	}
	URL_ADMIN = "https://adm-test.appunimed.com" 
	DATABASE_NAME = "ia_chat_laboratorios"
	SQLALCHEMY_DATABASE_URI =  "mysql://iaunivision:ia-univision-secret-key@sql-proxy:3309/ia_chat_laboratorios"
	LOGSTASH_HOST = "vm-elk-2.us-east1-d.c.ucwbmobile-hom.internal"
	AUTHORIZATION = "Y2hhdGJvdC1pYTpjaGF0Ym90LWlhLXNlY3JldC1rZXk="
	API_TIMEOUT_LIMIT = 5




