import os
import json
from azure.cosmos import CosmosClient
from azure.functions import HttpRequest, HttpResponse
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from azure.cognitiveservices.language.textanalytics.models import DetectedLanguage
from msrest.authentication import CognitiveServicesCredentials


# Initialize CosmosDB client
url = os.environ.get("COSMOS_DB_URL")
key = os.environ.get("COSMOS_DB_KEY")
subscription_key = os.environ.get("SUBSCRIPTION_KEY")
endpoint = os.environ.get("ENDPOINT")

client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplash')
prompt_container = database.get_container_client('prompt')
player_container = database.get_container_client('player')

text_analytics_client = TextAnalyticsClient(endpoint, credentials=CognitiveServicesCredentials(subscription_key))

#{id: "", username: "", texts: [{"language": "en", "text": "blahblah"}]}

def main(req:HttpRequest) ->HttpResponse:
    try:
        body = req.get_json()
        text = body["text"]
        username = body["username"]

        documents = [DetectedLanguage(id="1", text = text)]
        result = text_analytics_client.detect_language(documents=documents)
        detected_language = result.documents[0].detected_languages[0].name
        confidence = result.documents[0].detected_languages[0].score

        if len(text) < 15 or len(text) >80:
            return HttpResponse(
                json.dumps({"result":False, "msg": "Prompt less than 15 characters or more than 80 characters"}),
                mimetype="application/json",
                status_code=200,
            )

        if detected_language not in ['en', 'es'] or (detected_language in ['en', 'es'] and confidence < 0.8):
            return HttpResponse(
                json.dumps({"result": False, "msg": "Unsupported language"}),
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
        prompt_data = {
            "text": text,
            "username": username
        }
        prompt_container.create_item(body=prompt_data)
        return HttpResponse(
            json.dumps({"result": True, "msg": "OK"}),
            mimetype="application/json",
        )

    except Exception:
        return HttpResponse(
            json.dumps({"result": False, "msg": "Bad Request: Unable to get JSON"}),
            mimetype="application/json",
            status_code=500,
        )