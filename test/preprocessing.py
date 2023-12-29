from langchain.embeddings import OpenAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    character_list = os.listdir("./data/")
    character_list.remove("dialogue")
    dialogue_dataset = []
    character_index = {
        "rem": ["스바루", "렘"],
        "megumi": ["아키", "메구미"]
    }

    for character in character_list:
        char_path = f"./data/{character}/"
        data_list = os.listdir(char_path)
        for i, data in enumerate(data_list):
            data_path = f"./data/{character}/{data}"
            dialogue = []
            wpf = open(f"./data/dialogue/{character}/player_dialogue/{character}_dialogue_{i + 1}.txt", "w")
            wcf = open(f"./data/dialogue/{character}/character_dialogue/{character}_dialogue_{i + 1}.txt", "w")
            player_data = []
            character_data = []
            with open(data_path, "r") as f:
                dialogue = f.readlines()
                for con in dialogue:
                    ch, dia = con.split(":")[0], con.split(":")[1][2:-2]
                    if ch == character_index[character][0]:
                        player_data.append(dia + "\n")
                    elif ch == character_index[character][1]:
                        character_data.append(dia + "\n")
            wpf.writelines(player_data)
            wcf.writelines(character_data)
            wpf.close()
            wcf.close()
            
        