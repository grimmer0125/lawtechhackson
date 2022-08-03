from pydantic import BaseSettings


class DroidTownSettings(BaseSettings):
    droid_username = ""
    droid_api_key = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DataBaseSettings(BaseSettings):
    mongo_connect_str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DatasetSettings(BaseSettings):

    LAWSNOTE_JUDGMENT_PATH = ""
    DRAWTOWN_JUDGMENT_PATH = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"