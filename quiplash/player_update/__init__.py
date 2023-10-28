import json
import os
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions

url = os.environ.get("COSMOS_DB_URL")
key = os.environ.get("COSMOS_DB_KEY")
client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplash')
player_container = database.get_container_client('player')

def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "PUT":
        try:
            body = req.get_json()
            username = body.get("username")
            password = body.get("password")
            numGames = body.get("add_to_games_played")
            numScore = body.get("add_to_score")

            if not (username and password and numGames is not None and numScore is not None):
                return func.HttpResponse(
                    json.dumps({"result": False, "msg": "Invalid JSON data"}),
                    mimetype="application/json",
                    status_code=400,
                )

            query = f"SELECT * FROM player p WHERE p.username = '{username}'"
            items = list(player_container.query_items(query, enable_cross_partition_query=True))

            if len(items) == 0:
                return func.HttpResponse(
                    json.dumps({"result": False, "msg": "Player does not exist"}),
                    mimetype="application/json",
                    status_code=401,
                )
            else:
                currentGames = items[0]["games_played"] + numGames
                currentScore = items[0]["score"] + numScore

                # Update the values in the item
                items[0]["games_played"] = currentGames
                items[0]["score"] = currentScore

                player_container.replace_item(item=items[0], body=items[0])

                return func.HttpResponse(
                    json.dumps({"result": True, "msg": "OK"}),
                    mimetype="application/json",
                    status_code=200,
                )
        except exceptions.CosmosHttpResponseError as cosmos_error:
            return func.HttpResponse(
                json.dumps({"result": False, "msg": str(cosmos_error)}),
                mimetype="application/json",
                status_code=500,
            )
        except Exception as e:
            return func.HttpResponse(
                json.dumps({"result": False, "msg": str(e)}),
                mimetype="application/json",
                status_code=500,
            )
    else:
        return func.HttpResponse(
            json.dumps({"result": False, "msg": "Invalid Request Method"}),
            mimetype="application/json",
            status_code=400,
        )
