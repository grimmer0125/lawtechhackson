from enum import Enum, auto, IntEnum
from strenum import StrEnum


class Court(StrEnum):
    Taiwan_Shilin_District_Court = "臺灣士林地方法院"
    Taiwan_High_Court = "臺灣高等法院"
    Intellectual_Property_and_Commercial_Court = "智慧財產法院"
    Superme_Court = "最高法院"
    Taiwan_Kaohsiung_Juvenile_and_Family_Court = "臺灣高雄少年及家事法院"  # only 民事
    Judical_Yan = "司法院"  # 司法行政廳, only Criminal_Compensation


class LawType(StrEnum):
    Criminal = "刑事"
    Civil = "民事"
    Criminal_Compensation = "－刑事補償"


class JudgmentType(StrEnum):
    Judgment = "裁定"
    Ruling = "判決"


class PartyGroup(StrEnum):
    plaintiff = "plaintiff"
    defendant = "defendant"
    lawyer = "lawyer"
    agentAdLitem = "agentAdLitem"


def c(str1, str2):
    return f"{str1}_{str2}"
