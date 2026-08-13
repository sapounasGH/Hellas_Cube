from pydantic import BaseModel

#Data transfer object (DTO)
class dto(BaseModel):
    req_type:   str
    place:      str
    index:      str
    date1:      str
    date2:      str
    source:     str