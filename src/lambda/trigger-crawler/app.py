import boto3
import os

# Inicializar clientes da AWS
glue_client = boto3.client('glue')

# Obter o nome do Crawler do evento
crawler_name = os.environ['crawler']

def lambda_handler(event, context):
    try:
        # Iniciar o Crawler
        glue_client.start_crawler(
            Name=crawler_name
        )
        
        print(f"Crawler {crawler_name} iniciado com sucesso.")
        
    except Exception as e:
        print(f"Erro ao iniciar o Crawler {crawler_name}: {e}")
        raise e
        
    return {
        'statusCode': 200,
        'body': f"Crawler {crawler_name} iniciado com sucesso."
    }