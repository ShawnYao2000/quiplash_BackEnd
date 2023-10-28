import os
import json
from azure.cosmos import CosmosClient
from azure.functions import HttpRequest, HttpResponse

# Initialize CosmosDB client
url = os.environ.get("COSMOS_DB_URL")
key = os.environ.get("COSMOS_DB_KEY")
client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplash')
player_container = database.get_container_client('player')


def main(req: HttpRequest) -> HttpResponse:
    try:
        # Parse the request
        body = req.get_json()
        username = body["username"]
        password = body["password"]

        # Check username and password constraints
        if not (4 <= len(username) <= 14):
            return HttpResponse(
                json.dumps({"result": False, "msg": "Username less than 4 characters or more than 14 characters"}),
                mimetype="application/json")

        if not (10 <= len(password) <= 20):
            return HttpResponse(
                json.dumps({"result": False, "msg": "Password less than 10 characters or more than 20 characters"}),
                mimetype="application/json")

        # Check if username already exists in the database
        query = f"SELECT * FROM player p WHERE p.username = '{username}'"
        items = list(player_container.query_items(query, enable_cross_partition_query=True))

        if len(items) > 0:
            return HttpResponse(json.dumps({"result": False, "msg": "Username already exists"}),
                                mimetype="application/json")

        # If all checks pass, add the new player to the database
        player_data = {
            "username": username,
            "password": password,
            "games_played": 0,
            "total_score": 0
        }
        player_container.create_item(body=player_data)

        return HttpResponse(json.dumps({"result": True, "msg": "OK"}), mimetype="application/json")

    except Exception as e:
        return HttpResponse(json.dumps({"result": False, "msg": str(e)}), mimetype="application/json")