import json
from typing import Any
import os
import asyncio
from pydantic import BaseModel
from lawtechhackson.constants import Court, LawType, JudgmentType, PartyGroup
from lawtechhackson.env import DatasetSettings, DataBaseSettings
from lawtechhackson.db_manager import init_mongo
from lawtechhackson.models import JudgmentVictoryLawyerInfo, Judgment, LawIssue, Lawyer


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
            await law_issue.insert()


lawyer_dict = {}


async def update_laywer_stat_info(is_defeated: bool, laywyer_name: str,
                                  judgmentType: str):
    # 如果律師是 unique 的，裡面就直接 update laywer 欄位,
    #  TODO: 同名的還沒想好怎麼辦
    ## NOTE:
    # 如果無法徹底判斷是那個律師(同名 case), 加上有找到兩個律師，到時 ui 就 show 不一定?
    # 不過就算只有一筆那律師的判決，也可能是把 a,b 律師搞混(其中一律師沒有參加過判決)

    lawyer_list = await Lawyer.find(Lawyer.name == laywyer_name).to_list()
    if len(lawyer_list) > 0:
        print("find out laywer")
        if len(lawyer_list) == 1:
            print("update only this lawyer!!")
            lawyer = lawyer_list[0]

            ## reset in case the previous parsing fail and clean some interrupted data
            if laywyer_name not in lawyer_dict:
                lawyer_dict[laywyer_name] = 1
                lawyer.litigate_judgment_total = 0
                lawyer.defeated_judgment_count = 0
                lawyer.litigate_ruling_total = 0
                lawyer.defeated_ruling_count = 0

            if judgmentType == JudgmentType.Judgment:
                lawyer.litigate_judgment_total += 1
                if is_defeated:
                    lawyer.defeated_judgment_count += 1
            else:
                lawyer.litigate_ruling_total += 1
                if is_defeated:
                    lawyer.defeated_ruling_count += 1
            await lawyer.save()
            print("update lawyer ok")

        else:
            print("more than 1 lawyer !!!")


def find_domain(judgment: Judgment):
    # TODO:
    # NOTE: 刑事犯罪這個類別還滿大的
    return ""


# class LawyerGroup(BaseModel, validate_assignment=True):
#     lawyer_name = ""
#     group = ""


def find_lawyers(judgment: Judgment):
    # TODO(test)
    group_lawyer_list = []
    for i, party in enumerate(judgment.party):
        group = party.group
        # title = party.title
        value = party.value
        if PartyGroup.lawyer in group:  # or agentAdLitem
            lawyer_name = value
            if PartyGroup.plaintiff in group and PartyGroup.defendant in group:
                pre_party = judgment.party[i - 1]
                if PartyGroup.plaintiff in pre_party.group:
                    group = PartyGroup.plaintiff
                else:
                    group = PartyGroup.defendant
            elif PartyGroup.plaintiff in group:
                group = PartyGroup.plaintiff
            else:
                group = PartyGroup.defendant
            # law = LawyerGroup(lawyer_name=lawyer_name, group=group)
            group_lawyer_list.append({
                "group": group,
                "lawyer_name": lawyer_name
            })
    return group_lawyer_list


async def parse_judgment(judgment: Judgment):
    # TODO(test): detect it is victory or defeat

    # 民事:
    # - 被告應給付$$$元 (不一定)
    # - m 判決結果 會寫原告之訴駁回 之類
    # 刑事:
    # - 被告處有期徒刑xx(多久）
    # - 被告無罪

    # TODO(test): 整理用 mainText　裡的關鍵字來判斷
    is_defeated = False
    if judgment.sys == LawType.Civil:
        mainText = judgment.mainText
        if "駁回。" in mainText:
            is_defeated = True
    else:
        # TODO: handle LawType.Criminal later
        pass

    group_lawyer_list = find_lawyers(judgment)

    # TODO:　等先一輪 load_issue_to_db 後，再來回來補填這塊
    # domain = find_domain(judgment)

    for group_lawyer in group_lawyer_list:
        laywyer_name = group_lawyer["laywyer_name"]
        group = group_lawyer["group"]
        lawyerVictoryInfo = JudgmentVictoryLawyerInfo(
            lawyer_name=laywyer_name,
            judgment_no=judgment.no,
            judgment_date=judgment.date,
            court=judgment.court,
            type=judgment.type)

        await lawyerVictoryInfo.insert()
        if group == PartyGroup.plaintiff:
            await update_laywer_stat_info(is_defeated, laywyer_name,
                                          judgment.type)
        else:
            await update_laywer_stat_info(not is_defeated, laywyer_name,
                                          judgment.type)


async def load_file(path: str):
    with open(path) as f:
        json_data = json.load(f)
        judgment = Judgment(**json_data)
        await judgment.insert()
        # insert LawIssue
        await load_issue_to_db(judgment)
        # insert JudgmentVictoryLawyerInfo & update laywer
        await parse_judgment(judgment)


async def read_files(dataset_folder, court: Court, law: LawType):
    court_folder = f"{court}_{law}"
    folder_path = os.path.join(dataset_folder, court_folder)
    # total 478954: 台北士林民事
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
    await init_mongo(db_setting.mongo_connect_str, "test3", [LawIssue, Lawyer])

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
