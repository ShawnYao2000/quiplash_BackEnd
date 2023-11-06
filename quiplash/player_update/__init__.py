import json
import os
import re
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions

url = "https://sy1g21-quiplash.documents.azure.com:443/"
key = "nojxN7ZQZsTdQKUpK8D7mZVqV2DUSqYtIgiCxeEu5zuam8BBFY13SmZsS8WKyMDTZqRC4MBXeA5fACDbHUhapg=="
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
            
            if not (is_number(numGames) and is_number(numScore)):
                return func.HttpResponse(
                    json.dumps({"result": False, "msg": "Input numbers as scores/games"}),
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
                currentGames = player_data.get("games_played", 0) + numGames
                currentScore = player_data.get("total_score", 0) + numScore

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

    
def is_number(value):
    return isinstance(value, (int, float, complex))