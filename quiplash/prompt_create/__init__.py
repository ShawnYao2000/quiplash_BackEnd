import os
import json

from azure.cosmos import CosmosClient
from azure.functions import HttpRequest, HttpResponse
from ..shared_code import detect_lang, translate_lang


# Initialize CosmosDB client
url = os.environ.get("COSMOS_DB_URL")
key = os.environ.get("COSMOS_DB_KEY")

# Initialize translation service
translator_key = os.environ.get("TRANSLATOR_TEXT_SUBSCRIPTION_KEY")
translator_endpoint = os.environ.get("TRANSLATOR_TEXT_ENDPOINT")
translator_location = os.environ.get("TRANSLATOR_TEXT_LOCATION")

client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplashdb')
prompt_container = database.get_container_client('prompt')
player_container = database.get_container_client('player')
supported_lang = ['en', 'es', 'it', 'sv', 'ru', 'id', 'bg', 'zh-Hans']

#{id: "", username: "", texts: [{"language": "en", "text": "blahblah"}]}

def main(req:HttpRequest) ->HttpResponse:
    try:
        body = req.get_json()
        text = body["text"]
        username = body["username"]

        textDetect = detect_lang(text)
        detected_language = textDetect[0]
        confidence = textDetect[1]

        if len(text) < 15 or len(text) >80:
            return HttpResponse(
                json.dumps({"result":False, "msg": "Prompt less than 15 characters or more than 80 characters"}),
                mimetype="application/json",
                status_code=200,
            )

        if detected_language not in supported_lang or (detected_language in supported_lang and confidence < 0.3):
            return HttpResponse(
                json.dumps({"result": False, "msg": "Unsupported language or insufficient confidence"}),
                mimetype="application/json",
                status_code=200,
            )

        query = f"SELECT * FROM player p WHERE p.username = '{username}'"
        items = list(player_container.query_items(query, enable_cross_partition_query=True))
        if len(items) == 0:
            return HttpResponse(
                json.dumps({"result": False, "msg": "Player does not exist"}),
                mimetype="application/json",
                status_code=200,
            )

        #passed all checks

        #construct insertion
        translated_lang = translate_lang(text, detected_language)

        prompt_data = {
            "texts": translated_lang,
            "username": username
        }
        prompt_container.create_item(body=prompt_data, enable_automatic_id_generation=True)
        return HttpResponse(
            json.dumps({"result": True, "msg": "OK"}),
            mimetype="application/json",
        )

    except Exception as e:
        print(e)
        return HttpResponse(
            json.dumps({"result": False, "msg": "Bad Request:" + str(e)}),
            mimetype="application/json",
            status_code=500,
        )