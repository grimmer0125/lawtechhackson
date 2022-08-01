import pickle
import os 
from models import LawyerBatchData

def main():
    ## testing example
    # TODO: change to iterate all Taipei data
    lawyer_folder = "./sample_data/lawyer_info_from_crawler"
    file_name = "law_data_taipei.pickle"
    path = os.path.join(lawyer_folder, file_name)
    with (open(path, "rb")) as f:
        try:
            obj = pickle.load(f)
            lawyerBatch = LawyerBatchData(**obj)
            print("done")
            # TODO: upload to mongoDB
        except EOFError:
            print("load pickle error")

if __name__ == "__main__":
    main()

