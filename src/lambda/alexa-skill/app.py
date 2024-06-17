import boto3
import pprint
import json
import time
import re
import os
import logging
import gettext

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractRequestInterceptor, AbstractExceptionHandler)
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from alexa import data

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

boto3_session = boto3.session.Session()
region = boto3_session.region_name

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.WELCOME_MESSAGE)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

class ConsultarDadosIntentHandler(AbstractRequestHandler):
    """Handler for ConsultarDados Intent."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ConsultarDadosIntent")(handler_input)
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        session_attr = handler_input.attributes_manager.session_attributes
        
        print(boto3.__version__)

        # Define o nome do bucket e o caminho do arquivo
        database = os.environ['glue_database']
        output_bucket = os.environ['output_bucket']
        
        question = handler_input.request_envelope.request.intent.slots["query"].value
        pprint.pprint(question)
        
        if "messages" not in session_attr:
            session_attr["messages"] = []
        
        messages = session_attr["messages"]
        messages.append(self.format_message("user", question))
    
        # Obtém o conteúdo do arquivo do S3
        # context = self.get_file_from_s3(bucket_name, file_key)
        context = self.get_context_file()
    
        if context:
    
            # Executa a query no Bedrock
            model_id = "anthropic.claude-3-haiku-20240307-v1:0" #"anthropic.claude-3-sonnet-20240229-v1:0"
            get_answer = self.query_bedrock(context, question, messages, model_id)
            pprint.pprint(get_answer)
            query_string = self.extract("query", get_answer)
            pprint.pprint(query_string)
            
            # Executa a query no Athena
            athena_results = self.execute_athena_query(query_string, database, output_bucket)
    
            # Processar a resposta do Athena
            print('Consulta Athena bem-sucedida!')
            pprint.pprint(athena_results)
            
             # Converter o dicionário athena_results em uma string
            athena_results_str = json.dumps(athena_results)
            
            prompt = f"""
                Responda a essa pergunta com os dados a seguir, em até 40 palavras, informe detalhes e responda em uma linha.
                Caso os valores aprentem casas decimais, mude para o padrão brasileiro, utilizando virgula ao inves de ponto.
                """
            
            # Executa novamente a query no Bedrock para pegar a frase final
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0" #"anthropic.claude-3-haiku-20240307-v1:0" #"anthropic.claude-3-sonnet-20240229-v1:0"
            final_answer = self.query_bedrock(prompt + athena_results_str, question, messages, model_id)
            
            session_attr["messages"].append(self.format_message("assistant", final_answer))
            
            return (
                handler_input.response_builder
                .speak(final_answer)
                .ask("O que mais você gostaria de saber?")
                .response
            )
        
        else:
            print(f"Error")
            return (
                handler_input.response_builder
                .speak("Não consegui levantar as informações solicitadas, por favor tente perguntar de outra maneira")
                .ask("O que mais você gostaria de saber?")
                .response
            )
    
    def extract(self, variable, assistant):
        plan_pattern = re.compile(r"<"+ variable + ">(.*?)<\/" + variable + ">", re.DOTALL)
        plan_match = plan_pattern.search(assistant)
        if (plan_match.group(1).strip()) is not None:
            return plan_match.group(1).strip()
    
    def format_message(self, role, text):
        formated_obj = {
                "role": role,
                "content": [
                    {"type": "text", "text": text}
                ]
            }
        return formated_obj
        
    def get_context_file(self):
        # Construir o caminho completo para o arquivo context.txt
        file_path = os.path.join(os.getcwd(), 'resource', 'context.txt')
    
        try:
            # Lê o conteúdo do arquivo context.txt
            with open(file_path, 'r') as file:
                conteudo = file.read()
            return conteudo
        except Exception as e:
            print(f"Erro ao carregar o arquivo context.txt: {e}")
            return None
    
    def get_file_from_s3(self, bucket_name, file_key):
        """
        Função para obter o conteúdo de um arquivo do S3.
        """
        s3 = boto3.client('s3')
    
        try:
            # Obtém o conteúdo do arquivo do S3
            system = s3.get_object(Bucket=bucket_name, Key=file_key)['Body'].read().decode('utf-8')
            return system
        except Exception as e:
            print(f"Erro ao carregar o arquivo {file_key}: {e}")
            return None
    
    def query_bedrock(self, context, question, messages, model_id):
        """
        Função para executar uma query no Bedrock e obter a resposta.
        """
        bedrock_client = boto3.client("bedrock-runtime")
        
        model_arn = f'arn:aws:bedrock:{region}::foundation-model/{model_id}'
        
        # Definir os parâmetros de entrada para o método retrieve_and_generate
        input_params = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "system": context,
            "messages": messages,
            "temperature": 0.5,
            "top_p": 0.999,
            "top_k": 250
        }
        
        # Chamar o método retrieve_and_generate e obter a resposta
        response = bedrock_client.invoke_model(body=json.dumps(input_params), modelId=model_id)
        response_body = json.loads(response.get('body').read())
        outputText = response_body.get('content')[0].get('text')
        cleantext = outputText.strip('\\')
        
        pprint.pprint(response_body)
    
        return cleantext
    
    def execute_athena_query(self, query_string, database, output_bucket):
        """
        Função para executar uma query no AWS Athena.
        """
        athena_client = boto3.client('athena')
    
        # Executar a query
        response = athena_client.start_query_execution(
            QueryString=query_string,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': f's3://{output_bucket}/query_results/'}
        )
    
        # Obter o ID da execução da query
        query_execution_id = response['QueryExecutionId']
    
        # Aguardar até que a query seja concluída
        while True:
            query_execution = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
            state = query_execution['QueryExecution']['Status']['State']
            if state == 'SUCCEEDED':
                break
            elif state == 'FAILED':
                raise Exception(f"Query failed with reason: {query_execution['QueryExecution']['Status']['StateChangeReason']}")
            else:
                time.sleep(0.05)  # Esperar 5 segundos antes de verificar novamente
    
        # Obter os resultados da query
        results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
    
        return results
    

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.HELP_MSG)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.GOODBYE_MSG)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        _ = handler_input.attributes_manager.request_attributes["_"]
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = _(data.REFLECTOR_MSG).format(intent_name)

        return (
            handler_input.response_builder
            .speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        _ = handler_input.attributes_manager.request_attributes["_"]
        speak_output = _(data.ERROR)

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )


class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        i18n = gettext.translation(
            'data', localedir='locales', languages=[locale], fallback=True)
        handler_input.attributes_manager.request_attributes["_"] = i18n.gettext

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

class LogRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        logger.info(f"Request type: {handler_input.request_envelope.request.object_type}")

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ConsultarDadosIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
# make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
sb.add_request_handler(IntentReflectorHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(LogRequestInterceptor())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
