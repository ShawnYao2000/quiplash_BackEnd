import os
import json
from azure.cosmos import CosmosClient
from azure.functions import HttpRequest, HttpResponse

url = os.environ["COSMOS_DB_URL"]
key = os.environ["COSMOS_DB_KEY"]

client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplashdb')
prompt_container = database.get_container_client('prompt')

def main(req: HttpRequest) -> HttpResponse:
    try:
        body = req.get_json()
        players = body["player"]
        language = body["language"]

        result = []

        for p in players:
            # Project only the necessary fields and filter the texts by the correct language
            query = f"SELECT c.id, t.text, c.username FROM c JOIN t IN c.texts WHERE c.username = '{p}' AND t.language = '{language}'"
            player_prompts = list(prompt_container.query_items(query, enable_cross_partition_query=True))

            # Flatten the results to match the expected output
            for prompt in player_prompts:
                player_result = {
                    "id": prompt['id'],
                    "text": prompt['text'],  # This now directly gets the text for the correct language
                    "username": prompt['username']
                }
                result.append(player_result)

        return HttpResponse(
            json.dumps(result),
            mimetype="application/json"
        )

    except Exception as e:
        return HttpResponse(
            json.dumps({"result": False, "msg": "Bad Request: " + str(e)}),
            mimetype="application/json",
            status_code=500
        )

