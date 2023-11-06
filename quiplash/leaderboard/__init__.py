import json
import os
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions
from azure.functions import HttpRequest, HttpResponse

url = "https://sy1g21-quiplash.documents.azure.com:443/"
key = "nojxN7ZQZsTdQKUpK8D7mZVqV2DUSqYtIgiCxeEu5zuam8BBFY13SmZsS8WKyMDTZqRC4MBXeA5fACDbHUhapg=="

client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplashdb')
prompt_container = database.get_container_client('prompt')
player_container = database.get_container_client('player')


def main(req: HttpRequest) -> HttpResponse:
    try:
        body = req.get_json()
        k = body["top"]

        query = f"""
        SELECT TOP {k} c.username, c.games_played, c.total_score
        FROM c
        ORDER BY c.total_score DESC, c.games_played ASC, c.username ASC
        """

        parameters = [{"name": "@k", "value": k}]

        leaderboard = list(
            player_container.query_items(query, parameters=parameters, enable_cross_partition_query=True))

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
