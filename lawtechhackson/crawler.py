import pickle
import os
from models import LawyerBatchData, Lawyer
from db_manager import init_mongo
from env import DataBaseSettings

import asyncio

# TODO: no new taipei city?
pickle_list = [
    "law_data_Changhua.pickle",
    "law_data_Chiayi.pickle",
    "law_data_Hsinchu.pickle",
    "law_data_Hualien.pickle",
    "law_data_Kaohsiung.pickle",
    "law_data_Keelung.pickle",
    "law_data_Miaoli.pickle",
    "law_data_Nantou.pickle",
    "law_data_Pingtung.pickle",
    "law_data_Taitung.pickle",
    "law_data_Hualien.pickle",
    "law_data_taipei.pickle",
    "law_data_Keelung.pickle",
    "law_data_Yilan.pickle",
    "law_data_Hsinchu.pickle",
    "law_data_Taoyuan.pickle",
]


async def main():
    setting = DataBaseSettings()

    await init_mongo(setting.mongo_connect_str, "test", [Lawyer])

    print(f"start to load pickle to db")
    lawyer_folder = "./sample_data/lawyer_info_from_crawler"
    for file_name in pickle_list:
        print(f"file_name:{file_name}")
        path = os.path.join(lawyer_folder, file_name)
        with (open(path, "rb")) as f:
            try:
                count = 0
                obj = pickle.load(f)
                lawyerBatch = LawyerBatchData(**obj)
                lawyerData = lawyerBatch.data
                lawyers = lawyerData.lawyers
                for lawyer in lawyers:
                    count += 1
                    await lawyer.insert()
                    print(f"{count}")

                print(f"save a pickle done:{file_name}")
            except EOFError:
                print("load pickle error")
    print(f"end to load pickle to db")


if __name__ == "__main__":
    asyncio.run(main())
