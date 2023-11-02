import json
import os
import re
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions

url = os.environ.get("COSMOS_DB_URL")
key = os.environ.get("COSMOS_DB_KEY")
client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplashdb')
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
                player_data = items[0]
                currentGames = safe_addition(player_data.get("games_played", 0), numGames)
                currentScore = safe_addition(player_data.get("total_score", 0), numScore)

                # You need to cast currentGames and currentScore to strings before concatenating with other strings for printing.
                print(f"currentGames: {currentGames}")
                print(f"currentScore: {currentScore}")

                player_data["games_played"] = currentGames
                player_data["total_score"] = currentScore

                player_container.replace_item(item=player_data, body=player_data)

                return func.HttpResponse(
                    json.dumps({"result": True, "msg": "OK"}),
                    mimetype="application/json",
                    status_code=200,
                )


        except Exception as e:
            return func.HttpResponse(
                json.dumps({"result": False, "msg HERE!": str(e)}),
                mimetype="application/json",
                status_code=500,
            )
    else:
        return func.HttpResponse(
            json.dumps({"result": False, "msg": "Invalid Request Method"}),
            mimetype="application/json",
            status_code=400,
        )

def safe_addition(value1, value2):
    # Try to convert both values to integers
    try:
        int_value1 = int(value1)
        int_value2 = int(value2)
        return int_value1 + int_value2
    except ValueError:
        # If it fails, then at least one value is a string, so convert both to strings
        str_value1 = str(value1)
        str_value2 = str(value2)
        return str_value1 + str_value2