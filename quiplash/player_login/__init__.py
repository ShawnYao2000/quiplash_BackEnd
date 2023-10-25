from azure.functions import HttpRequest, HttpResponse
import json

from quiplash.player_register import player_container


def login(req: HttpRequest) -> HttpResponse:
    body = req.get_json()
    username = body["username"]
    password = body["password"]

    # Query the database to find the user
    query = f"SELECT * FROM player p WHERE p.username = '{username}'"
    items = list(player_container.query_items(query, enable_cross_partition_query=True))

    if len(items) == 0 or items[0]["password"] != password:
        return HttpResponse(json.dumps({"result": False, "msg": "Username or password incorrect"}),
                            mimetype="application/json")

    return HttpResponse(json.dumps({"result": True, "msg": "OK"}), mimetype="application/json")
