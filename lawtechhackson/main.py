from constants import Court, Law, c
from env import DatasetSettings
from models import Judgment
import json
from typing import Any
import os

# English dict ref:
# 1. https://www.judicial.gov.tw/tw/dl-58197-208aa7b4b75b4f4f891d27d7a86f6851.html
# 2. https://www.judicial.gov.tw/tw/lp-1501-1.html
# 3. http://www.ls.fju.edu.tw/doc/vocabulary/%E9%99%84%E4%BB%B6%E5%9B%9B%20%20%20%E6%B0%91%E4%BA%8B%E8%A8%B4%E8%A8%9F%E6%B3%95.pdf

def read_file(dataset_folder, court_folder, file_name:str):
    ## e.g. /Users/grimmer/git/LawTechHackson/lawsnote/judgment/臺灣士林地方法院_民事/民事裁定_110,簡聲抗,19_2021-09-29.json
    path = os.path.join(dataset_folder, court_folder, file_name)
    with open(path) as f:
        json_data = json.load(f)
        resp = Judgment(**json_data)
    return resp 

def analysis(judgment: Judgment):
    # TODO: detect it is victory or defeat
    pass 

def load_to_db(restul:Any):
    pass

def main():
    settings = DatasetSettings()
    
    # NOTE: first test file 
    # TODO: load a batch of files
    file_name = "民事裁定_110,簡聲抗,19_2021-09-29.json"
    judgment = read_file(settings.LAWSNOTE_JUDGMENT_PATH, f"{Court.Taiwan_Shilin_District_Court}_{Law.Civil}", file_name)
    result = analysis(judgment)
    load_to_db(result)
    
if __name__ == "__main__":
    main()