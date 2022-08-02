from pydantic import BaseModel, BaseSettings, Field, validator, root_validator
from typing import Optional, Tuple, Literal
from beanie import Document, Indexed, init_beanie


class RelatedIssue(BaseModel, validate_assignment=True):
    lawName: str
    issueRef: str


class Attachment(BaseModel, validate_assignment=True):
    fileName: str
    fileUrl: str


class Party(BaseModel):
    group: list[str]
    title: str
    value: str


class Judgment(BaseModel, validate_assignment=True):
    """ use lawsnote as reference first """
    court: str
    date: str
    no: str
    sys: str
    reason: str
    judgement: str
    type: str  # 判決或裁定
    historyHash: str
    mainText: str
    opinion: str
    relatedIssues: list[RelatedIssue]
    attachAsJudgement: Optional[str]  # url
    attachments: Optional[list[Attachment]]
    party: Optional[list[Party]]


class Lawyer(Document, validate_assignment=True):
    name: Indexed(str) = None
    now_lic_no: Indexed(str) = None
    court: list[str]
    guild_name: list[str]
    office: Indexed(str) = None


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
