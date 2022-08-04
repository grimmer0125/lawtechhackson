from constants import Court, LawType
from env import DatasetSettings, DataBaseSettings
from lawtechhackson.models import Lawyer, JudgmentVictoryLawyerInfo
from models import Judgment, LawIssue
import json
from typing import Any
import os
import asyncio
from db_manager import init_mongo


# English dict ref:
# 1. https://www.judicial.gov.tw/tw/dl-58197-208aa7b4b75b4f4f891d27d7a86f6851.html
# 2. https://www.judicial.gov.tw/tw/lp-1501-1.html
# 3. http://www.ls.fju.edu.tw/doc/vocabulary/%E9%99%84%E4%BB%B6%E5%9B%9B%20%20%20%E6%B0%91%E4%BA%8B%E8%A8%B4%E8%A8%9F%E6%B3%95.pdf

### 有些 todo 是寫在 models.py 裡 ###
async def load_issue_to_db(judgment: Judgment):
    for issue in judgment.relatedIssues:
        lawName = issue.lawName
        if await LawIssue.find_one(LawIssue.name == lawName) == None:
            law_issue = LawIssue(name=lawName)
            # write to DB
            await law_issue.save()


async def count_laywer_stat_info():
    # TODO:
    # 如果律師是 unique 的，裡面就直接 update laywer 欄位, 不是就??
    pass


def find_domain(judgment: Judgment):
    # TODO:
    # NOTE: 刑事犯罪這個類別還滿大的
    return ""


def find_lawyer(judgment: Judgment):
    # TODO:
    for party in judgment.party:
        pass

    return [""]


async def find_victory(judgment: Judgment):
    # TODO: detect it is victory or defeat

    # 民事:
    # - 被告應給付$$$元 (不一定)
    # - m 判決結果 會寫原告之訴駁回 之類
    # 刑事:
    # - 被告處有期徒刑xx(多久）
    # - 被告無罪

    is_defeated = False
    if judgment.sys == LawType.Civil:
        mainText = judgment.mainText
        if "駁回。" in mainText:
            is_defeated = True
    else:
        # TODO: handle LawType.Criminal later
        pass

    lawyers = find_lawyer(judgment)
    domain = find_domain(judgment)
    guild_name = ""  #?

    for laywyer in lawyers:
        lawyerInfo = JudgmentVictoryLawyerInfo(lawyer_name=laywyer,
                                               judgment_no=judgment.no,
                                               judgment_date=judgment.date,
                                               court=judgment.court,
                                               type=judgment.type,
                                               domain=domain,
                                               guild_name=guild_name)
        await lawyerInfo.insert()
        await count_laywer_stat_info()


async def load_file(path: str):
    with open(path) as f:
        json_data = json.load(f)
        judgment = Judgment(**json_data)
        await load_issue_to_db(judgment)
        await find_victory(judgment)


async def read_files(dataset_folder, court: Court, law: LawType):
    court_folder = f"{court}_{law}"
    folder_path = os.path.join(dataset_folder, court_folder)
    file_count = 0
    for root, directories, files in os.walk(folder_path):
        print("start to read files")
        for file_name in files:
            if "json" not in file_name:
                continue
            file_count += 1
            file_path = os.path.join(root, file_name)
            await load_file(file_path)
            print(f"read:{file_count}")
        print("end to read files")


async def read_file(dataset_folder, court: Court, law: LawType,
                    file_name: str):
    ## e.g. /Users/grimmer/git/LawTechHackson/lawsnote/judgment/臺灣士林地方法院_民事/民事裁定_110,簡聲抗,19_2021-09-29.json
    court_folder = f"{court}_{law}"
    path = os.path.join(dataset_folder, court_folder, file_name)
    await load_file(path)


### some usage notes about pydantic ###
# 1. 如果是用 Judgment(**json_data)，它預設會檢查型斜
#   1. 如果某些 fields 跟指定的 type 不一樣，它會把某些 type 自動轉型，像 int -> str. 但如果是塞 []　到 str type,
#      它會 throw error
# 2. 如果是已產生的 Pydantic instance，然後再 assign field，預設不會檢查 type，所以可以塞 [] 到 str type field，
#    1. 但可以 validate_assignment=True 來 enable 檢查型別
###


async def main():
    settings = DatasetSettings()
    db_setting = DataBaseSettings()
    await init_mongo(db_setting.mongo_connect_str, "test", [LawIssue])

    # NOTE: first test file
    # file_name = "民事裁定_110,簡聲抗,19_2021-09-29.json"
    # judgment = read_file("", "sample_data", file_name)
    # read_file(settings.LAWSNOTE_JUDGMENT_PATH,
    #           Court.Taiwan_Shilin_District_Court, LawType.Civil, file_name)

    await read_files(settings.LAWSNOTE_JUDGMENT_PATH,
                     Court.Taiwan_Shilin_District_Court, LawType.Civil)


if __name__ == "__main__":
    print("start")
    asyncio.run(main())
    print("end")
