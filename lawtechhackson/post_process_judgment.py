import asyncio
from lawtechhackson.db_manager import init_mongo
from lawtechhackson.env import DatasetSettings, DataBaseSettings
from lawtechhackson.models import JudgmentVictoryLawyerInfo, Judgment, LawIssue, Lawyer


async def list_LawIssue():
    # until now, 140008 judgments are saved into DB
    async for result in LawIssue.find():
        name = result.name
        with open("LawIssue_list.txt", "a") as file_object:
            file_object.write(f"{name}\n")


async def main():
    db_setting = DataBaseSettings()
    await init_mongo(db_setting.mongo_connect_str, "test3",
                     [JudgmentVictoryLawyerInfo, Judgment, LawIssue, Lawyer])

    await list_LawIssue()


if __name__ == "__main__":
    print("start")
    asyncio.run(main())
    print("end")