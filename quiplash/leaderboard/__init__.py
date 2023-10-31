import json
import os
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions
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
        k = body["top"]

        # SQL query to fetch the top k players
        query = f"""
        SELECT TOP @k c.username, c.games_played, c.total_score
        FROM c
        ORDER BY c.total_score DESC, c.games_played ASC, c.username ASC
        """

        parameters = [{"name": "@k", "value": k}]

        leaderboard = list(
            player_container.query_items(query, parameters=parameters, enable_cross_partition_query=True))

        # Convert games_played and total_score to string if required
        for player in leaderboard:
            player["games_played"] = str(player["games_played"])
            player["total_score"] = str(player["total_score"])

        return HttpResponse(
            json.dumps(leaderboard),
            mimetype="application/json"
        )

    except Exception as e:
        return HttpResponse(
            json.dumps({"result": False, "msg": "Bad request: " + str(e)}),
            mimetype="application/json",
            status_code=500
        )
