import json
import os
from azure.functions import HttpRequest, HttpResponse
from azure.cosmos import CosmosClient


url = "https://sy1g21-quiplash.documents.azure.com:443/"
key = "nojxN7ZQZsTdQKUpK8D7mZVqV2DUSqYtIgiCxeEu5zuam8BBFY13SmZsS8WKyMDTZqRC4MBXeA5fACDbHUhapg=="
client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplashdb')
player_container = database.get_container_client('player')


def main(req: HttpRequest) -> HttpResponse:
    if req.method == "GET":
        # Handle GET request with query parameters
        body = req.get_json()
        username = body["username"]
        password = body["password"]
    else:
        return HttpResponse(
            json.dumps({"result": False, "msg": "Unsupported HTTP method"}),
            mimetype="application/json",
            status_code=405,
        )

    # Query the database to find the user
    query = f"SELECT * FROM player p WHERE p.username = '{username}'"
    items = list(player_container.query_items(query, enable_cross_partition_query=True))

    if len(items) == 0 or items[0]["password"] != password:
        return HttpResponse(
            json.dumps({"result": False, "msg": "Username or password incorrect"}),
            mimetype="application/json",
        )

    return HttpResponse(json.dumps({"result": True, "msg": "OK"}), mimetype="application/json")

