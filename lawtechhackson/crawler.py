import pickle
import os
from models import LawyerBatchData, Lawyer
from db_manager import init_mongo
from env import DataBaseSettings

import asyncio


async def main():
    setting = DataBaseSettings()

    await init_mongo(setting.mongo_connect_str, "test", [Lawyer])

    ## testing example
    lawyer_folder = "./sample_data/lawyer_info_from_crawler"
    # TODO: change to iterate all Taipei data
    file_name = "law_data_taipei.pickle"
    path = os.path.join(lawyer_folder, file_name)
    with (open(path, "rb")) as f:
        try:
            obj = pickle.load(f)
            lawyerBatch = LawyerBatchData(**obj)
            lawyerData = lawyerBatch.data
            lawyers = lawyerData.lawyers
            for lawyer in lawyers:
                print(lawyer)
                await lawyer.insert()
                ## TODO: remove break later, just test uploading 1st to DB
                break
            # TODO: upload Guild list & guildMap

            print("done")
            # TODO: upload to mongoDB
        except EOFError:
            print("load pickle error")


if __name__ == "__main__":
    asyncio.run(main())
