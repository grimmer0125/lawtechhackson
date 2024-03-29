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
    "law_data_Taichung.pickle",  # 忘了加
    "law_data_Tainan.pickle",  # 忘了加
    "law_data_taipei.pickle",
    "law_data_Taitung.pickle",
    "law_data_Taoyuan.pickle",
    "law_data_Yilan.pickle",
    "law_data_Yunlin.pickle",  # 忘了加
    "law_data_Hualien.pickle",  # 重複了
    "law_data_Keelung.pickle",  # 重複了
    "law_data_Hsinchu.pickle"  # 重複了
]

lawyer_dict = {}


async def main():
    setting = DataBaseSettings()

    await init_mongo(setting.mongo_connect_str, "test3", [Lawyer])

    print(f"start to load pickle to db")
    lawyer_folder = "./sample_data/lawyer_info_from_crawler"

    for root, directories, files in os.walk(lawyer_folder):
        print("start to read files")
        for file_name in files:
            if "pickle" not in file_name:
                continue

            # for file_name in pickle_list:
            # if file_name != "law_data_Taitung.pickle":
            #     continue
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
                        name = lawyer.name
                        if name not in lawyer_dict:
                            lawyer_dict[name] = lawyer
                        else:
                            s_lawyer = lawyer_dict[name]
                            log = f"find:{name}.s_n:{s_lawyer.now_lic_no}. new:${lawyer.now_lic_no}"
                            print(f"{log}")
                            with open("duplicate_lawyer.txt",
                                      "a") as file_object:
                                # Append 'hello' at the end of file
                                file_object.write(log)
                        await lawyer.insert()
                        print(f"{count}")

                    print(f"save a pickle done:{file_name}")
                except EOFError:
                    print("load pickle error")
    print(f"end to load pickle to db")


if __name__ == "__main__":
    asyncio.run(main())
