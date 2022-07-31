from pydantic import BaseSettings

class DatasetSettings(BaseSettings):

    LAWSNOTE_JUDGMENT_PATH = "" 
    DRAWTOWN_JUDGMENT_PATH = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"