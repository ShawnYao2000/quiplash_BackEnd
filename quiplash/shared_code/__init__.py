import requests
import uuid
import json


translate_target = ['en', 'es', 'it', 'sv', 'ru', 'id', 'bg', 'zh-Hans']
def detect_lang(text):
    # Endpoint URL
    url = "https://api.cognitive.microsofttranslator.com/Detect?api-version=3.0"

    # Request headers
    headers = {
        "Ocp-Apim-Subscription-Key": "4c4d10c9912f44ce9c38ba16924b1ba9",  # Make sure to replace with your actual key
        "Ocp-Apim-Subscription-Region": "uksouth",
        "Content-Type": "application/json"
    }

    # Body
    body = [{"text": text}]

    # Initialize the return variable
    result = []

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, json=body)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Parse the response content for language code and score
        response_json = response.json()
        if response_json:
            # Assuming the response contains at least one detection result
            detection = response_json[0]
            lang_code = detection.get('language')
            # Casting score to float, generally not needed but here for demonstration
            score = float(detection.get('score', 0))  # Providing a default of 0 if score is not found
            result = [lang_code, score]

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(f"An error occurred: {e}")

    return result


def translate_lang(text_to_translate, from_lang):
    # Set up the endpoint and path for the Microsoft Translator API
    endpoint = "https://api.cognitive.microsofttranslator.com"
    path = '/translate'
    constructed_url = endpoint + path

    # Set the params for API
    params = {
        'api-version': '3.0',
        'from': from_lang,
        'to': translate_target
    }

    # Set the headers
    headers = {
        "Ocp-Apim-Subscription-Key": "4c4d10c9912f44ce9c38ba16924b1ba9",  # Make sure to replace with your actual key
        "Ocp-Apim-Subscription-Region": "uksouth",
        "Content-Type": "application/json",
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # Create the body
    body = [{
        'text': text_to_translate
    }]

    # Make the POST request to the Microsoft Translator API
    response = requests.post(constructed_url, params=params, headers=headers, json=body).json()

    # Parse the response to match the desired output format
    translation_output = []
    for language in translate_target:
        translated_text = next((trans['text'] for trans in response[0]['translations'] if trans['to'] == language), None)
        translation_output.append({"language": language, "text": translated_text})

    return translation_output


# Example usage:
translated_text = translate_lang(
    text_to_translate=": Anything between 400 (the minimum) and 600 is fine. You may delete the treehuggers database after finishing the lab activities if you want.",
    from_lang="en"
)

# Print the response in a formatted way
print(translated_text)