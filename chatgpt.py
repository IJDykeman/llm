import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import json
from print_colors import *
import openai


def system_message(contet):
    return {"role": "system", "content": contet}

def user_message(content):
    return {"role": "user", "content": content}

def assistant_message(content):
    return {"role": "assistant", "content": content}

def generate_chat_response_one_req(messages):

    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
     "model": "gpt-3.5-turbo",
     "messages": messages,
     "temperature": 0.7,
    }

    print ("Waiting for response... ")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(data),
    )

    response_json = response.json()
    # print(response_json)
    result = response_json["choices"][0]["message"]["content"].strip()
    print_green(result)
    return result

def generate_chat_response_streaming(messages, timeout_seconds=10, max_retries=3, print_fn=print_green):
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7,
        "stream": True,
    }

    for attempt in range(max_retries):
        try:
            print("Waiting for response... ")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(data),
                stream=True,
                timeout=timeout_seconds
            )

            result = ""
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith("data:"):
                    event_data = line[5:].strip()
                    if event_data != '[DONE]':
                        delta = json.loads(event_data)['choices'][0]['delta']
                        if 'content' in delta:
                            new_content = delta['content']
                            print_fn(new_content, end="", flush=True)
                            result += new_content
            print_fn()
            return result
        except requests.exceptions.Timeout:
            print(f"Timeout after {timeout_seconds} seconds. Retrying...")

    print_fn()
    return f"Failed to get a response after {max_retries} attempts."


def generate_chat_response_api(messages):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7,
    }

    print("Waiting for response... ")
    response = openai.ChatCompletion.create(**data)

def generate_chat_response(conversation):
    try:
        # response = generate_chat_response_one_req(conversation)
        # return response
        response = generate_chat_response_streaming(conversation)
        return response
    except Exception as e:
        print_red(f"Error: {e}")
        return "Error: " + str(e)






    result = response.choices[0].message.content.strip()
    print_green(result)
    return result

if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Give a rousing speech in the style of the Gettysburg Address on good software practices.  Reference violent struggle and keep it short."},
    ]
    generate_chat_response(messages)
