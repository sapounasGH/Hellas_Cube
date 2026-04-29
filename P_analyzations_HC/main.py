import indexes
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

#for testing
import time

app = FastAPI(title="HellasCube", version="0.0.1")        
analyzation = indexes.env_ind()

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

   # CERTAIN FIX ! we can change that and have a json that decodes the analyzation i want to do 
   #Here we will be routing to the functions USE CLASSES dont forget...

   #A BIG IF to choose index  with the sys argv

class ndi_req(BaseModel):
    place: str
    index: str
    date1: str
    date2: str

@app.get("/")
def working():
    json={
        "STATUS":"OK",
        "MESSAGE": "SERVER IS RUNNING"
    }
    print(json)
    return(json)

@app.post("/analyzation/ndvi")
def ndvi(req: ndi_req):
    start = time.time()
    ansr=analyzation.ndvi(req.place, req.date1, req.date2) 
    time.sleep(1)
    end = time.time()
    json={
        "STATUS":"OK",
        "analyzation": "NDVI",
        "place":req.place,
        "result": ansr,
        "time": start-end
    }
    print(json)
    return(json)


@app.post("/analyzation/ndci")
def ndci(req: ndi_req):
    print(f"{analyzation.ndci(req.place, req.date1, req.date2)}")

@app.post("/analyzation/ndti")
def ndci(req: ndi_req):
    print(f"{analyzation.ndti(req.place, req.date1, req.date2)}")

@app.post("/analyzation/wofs")
def ndci(req: ndi_req):
    print(f"{analyzation.flood_wofs(req.place, req.date1, req.date2)}") 

if __name__=="__main__":
   main()