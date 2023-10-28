import os
import json
from azure.cosmos import CosmosClient
from azure.functions import HttpRequest, HttpResponse

# Initialize CosmosDB client
url = os.environ.get("COSMOS_DB_URL")
key = os.environ.get("COSMOS_DB_KEY")

client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplash')
prompt_container = database.get_container_client('prompt')
player_container = database.get_container_client('player')


def main(req: HttpRequest) -> HttpResponse:
    try:
        body = req.get_json()

        # Ensure only 'player' or 'word' or both are present, and no other keys
        if not (set(body.keys()) - {"player", "word"}):
            if "player" in body:
                username = body["player"]
                #If only player presented

                query = f"SELECT * FROM player p WHERE p.username = '{username}'"
                items = list(player_container.query_items(query, enable_cross_partition_query=True))

                if len(items) == 0:
                    return HttpResponse(
                        json.dumps({"result": False, "msg": "Player does not exist"}),
                        mimetype="application/json",
                        status_code=500
                    )
                else:
                    query = f"SELECT * FROM prompt p WHERE p.username = '{username}'"
                    prompt_items = list(prompt_container.query_items(query=query, enable_cross_partition_query=True))
                    deletedPrompt = len(prompt_items)
                    for item in prompt_items:
                        prompt_container.delete_item(item, partition_key=item['username'])
                    return HttpResponse(
                        json.dumps({"result": True, "msg": f"'{deletedPrompt}' prompts deleted"}),
                        mimetype="application/json"
                    )


            if "word" in body:
                word = body["word"]
                #If only word presented

        else:
            return HttpResponse(
                json.dumps({"result": False, "msg": "Invalid input. Please provide only 'player' and/or 'word'"}),
                mimetype="application/json",
                status_code=400,  # Bad Request
            )

    except Exception as e:
        return HttpResponse(
            json.dumps({"result":False, "msg": "Bad Request:" + str(e)}),
            mimetype="application/json",
            status_code=500
        )
