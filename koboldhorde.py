import discord
import asyncio
import requests
import json
import nltk
from nltk.tokenize import word_tokenize
import time


api_endpoint = "https://koboldai.net/api/v2/"

async def main():
    # load model
    def checkModel():
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        }
        response = requests.request("GET", api_endpoint + "/model", headers=headers)
        return response

    response = checkModel()
    model_response_json = json.loads(response.content.decode("utf-8"))
    print(model_response_json["result"])


# discord connection
intents = discord.Intents.default()
intents.message_content = True
intents = discord.Intents.default(
)
intents.typing = True
intents.presences = True
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

def tokenize_message(message_content):
    words = word_tokenize(message_content)
    return len(words)

@client.event
async def on_ready():
    print(f'The AI has logged in as {client.user}.')

dialogue_history = []
total_tokens = 0

def reset_dialogue_history():
    global dialogue_history
    global total_tokens
    dialogue_history = []
    total_tokens = 0


def update_dialogue_history(message_content):
    global dialogue_history
    global total_tokens
    tokens = word_tokenize(message_content)
    if total_tokens + len(tokens) > 1024:
        reset_dialogue_history()
        print("Memory reset.")
    else:
        dialogue_history.append(message_content)
        total_tokens += len(tokens)
        print("Updated memory.")


@client.event
async def on_message(message):
    if message.author == client.user:
        update_dialogue_history(message.content.strip())
        return
    persona = # add persona here
    if message.content:
        update_dialogue_history(message.content.strip())
        prompt = f"{persona}<START>{dialogue_history}You: {message.content.strip()}\nBOT: "

        async def generate(prompt=""):
            request_payload = {
                "prompt": prompt,
                "params": {
                    "temperature": 0.65,
                    "rep_pen": 1.08,
                    "rep_pen_slope": 0.9,
                    "rep_pen_range": 1024,
                    "top_p": 0.9,
                    "top_k": 0,
                    "top_a": 0.0,
                    "tfs": 0.9,
                    "typical": 1.0,
                    "max_length": 200,
                    "set_world_info": True,
                    "use_memory": True
                }
            }

            response = requests.post(
                api_endpoint + "/generate/async", 
                headers={"Content-Type": "application/json", "apikey": "#ADD HERE"},
                data=json.dumps(request_payload)
            )

            task_id = json.loads(response.content.decode("utf-8"))['id']
            print(task_id)
            print(response.status_code)
            while True:
                time.sleep(5)
                status_check = requests.get(
                    api_endpoint + f"/generate/check/{task_id}", 
                    headers={"Content-Type": "application/json", "apikey": "#ADD HERE"}
                )
                status_check_json = json.loads(status_check.content.decode("utf-8"))
                print(status_check_json)
                if status_check_json.get('done') == True:
                    get_text = requests.get(
                    api_endpoint + f"/generate/status/{task_id}", 
                    headers={"Content-Type": "application/json", "apikey": "#ADD HERE"}
                    )
                    text_response_json = json.loads(get_text.content.decode("utf-8"))
                    generated_text = text_response_json['generations'][0]['text']
                    responses = []
                    for line in generated_text.split("\n"):
                        if "Evie: " in line:
                            response = line.strip().split(":")[-1].strip()
                            responses.append(response)
                        if responses:
                            async with message.channel.typing():
                                await message.channel.send(responses[0], reference=message)
                            break
                

    await generate(prompt)

client.run(
    ""
)