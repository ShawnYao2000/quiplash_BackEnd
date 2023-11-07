import os
import re
import json
from azure.cosmos import CosmosClient
from azure.functions import HttpRequest, HttpResponse

# Initialize CosmosDB client
url = "https://sy1g21-quiplash.documents.azure.com:443/"
key = "nojxN7ZQZsTdQKUpK8D7mZVqV2DUSqYtIgiCxeEu5zuam8BBFY13SmZsS8WKyMDTZqRC4MBXeA5fACDbHUhapg=="

client = CosmosClient(url, credential=key)
database = client.get_database_client('quiplashdb')
prompt_container = database.get_container_client('prompt')
player_container = database.get_container_client('player')


def main(req: HttpRequest) -> HttpResponse:
    try:
        body = req.get_json()

        # Ensure only 'player' or 'word' or both are present, and no other keys
        if not (set(body.keys()) - {"player", "word"}):
            if "player" in body:
                username = body["player"]
                # If delete player
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
                        json.dumps({"result": True, "msg": f"{deletedPrompt} prompts deleted"}),
                        mimetype="application/json"
                    )

            # ----------------------------------------------

            if "word" in body:
                word_to_delete = body["word"]
                # Regex pattern for whole word match, case-sensitive, only in English text
                pattern = fr'(?<!\S){re.escape(word_to_delete)}(?!\S)'

                # Query to fetch all prompts as Cosmos DB may not support regex within the query
                prompts = list(prompt_container.query_items(
                    query="SELECT * FROM prompt p",
                    enable_cross_partition_query=True
                ))
                deletedCount = 0

                for prompt in prompts:
                    # Filter only English texts
                    english_texts = [text for text in prompt['texts'] if text['language'] == 'en']
                    # Check if the word is present in any English text
                    if any(re.search(pattern, text_entry['text']) for text_entry in english_texts):
                        prompt_container.delete_item(prompt['id'], partition_key=prompt['username'])
                        deletedCount += 1

                # Return the HTTP response
                return HttpResponse(
                    json.dumps({"result": True, "msg": f"{deletedCount} prompts deleted"}),
                    mimetype="application/json"
                )


        else:
            return HttpResponse(
                json.dumps({"result": False, "msg": "Invalid input. Please provide only 'player' and/or 'word'"}),
                mimetype="application/json",
                status_code=400,  # Bad Request
            )

    except Exception as e:
        return HttpResponse(
            json.dumps({"result": False, "msg": "Bad Request: " + str(e)}),
            mimetype="application/json",
            status_code=500  # Indicating an Internal Server Error
        )

