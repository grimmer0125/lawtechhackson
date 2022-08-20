from typing import Any
from lawtechhackson.db_manager import init_mongo
from lawtechhackson.env import DataBaseSettings
from lawtechhackson.db_models import JudgmentVictoryLawyerInfo, Judgment, Lawyer, LawyerStat
from beanie.operators import In
from typing import Any
from pydantic import BaseModel


class LawyerProfile(BaseModel):
    name: str
    now_lic_no: str
    guilds: list[str] = []
    office: str
    total_litigates: int = 0
    win_rate: float = 0
    law_issues: list[str] = []


class LawyerService:

    def __init__(self):
        print("LawyerService init")

    async def init_mongo_with_collections(self):
        db_setting = DataBaseSettings()
        await init_mongo(
            db_setting.mongo_connect_str, "test3",
            [JudgmentVictoryLawyerInfo, Judgment, Lawyer, LawyerStat])

    def filter_duplicate(self, lawyer_found_list: list[Any]):
        non_duplicate_list = []
        lawyer_dict = dict()
        lawyer_count_dict = dict()
        for lawyer_found in lawyer_found_list:
            name = lawyer_found.name
            lawyer_dict[name] = lawyer_found
            if name not in lawyer_count_dict:
                lawyer_count_dict[name] = 1
            else:
                lawyer_count_dict[name] += 1
        for name, count in lawyer_count_dict.items():
            if count == 1:
                lawyer = lawyer_dict[name]
                non_duplicate_list.append(lawyer)
        return non_duplicate_list

    async def get_lawyers_data_in_db(self, lawyer_name_list: list[str]):
        lawyer_short_name_list = list(
            map(lambda x: x.replace("律師", ""), lawyer_name_list))
        lawyer_found_list = await Lawyer.find(
            In(Lawyer.name, lawyer_short_name_list)).to_list()
        lawyer_unique_list: list[
            Lawyer] = self.filter_duplicate(  # 所以這兩人都沒有同名的律師
                lawyer_found_list)
        return lawyer_unique_list

    async def get_lawyers_profile(self, lawyer_name_list: list[str]):

        # lawyer_short_name_list = list(
        #     map(lambda x: x.replace("律師", ""), lawyer_name_list))
        # lawyer_found_list = await Lawyer.find(
        #     In(Lawyer.name, lawyer_short_name_list)).to_list()

        lawyer_unique_list = await self.get_lawyers_data_in_db(lawyer_name_list
                                                               )
        # lawyer_unique_list: list[
        #     Lawyer] = self.filter_duplicate(  # 所以這兩人都沒有同名的律師
        #         lawyer_found_list)

        lawyer_name_unique_list = list(
            map(lambda x: x.name, lawyer_unique_list))
        # 感覺這邊應該也不用丟 lawyer_name_unique_list, 因為同名的本來就不會在 LawyerStat 裡。
        # TODOx (是因為 ai 那邊除了士林多了台北地院，但 DB 只有士林 ): 為何 張宇維律師 找不到 LawyerStat，但 ai model 有 output 這位??? 可以用 JudgmentVictoryLawyerInfo 檢查
        # 張宇維律師 (<- not found in stat, 可能是因為重複, 但 Lawyer 沒有找到同名的阿?), 黃鉦哲律師
        lawyer_state_list = await LawyerStat.find(
            In(Lawyer.name, lawyer_name_unique_list)).to_list()
        lawyer_state_dict: dict[str, LawyerStat] = dict()
        for lawyer_stat in lawyer_state_list:
            if lawyer_stat.name in lawyer_state_dict:
                # TODO: 可能找到同一律師但重複的 LawyerStat，因為之前 parse 時跑了幾次 (可能部份是跑一半)，每一次都存一個
                if lawyer_stat.total_litigates > lawyer_state_dict[
                        lawyer_stat.name].total_litigates:
                    lawyer_state_dict[lawyer_stat.name] = lawyer_stat
            else:
                lawyer_state_dict[lawyer_stat.name] = lawyer_stat

        profile_list: list[LawyerProfile] = []
        for i, lawyer in enumerate(lawyer_unique_list):
            name = lawyer.name
            now_lic_no = lawyer.now_lic_no
            guilds = lawyer.guild_name
            office = lawyer.office
            total_litigates = 0
            win_rate = 0
            # 案件類型
            law_issues: list[str] = []
            # TODO: 地區? a. 公會, b. 曾經經手的訴頌的法院名稱 <-但這撈時沒有去統計

            stat = lawyer_state_dict.get(name)
            if stat is not None:
                total_litigates = stat.total_litigates
                if stat.win_rate:
                    win_rate = stat.win_rate
                law_issues = stat.law_issues
            profile = LawyerProfile(name=name,
                                    now_lic_no=now_lic_no,
                                    guilds=guilds,
                                    office=office,
                                    total_litigates=total_litigates,
                                    win_rate=win_rate,
                                    law_issues=law_issues)
            profile_list.append(profile)

        return profile_list

    async def get_lawyer_detail_profile(self, lawyer_name: str):
        shortname = lawyer_name.replace("律師", "")
        judgmentVictory_list = await JudgmentVictoryLawyerInfo.find(
            JudgmentVictoryLawyerInfo.lawyer_name == shortname).to_list()

        query_limit = 10
        judgment_list: list[Judgment] = []
        # TODO(n+1 query): mongoDB 的 In 有可能兩種 query嗎?
        for i, judgmentVictory in enumerate(judgmentVictory_list):
            if i >= query_limit:
                print("this laywer has more than 10 judgments")
                break

            # NOTE: 應該只可能找到一筆，多筆的 check 先 skip
            judgment = await Judgment.find_one(
                Judgment.court == judgmentVictory.court,
                Judgment.file_uri == judgmentVictory.file_uri)
            if judgment is not None:
                judgment_list.append(judgment)
        return judgment_list