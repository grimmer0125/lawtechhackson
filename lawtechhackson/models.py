from pydantic import BaseModel, BaseSettings, Field, validator, root_validator
from typing import Optional, Tuple, Literal
from beanie import Document, Indexed, init_beanie
from datetime import datetime


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


class LawIssue(Document, validate_assignment=True):
    """ a helper class: 幫助我們知道 dataset 裡到底有那些法條 """
    name: str = ""


## 此為整理的資料
# 律師1w/事務所+判決w/date(或許加上公會地區)+判斷種類
# 律師2w/事務所+判決w/date(或許加上公會地區+判斷種類
class JudgmentVictoryLawyerInfo(Document, validate_assignment=True):
    is_defeated: bool = False
    # guild_name: Optional[str]  # 公會
    judgment_no: str
    judgment_date: datetime  # = Field(format="date-time")
    court: str
    domain: str = ""  # 刑事專長等等
    lawyer_name: str
    type: str


## 原始資料
# court (某種區域資訊)
# no+date才是唯一性?: 可以用 compound. 檔名就是(還有加上是否民事判定等)
# x 事務所資訊? ps. # 律師+事務所才是律師唯一性? 地區(公會名字)可以參考
# 引用法
####
class Judgment(Document, validate_assignment=True):
    """ use lawsnote as reference first """
    file_uri: str = ""
    court: str
    date: datetime  #str = Field(format="date-time")
    no: str
    sys: str
    reason: str
    # long
    # judgement: str
    # ref: https://www.legis-pedia.com/article/lawABC/749
    type: str = ""  # 判決或裁定
    historyHash: str = ""
    mainText: str = ""
    # long, is included in judgement
    # opinion: Optional[str]
    relatedIssues: list[RelatedIssue]  # reason: 支付命令. 的話可能這裡會是空的
    attachAsJudgement: str = ""  # url
    attachments: list[Attachment] = []
    party: list[Party]

    @validator("date", pre=True)
    def set_date(cls, v):
        return datetime.fromisoformat(v)


class Lawyer(Document, validate_assignment=True):
    name: Indexed(str) = None
    now_lic_no: Indexed(str) = None
    court: list[str]
    # 公會名字
    guild_name: list[str]
    office: Indexed(str) = None
    ## stat info fields from JudgmentVictoryLawyerInfo
    # victory_count: int = 0
    litigate_judgment_total: int = 0  # total
    defeated_judgment_count: int = 0
    litigate_ruling_total: int = 0  # total
    defeated_ruling_count: int = 0


class Guild(BaseModel, validate_assignment=True):
    name: str
    no: str


class LawyerData(BaseModel, validate_assignment=True):
    lawyers: list[Lawyer]
    # courtMap: [] # always a empty list
    guildMap: list[list[str]] = Field(format=Guild)  # e.g. [['台北律師公會', 7195]]

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
