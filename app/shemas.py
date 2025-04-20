from pydantic import BaseModel

class Url_request(BaseModel):
    fileName: str # input.mp4
    fileType: str # video/mp4

class WorkflowRequest(BaseModel):
    name: str