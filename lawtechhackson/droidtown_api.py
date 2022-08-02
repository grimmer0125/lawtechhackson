from requests import post
# from  import

from env import DroidTownSettings


def main():
    setting = DroidTownSettings()

    url = "https://api.droidtown.co/Articut/Toolkit/Laws/"
    payload = {
        # 若您是使用 Docker 版本，無須填入 username, api_key 參數
        "username":
        setting.
        username,  # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
        "api_key":
        setting.
        api_key,  # 這裡填入您在 https://api.droidtown.co 登入後取得的 Api_Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
        "result_pos": [
            "<ENTITY_nouny>被告</ENTITY_nouny><MODIFIER>前</MODIFIER><FUNC_inter>因</FUNC_inter><MODIFIER>非法</MODIFIER><ACTION_verb>持有</ACTION_verb><ENTITY_nouny>槍械</ENTITY_nouny>",
            "，",
            "<CLAUSE_particle>業</CLAUSE_particle><ACTION_verb>經</ACTION_verb><ENTITY_nouny>前案</ENTITY_nouny><ACTION_verb>判決</ACTION_verb><MODIFIER>非法</MODIFIER><ACTION_verb>持有</ACTION_verb><MODAL>可</MODAL><ACTION_verb>發射</ACTION_verb><ENTITY_nouny>子彈</ENTITY_nouny><ENTITY_nouny>具</ENTITY_nouny><ENTITY_nouny>殺傷力</ENTITY_nouny><FUNC_inner>之</FUNC_inner><ENTITY_nouny>槍枝</ENTITY_nouny><ENTITY_nouny>罪</ENTITY_nouny>",
            "，",
            "<ACTION_verb>處</ACTION_verb><MODIFIER>有期</MODIFIER><ENTITY_nounHead>徒刑</ENTITY_nounHead><TIME_year>參年</TIME_year><TIME_month>陸月</TIME_month>",
            "，",
            "<ACTION_verb>併</ACTION_verb><ENTITY_nounHead>科罰金</ENTITY_nounHead><ENTITY_noun>新臺幣</ENTITY_noun><KNOWLEDGE_currency>拾萬元</KNOWLEDGE_currency>",
            "。",
            "<FUNC_inner>於</FUNC_inner><ENTITY_nouny>前案</ENTITY_nouny><ACTION_verb>偵查</ACTION_verb><ENTITY_noun>過程</ENTITY_noun><RANGE_locality>中</RANGE_locality>",
            "，",
            "<ENTITY_nouny>南投縣</ENTITY_nouny><ENTITY_noun>政府</ENTITY_noun><ENTITY_nouny>警察局</ENTITY_nouny><LOCATION>集集</LOCATION><ENTITY_oov>分局</ENTITY_oov><FUNC_inner>之</FUNC_inner><ENTITY_nouny>員警</ENTITY_nouny>",
            "，",
            "<ACTION_verb>持</ACTION_verb><ENTITY_nouny>本院</ENTITY_nouny><ACTION_verb>核發</ACTION_verb><FUNC_inner>之</FUNC_inner><TIME_year>105年度</TIME_year><ENTITY_oov>聲</ENTITY_oov><VerbP>搜字</VerbP><KNOWLEDGE_lawTW>第165號</KNOWLEDGE_lawTW><ACTION_verb>搜索</ACTION_verb><ENTITY_nouny>票</ENTITY_nouny><ACTION_verb>搜索</ACTION_verb>",
            "。"
        ],
        "func": ["get_all"]
    }

    response = post(url, json=payload).json()


if __name__ == "__main__":
    print("start")
    main()
