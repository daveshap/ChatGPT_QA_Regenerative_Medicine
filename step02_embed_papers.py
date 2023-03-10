import os
import openai
import json
from time import time,sleep


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=2)


def gpt3_embedding(content, engine='text-embedding-ada-002'):
    #try:
        print('CONTENT TO EMBED:', content)
        content = content.encode(encoding='ASCII',errors='ignore').decode()  # fix any UNICODE errors
        response = openai.Embedding.create(input=content,engine=engine)
        vector = response['data'][0]['embedding']  # this is a normal list
        print('VECTOR:', vector)
        return vector
    #except:
    #    return None


def process_text_files(dir_path, out_path):
    # Create the output directory if it doesn't exist
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    # Loop through all files in the directory
    for filename in os.listdir(dir_path):
        if filename.endswith(".txt"):
            # Read in the text file
            with open(dir_path + filename, "r", encoding="utf-8") as f:
                text = f.read()

            # Split the text into pages
            pages = text.split("NEW PAGE")

            # Generate embeddings for each page
            embeddings = [gpt3_embedding(page) for page in pages]

            # Create a dictionary with the filename and the pages and embeddings
            output_dict = {"original_filename": filename,
                           "pages": [{"page_number": i+1,
                                      "text": page,
                                      "embedding": embedding} for i, (page, embedding) in enumerate(zip(pages, embeddings))]}

            # Save the dictionary to a JSON file
            #with open(os.path.join(out_path, filename.replace(".txt", ".json")), "w") as f:
            #    json.dump(output_dict, f)
            save_json(os.path.join(out_path, filename.replace(".txt", ".json")), output_dict)


if __name__ == "__main__":
    openai.api_key = open_file('key_openai.txt')
    # Define the directories where the text files and output JSON files are located
    dir_path = "papers_txt/"
    out_path = "papers_json/"

    # Process the text files
    process_text_files(dir_path, out_path)
