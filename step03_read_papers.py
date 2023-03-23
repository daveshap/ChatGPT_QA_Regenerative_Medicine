import re
import os
import json
import openai
from time import time, sleep



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return json.load(infile)


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=2)


def chatgpt_completion(messages, temp=0, model="gpt-4"):
    max_retry = 7
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=messages, temperature=temp)
            text = response['choices'][0]['message']['content']
            filename = 'chat_%s_mordin.txt' % time()
            if not os.path.exists('chat_logs'):
                os.makedirs('chat_logs')
            save_file('chat_logs/%s' % filename, text)
            return text
        except Exception as oops:
            if 'maximum context length' in str(oops):
                a = messages.pop(1)
                continue
            retry += 1
            if retry >= max_retry:
                print(f"Exiting due to an error in ChatGPT: {oops}")
                exit(1)
            print(f'Error communicating with OpenAI: {oops}. Retrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)


if __name__ == '__main__':
    openai.api_key = open_file('key_openai.txt')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('default_system_mordin.txt')})
    # iterate through all JSON files under the papers_json folder
    for filename in os.listdir('papers_json'):
        if filename.endswith('.json'):
            filepath = os.path.join('papers_json', filename)
            data = load_json(filepath)

            # iterate through all pages in the JSON data
            for page in data['pages']:
                # append the page content to the conversation with role: user
                conversation.append({'role': 'user', 'content': page['text']})

                # get the response from ChatGPT
                response = chatgpt_completion(conversation)
                print('\n\n', response)

                # append the response to the conversation with role: assistant
                conversation.append({'role': 'assistant', 'content': response})

                # add the response to the notes field of the page object
                page['notes'] = response

            # save the updated JSON data
            save_json(filepath, data)