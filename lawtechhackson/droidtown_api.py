from requests import post

from env import DroidTownSettings

# 法學院查詢系統
# https://law.judicial.gov.tw/FJUD/data.aspx?ty=JD&id=SLDV%2c110%2c%e7%b0%a1%e8%81%b2%e6%8a%97%2c19%2c20210929%2c1
# 感覺是
# 1. 簡易庭(可對簡易廷抗告，會成為第二筆同一字號簡易庭)
# 2. -> 地方法院 (對其抗告就是到高等法院)
# 3. -> 高等法院 -> 最高法院
# 更x審，就是退回到下級再審
# p.s. 法院網站現在除了內文，右邊也會有智慧小幫手列出內文用到的法條 (跟 lawsnote 差不多)
#    ，也會有歷審裁判 (判決書會提到前一審編號，現在是初審右邊幫手會列出後幾審的編號)
# e.g.
# repo 裡存的 lawsnote/droidtown example (2021, 簡聲抗, 19, 士林)　對應到的法院頁面: https://bit.ly/3vyOcdC
# 下面 https://github.com/Droidtown/LawsDocAssistant_tw 對應到的　https://bit.ly/3SmVmLK

# lawsnote 的資料介紹
# https://docs.google.com/document/d/1DJ2jfxb-1eh3pIdiAvCNkUHbp80gYNmqT0sojRJxdwE/edit#
# 它的 relatedIssues
# 1. 判決主文內找出來的

# Droidtown
# https://api.droidtown.co/document/#Addons_3 laws api
# https://github.com/Droidtown/LawsDocAssistant_tw laws api 使用 example
# 1. 要先將內文送至 https://api.droidtown.co/Articut/API/ 進行斷詞
# 2. 將斷詞結果送至 https://api.droidtown.co/Articut/Toolkit/Laws/ 取得法律相關條文
# 3. 會從主文(內文) 找出
#    法條索引 (好像法院的比較準), 刑責，事件參照(目前網頁上的例子都是空的)
### droidtown ai 部份:
# https://github.com/Droidtown/LeA/
###　它的資料集就是給斷詞後的結果
# relatedIssues法條, party 等都跟 lawsnote 一樣 (可能是統一制定).
#   但 lawsnote judgement/opionion 是給原始全文,
#   但它 judgement/opionion 是給斷詞後的結果 -> 所以檔案從 14K 變成 416KB


def main():
    setting = DroidTownSettings()

    url = "https://api.droidtown.co/Articut/Toolkit/Laws/"
    payload = {
        # 若您是使用 Docker 版本，無須填入 username, api_key 參數
        "username":
        setting.
        droid_username,  # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
        "api_key":
        setting.
        droid_api_key,  # 這裡填入您在 https://api.droidtown.co 登入後取得的 Api_Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
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
