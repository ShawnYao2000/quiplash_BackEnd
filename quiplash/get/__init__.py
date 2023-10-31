import os
import json
from azure.cosmos import CosmosClient
from azure.functions import HttpRequest, HttpResponse

url = os.environ.get("COSMOS_DB_URL")
key = os.environ.get("COSMOS_DB_KEY")

client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplash')
prompt_container = database.get_container_client('prompt')
player_container = database.get_container_client('player')

def main(req: HttpRequest) -> HttpResponse:
    try:
        body = req.get_json()
        players = body["player"]
        language = body["language"]

        result = []  # This will store the combined results

        for p in players:
            query = f"SELECT * FROM prompt p WHERE p.username = '{p}' AND ARRAY_CONTAINS({{'language': '{language}'}}, p.texts)"
            player_prompts = list(prompt_container.query_items(query, enable_cross_partition_query=True))

            # If you want each player's prompts in a separate object:
            player_result = {
                "text": player_prompts,
                "username": p
            }
            result.append(player_result)

        return HttpResponse(
            json.dumps(result),
            mimetype="application/json"
        )

    except Exception as e:
        return HttpResponse(
            json.dumps({"result":False, "msg": "Bad Request:" + str(e)}),
            mimetype="application/json",
            status_code=500
        )