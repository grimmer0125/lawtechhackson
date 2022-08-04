from pydantic import BaseModel, BaseSettings, Field, validator, root_validator
from typing import Optional, Tuple, Literal
from beanie import Document, Indexed, init_beanie


class RelatedIssue(BaseModel, validate_assignment=True):
    lawName: str
    issueRef: str


class Attachment(BaseModel, validate_assignment=True):
    fileName: str
    fileUrl: str


# {
#      "group": [
#          "plaintiff",
#          "agentAdLitem",
#          "lawyer"
#      ],
#      "title": "訴訟代理人",
#      "value": "陳和貴律師"
#  },

# {
#     "group": [
#         "plaintiff",
#         "agentAdLitem",
#         "lawyer"
#     ],
#     "title": "前列二人共同訴訟代理人",
#     "value": "李聖隆律師"
# },

# {
#     "group": [
#         "defendant",
#         "agentAdLitem",
#         "lawyer"
#     ],
#     "title": "訴訟代理人",
#     "value": "王敬堯律師"
# },

# {
#     "group": [
#         "defendant",
#         "agentAdLitem",
#         "lawyer"
#     ],
#     "title": "複代理人",
#     "value": "劉雅雲律師"
# },


class Party(BaseModel):
    # [plaintiff 原告, agentAdLitem 訴訟代理人, defendant, 被告, lawyer 律師]
    group: list[str]
    # 相對人/抗告人/訴訟代理人/上訴人/被上訴人
    title: str
    value: str


## TODO:
# 律師的勝率需要時再另外定時計算。算完存在 Lawyer
# 如果無法徹底判斷是那個律師(同名 case), 加上有找到兩個律師，到時 ui 就 show 不一定?
# 不過就算只有一筆那律師的判決，也可能是把 a,b 律師搞混(其中一律師沒有參加過判決)

## TODO: (nice to have) 存律師資料 Lawyer 到 DB 時就去找說到底有沒有同名的律師


class LawIssue(Document, validate_assignment=True):
    """ a helper class: 幫助我們知道 dataset 裡到底有那些法條 """
    name: str = ""


## 此為整理的資料
# 律師1w/事務所+判決w/date(或許加上公會地區)+判斷種類
# 律師2w/事務所+判決w/date(或許加上公會地區+判斷種類
class JudgmentVictoryLawyerInfo(Document, validate_assignment=True):
    # TODO: 整理用 mainText　裡的關鍵字來判斷
    is_defeated: bool = False
    # guild_name: Optional[str]  # 公會
    judgment_no: str
    judgment_date: str
    court: str
    # TODO:　整理那些法條對應到那個 domain
    domain: str = ""  # 刑事專長等等
    lawyer_name: str
    type: str


## 原始資料
# court (某種區域資訊)
# TODO: date: 要轉換?
# no+date才是唯一性?: 可以用 compound. 檔名就是(還有加上是否民事判定等)
# TODO: 律師: 從 party 裡找,
# 事務所資訊? ps. # 律師+事務所才是律師唯一性? 地區(公會名字)可以參考
# 引用法
####
class Judgment(Document, validate_assignment=True):
    """ use lawsnote as reference first """
    court: str
    date: str
    no: str
    sys: str
    reason: str
    # long
    # judgement: str
    # ref: https://www.legis-pedia.com/article/lawABC/749
    type: str = ""  # 判決或裁定
    historyHash: Optional[str]
    mainText: Optional[str]
    # long, is included in judgement
    # opinion: Optional[str]
    relatedIssues: list[RelatedIssue]  # reason: 支付命令. 的話可能這裡會是空的
    attachAsJudgement: Optional[str]  # url
    attachments: Optional[list[Attachment]]
    party: list[Party]


class Lawyer(Document, validate_assignment=True):
    name: Indexed(str) = None
    now_lic_no: Indexed(str) = None
    court: list[str]
    # 公會名字
    guild_name: list[str]
    office: Indexed(str) = None
    ## stat info fields from JudgmentVictoryLawyerInfo
    # victory_count: int = 0
    litigate_count: int = 0  # total
    defeated_count: int = 0


class Guild(BaseModel, validate_assignment=True):
    name: str
    no: str


class LawyerData(BaseModel, validate_assignment=True):
    lawyers: list[Lawyer]
    # courtMap: [] # always a empty list
    guildMap: list[list[str]]  # e.g. [['台北律師公會', 7195]]

    @validator("guildMap")
    def set_guild(cls, v):
        guilds = []
        for guild_raw in v:
            name = guild_raw[0]
            no = guild_raw[1]
            guild = Guild(name=name, no=no)
            guilds.append(guild)
        return guilds


class LawyerBatchData(BaseModel, validate_assignment=True):
    data: LawyerData
