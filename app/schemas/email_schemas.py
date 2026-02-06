from pydantic import BaseModel

class EmailCreate(BaseModel):
    sender: str
    subject: str
    body: str

class EmailResponse(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    replied: bool

    class Config:
        orm_mode = True
