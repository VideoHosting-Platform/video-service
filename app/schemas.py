from pydantic import BaseModel, Field


class VideoCreate(BaseModel):
    title: str
    video_url: str
    video_id: str
    # author_fk: int = Field(alias="author_id")

class VideoReturn(BaseModel):
    title: str
    video_url: str
    video_id: str
    views: int
    likes: int
    dislikes:int

class User(BaseModel):
    name: str
    email: str
    # password:str

class Url_request(BaseModel):
    fileName: str # input.mp4
    fileType: str # video/mp4

class WorkflowRequest(BaseModel):
    name: str