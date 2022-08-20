import pickle
# 第一次執行會需要一點時間下載，之後就會使用 cache 住的
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy.linalg import norm
from sklearn.metrics.pairwise import cosine_similarity
from typing import Any, Optional

import heapq
from ArticutAPI import Articut


class AIService:

    def __init__(self):
        self.model = None
        self.lawyer_emd = None
        self.stopwords = None

    def load_model(self):
        """ 會花幾秒 load 一下"""
        self.model = SentenceTransformer('ckiplab/albert-base-chinese')
        with open('./sample_data/lawyer_emd.pickle', 'rb') as f:
            self.lawyer_emd = pickle.load(f)

    def load_stopwords(self):
        """loading Chinese stopwords """
        stpwrdpath = "./sample_data/chinese"
        with open(stpwrdpath, 'rb') as fp:
            stopword_ = fp.read().decode('utf-8')  # readin stopwords
        self.stopwords = stopword_.splitlines()  # stopwords list

    def get_similiar_lawyers(self,
                             cosine_sim: np.ndarray,
                             input_lawyer: int = 3) -> list[int]:
        # Get the similarity scores
        sim_scores = list(enumerate(cosine_sim))

        # Sort the layers based on the similarity scores
        #sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the top-k most similar articles
        #sim_scores = sim_scores[0:input_lawyer]

        # using heapq to find max-k values
        sim_scores = heapq.nlargest(input_lawyer,
                                    sim_scores,
                                    key=lambda x: x[1])

        # Get the lawyer indices
        lawyer_indices = [i[0] for i in sim_scores]
        scores = [i[1] for i in sim_scores]

        # Return the top-k most similar article ID
        return lawyer_indices, scores

    def lawyer_query(self, user_input: list[str]) -> list[str]:
        query_emd = self.model.encode(user_input)
        search_emd = np.array(list(self.lawyer_emd.values()))
        cosine_sim = cosine_similarity(
            search_emd,
            query_emd)  # using cosine_sim in scikit learn for quick access
        lawyer_indices, scores = self.get_similiar_lawyers(cosine_sim, 3)
        lawyer = list(self.lawyer_emd.keys())

        found_lawyer_list = [lawyer[index] for index in lawyer_indices]
        return found_lawyer_list

    def predict(self, query_str: str) -> list[str]:
        username = "nchureborn@gmail.com"  #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
        apikey = "U9klFNFijvCMGxEjSy&m4I#bQ!o#aJ$"  #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
        articut = Articut(username, apikey)
        resultDICT = articut.parse(query_str)
        query_str_list = resultDICT['result_segmentation'].split('/')
        if self.stopwords == None:
            self.load_stopwords()
        query_str_list = [
            word for word in query_str_list if not word in self.stopwords
        ]
        result = self.lawyer_query(query_str_list)

        return result


def main():
    ai_service = AIService()
    ai_service.load_model()
    result = ai_service.predict(["股票"])
    print(result)


if __name__ == '__main__':
    main()
