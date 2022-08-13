from ctypes import Union
import json
from operator import truediv
from typing import Any, Union, Optional
import os
import asyncio
import pathlib
from pydantic import BaseModel
from lawtechhackson.constants import Court, LawType, JudgmentType, PartyGroup
from lawtechhackson.env import DatasetSettings, DataBaseSettings
from lawtechhackson.db_manager import init_mongo
from lawtechhackson.db_models import JudgmentVictoryLawyerInfo, Judgment, LawIssue, Lawyer, LawyerStat


# English dict ref:
# 1. https://www.judicial.gov.tw/tw/dl-58197-208aa7b4b75b4f4f891d27d7a86f6851.html
# 2. https://www.judicial.gov.tw/tw/lp-1501-1.html
# 3. http://www.ls.fju.edu.tw/doc/vocabulary/%E9%99%84%E4%BB%B6%E5%9B%9B%20%20%20%E6%B0%91%E4%BA%8B%E8%A8%B4%E8%A8%9F%E6%B3%95.pdf
async def load_issue_to_db(judgment: Judgment):
    # NOTE: can use set to reduce duplicate query
    for issue in judgment.relatedIssues:
        lawName = issue.lawName
        if await LawIssue.find_one(LawIssue.name == lawName) == None:
            law_issue = LawIssue(name=lawName)
            # write to DB
            await law_issue.insert()


lawyer_dict = {}
lawyer_stat_dict = {}


async def update_laywer_stat_info(is_defeated: bool, laywyer_name: str,
                                  judgmentType: str):
    # 如果律師是 unique 的，裡面就直接 update laywer 欄位,
    #  TODO: 同名的還沒想好怎麼辦
    ## NOTE:
    # 如果無法徹底判斷是那個律師(同名 case), 加上有找到兩個律師，到時 ui 就 show 不一定?
    # 不過就算只有一筆那律師的判決，也可能是把 a,b 律師搞混(其中一律師沒有參加過判決)

    lawyer_list = await Lawyer.find(Lawyer.name == laywyer_name).to_list()
    if len(lawyer_list) > 0:
        # print("find out laywer")
        if len(lawyer_list) == 1:
            # print("update only this lawyer!!")
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
            # print("update lawyer ok")

        else:
            print("more than 1 lawyer !!!")


def find_domain(judgment: Judgment):
    # TODO:
    # NOTE: 刑事犯罪這個類別還滿大的
    return ""


# class LawyerGroup(BaseModel, validate_assignment=True):
#     lawyer = ""
#     group = ""

from enum import auto

from strenum import StrEnum


class Key(StrEnum):
    group = auto()
    lawyer_name = auto()


def find_lawyers(judgment: Judgment):
    group_lawyer_list = []
    # # or title.startswith("債務人"),
    # 有看到 lawyer 裡沒有 plaintiff/defendant, 然後一開始的人 title 是債務人+沒有明顯被告 (但為了怕有債權人也是這種 case, 或是有債權人原告的 case,
    # 只好設定成預設值)
    current_group = PartyGroup.plaintiff
    for i, party in enumerate(judgment.party):
        group = party.group
        title = party.title
        value = party.value
        # case0:  原告+被告
        # case1:  反訴原告"+"反訴被告"
        # case2   反反訴: 原告即反訴被告+被告即反訴原告 https://www.facebook.com/437195293064003/posts/2134684499981732/
        # case4:  反反反: 上訴人即被告即反訴原告 (之前這 case 會找不到, 所以 special_case 會是 "" 所以會當成被告鎮營 --> 就算了)
        #      or 上訴人即附帶被上訴人 即反訴被告 https://law.judicial.gov.tw/FJUD/data.aspx?ty=JD&id=TPHV%2c106%2c%e4%b8%8a%e6%98%93%2c622%2c20190130%2c1&ot=in

        # 聲請人/抗告人 vs 相對人(group會是空的) <-還沒見過反訴的 case, 不過先列好了. 抗告人跟聲請人的定義?
        #
        if title.startswith("原告") or title.startswith(
                "反訴原告") or title.startswith("上訴人") or title.startswith(
                    "聲請人") or title.startswith(
                        "抗告人"):  # title.startswith("原告即反訴被告") or
            current_group = PartyGroup.plaintiff
        elif title.startswith("被告") or title.startswith(
                "反訴被告") or title.startswith("被上訴人") or title.startswith(
                    "相對人"):  # or title.startswith("被告即反訴原告")
            current_group = PartyGroup.defendant

        if PartyGroup.lawyer in group:  # or agentAdLitem
            lawyer_name = value
            if (PartyGroup.plaintiff in group and PartyGroup.defendant in group
                ) or (
                    PartyGroup.plaintiff not in
                    group  # 有見過 group 全空 case 但還沒見過有律師但是是空的 case. 聲請人/抗告人之反訴?
                    and PartyGroup.defendant not in group):
                group = current_group
                # print(f"反訴case:{judgment.file_uri}")
            elif PartyGroup.plaintiff in group:
                group = PartyGroup.plaintiff
            elif PartyGroup.defendant in group:
                group = PartyGroup.defendant

            # lawGroup = LawyerGroup(lawyer=lawyer_name, group=group)
            group_lawyer_list.append({
                Key.group: group,
                Key.lawyer_name: lawyer_name
            })
    return group_lawyer_list


async def fill_lawyer_stat(is_defeated: bool, laywyer_name: str,
                           judgment: Judgment):

    stat: Optional[LawyerStat] = None
    if laywyer_name in lawyer_stat_dict:
        stat = lawyer_stat_dict[laywyer_name]
    else:
        lawyer_list = await Lawyer.find(Lawyer.name == laywyer_name).to_list()
        if len(lawyer_list) == 0:
            # FIX: but it happened. no this in crawler data?
            print("should not be possible to find 0 lawyers")
        elif len(lawyer_list) == 1:
            lawyer = lawyer_list[0]
            stat = LawyerStat(name=laywyer_name, now_lic_no=lawyer.now_lic_no)
            lawyer_stat_dict[laywyer_name] = stat
        else:
            # TODO: 要統計多少比率的判決是同名的嗎? 存在 JudgmentVictoryLawyerInfo 裡. 先算了，因為以後可能同名的人才會出來
            print("more than 1 lawyer, skip !!!")
    if stat is None:
        return

    ## relatedIssues part
    # if len(stat.law_issues) > 0:
    #     print("bingo0")
    issue_set = set(stat.law_issues)
    for issue in judgment.relatedIssues:
        law_name = issue.lawName
        issue_set.add(law_name)
    issue_list = list(issue_set)
    stat.law_issues = issue_list

    stat.total_litigates += 1
    # if stat.total_litigates == 2:
    #     print("bingo")
    if judgment.type == JudgmentType.Judgment:
        stat.judgment_count += 1
        if is_defeated:
            stat.defeated_judgment_count += 1
            stat.total_defeated_litigates += 1

        stat.win_rate_judgment = (
            stat.judgment_count -
            stat.defeated_judgment_count) / stat.judgment_count

    else:
        stat.ruling_count += 1
        if is_defeated:
            stat.defeated_ruling_count += 1
            stat.total_defeated_litigates += 1

        stat.win_rate_ruling = (stat.ruling_count -
                                stat.defeated_ruling_count) / stat.ruling_count

    stat.win_rate = (stat.total_litigates -
                     stat.total_defeated_litigates) / stat.total_litigates

    # await stat.save()


find = False


async def parse_judgment(judgment: Judgment):
    # 民事:
    # - 被告應給付$$$元 (不一定)
    # - m 判決結果 會寫原告之訴駁回 之類
    # 刑事:
    # - 被告處有期徒刑xx(多久）
    # - 被告無罪

    # NOTE: 整理用 mainText　裡的關鍵字來判斷
    is_defeated = False
    if judgment.sys == LawType.Civil:
        mainText = judgment.mainText
        # NOTE: 特別 case, 部份勝訴?: 原告其餘之訴駁回。\n訴訟費用新臺幣壹仟元，由被告連帶負擔百分之
        # 四十三即新臺幣肆伯參拾元，餘由原告負擔。\n本判決原告勝訴部分，
        # partial defeated/victory 當做沒有輸好了:
        if "駁回。" in mainText and "勝訴" not in mainText:  # 之前這 case 當成 defeated 的就算了
            is_defeated = True
    else:
        # TODO: handle LawType.Criminal later
        pass

    group_lawyer_list = find_lawyers(judgment)

    # TODO(pass):　等先一輪 load_issue_to_db 後，再來回來補填這塊
    # domain = find_domain(judgment)

    lawyer_set = set()
    for group_lawyer in group_lawyer_list:
        laywyer_name = group_lawyer[Key.lawyer_name]
        shortname = laywyer_name.replace("律師", "")
        if shortname not in lawyer_set:
            lawyer_set.add(shortname)
        else:
            continue
        group = group_lawyer[Key.group]

        if group == PartyGroup.plaintiff:
            laywyer_is_defeated = is_defeated
        else:
            laywyer_is_defeated = not is_defeated

        # NOTE: 方便查某律師跟判決的關係, 所以如果有lawyer_stat(目前同名就 ignore) 的話就可以再繼續查
        # JudgmentVictoryLawyerInfo
        # if saveJudgmentVictoryLawyerInfo:
        #     ## only enable for first time iterate whole dataset
        #     lawyerVictoryInfo = JudgmentVictoryLawyerInfo(
        #         file_uri=judgment.file_uri,  # 現存的資料存時沒有這行
        #         is_defeated=is_defeated,
        #         lawyer_name=shortname,
        #         judgment_no=judgment.no,
        #         judgment_date=judgment.date,
        #         court=judgment.court,
        #         type=judgment.type)
        #     await lawyerVictoryInfo.insert()
        # else:
        if False:
            lawyerVictoryInfos = await JudgmentVictoryLawyerInfo.find(
                JudgmentVictoryLawyerInfo.court == judgment.court,
                JudgmentVictoryLawyerInfo.judgment_no == judgment.no,
                JudgmentVictoryLawyerInfo.judgment_date == judgment.date,
                # 應該不太可能不同type同一天出來吧? type 應該不太需要
                JudgmentVictoryLawyerInfo.type == judgment.type,
                JudgmentVictoryLawyerInfo.lawyer_name == shortname).to_list()
            if len(lawyerVictoryInfos) == 0:
                ## TODO: create a one
                lawyerVictoryInfo = JudgmentVictoryLawyerInfo(
                    file_uri=judgment.file_uri,  # 現存的資料存時沒有這行
                    lawyer_name=shortname,
                    judgment_no=judgment.no,
                    judgment_date=judgment.date,
                    court=judgment.court,
                    type=judgment.type,
                    is_defeated=laywyer_is_defeated,  # 現存的資料存時沒有這行
                    sys=judgment.sys)  # 現存的資料存時沒有這行
                await lawyerVictoryInfo.insert()  #
            else:
                if len(lawyerVictoryInfos) > 1:
                    print("more than one lawyerVictoryInfo")
                lawyerVictoryInfo = lawyerVictoryInfos[0]
                lawyerVictoryInfo.sys = judgment.sys
                lawyerVictoryInfo.file_uri = judgment.file_uri
                lawyerVictoryInfo.is_defeated = laywyer_is_defeated
                await lawyerVictoryInfo.save()

        await fill_lawyer_stat(laywyer_is_defeated, shortname, judgment)
        # await update_laywer_stat_info(is_defeated, shortname,
        #                               judgment.type)


async def load_file(path: str):
    with open(path) as f:
        json_data = json.load(f)
        judgment = Judgment(**json_data)
        judgment.file_uri = pathlib.Path(path).stem

        ## insert judgments
        # await judgment.insert()

        ## insert LawIssue for analyzing
        # await load_issue_to_db(judgment)

        # insert JudgmentVictoryLawyerInfo & update lawyerStat

    global find
    if find is False and judgment.file_uri == "民事判決_100,士訴,2_2011-09-07":
        find = True

    await parse_judgment(judgment)


async def save_stat_dict():
    print("start save_stat_dict")
    for stat in lawyer_stat_dict.values():
        o_stat = await LawyerStat.find_one(
            LawyerStat.name == stat.name,
            LawyerStat.now_lic_no == stat.now_lic_no)
        if o_stat is not None:
            stat.id = o_stat.id
        await stat.save()
    print("end save_stat_dict")


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
            if file_count % 100 == 0:
                print(f"read:{file_count}")
        print("end to read files")

    await save_stat_dict()


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
    await init_mongo(
        db_setting.mongo_connect_str, "test3",
        [JudgmentVictoryLawyerInfo, Judgment, LawIssue, Lawyer, LawyerStat])

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
