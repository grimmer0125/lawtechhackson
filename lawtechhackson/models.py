from pydantic import BaseModel, BaseSettings, Field, validator, root_validator

from typing import Optional, Tuple, Literal

class RelatedIssue(BaseModel):
    lawName: str
    issueRef: str


class Attachment(BaseModel):
    fileName: str 
    fileUrl: str

class Party(BaseModel):
    group: list[str]
    title: str
    value: str
class Judgment(BaseModel):
    """ use lawsnote as reference first """
    court: str
    date: str
    no: str
    sys: str
    reason: str 
    judgement: str
    type: str # 判決或裁定
    historyHash: str
    mainText: str
    opinion: str
    relatedIssues: list[RelatedIssue]
    attachAsJudgement: Optional[str] # url 
    attachments: Optional[list[Attachment]] 
    party: Optional[list[Party]]



