import pickle
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np
from numpy import dot
from numpy.linalg import norm


def lawyer_query(user_input, model, lawyer_emd):
    query_emd = model.encode(user_input)
    search_emd = lawyer_emd.values()
    cosine = np.dot(search_emd,query_emd)/(norm(search_emd, axis=1)*norm(query_emd))
    lawyer_dict = {}

    return lawyer_dict


model = SentenceTransformer('ckiplab/albert-base-chinese')
with open('./lawyer_emd.pickle', 'rb') as f:
    lawyer_emd = pickle.load(f)

# result = lawyer_query(user_input, model, lawyer_emd)
