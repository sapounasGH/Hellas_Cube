import indexes
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from set_AWS import set_AWS
#Threading
from dask.distributed import Client, LocalCluster

#for testing
import time

#for logging
#import logging
#import json

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    set_AWS()
    cluster = LocalCluster(
        n_workers=4,           
        threads_per_worker=2, 
        memory_limit="4GB"    
    )
    client = Client(cluster)
    app.state.dask_client = client
    print(f"Dask dashboard: {client.dashboard_link}")
    yield
    client.close()
    cluster.close()

app = FastAPI(title="HellasCube", version="0.0.1", lifespan=lifespan)      
analyzation = indexes.env_ind()

def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
   # CERTAIN FIX ! we can change that and have a json that decodes the analyzation i want to do 
   #Here we will be routing to the functions USE CLASSES dont forget...

class ndi_req(BaseModel):
    place: str
    index: str
    date1: str
    date2: str

@app.get("/test")
def working():
    json={
        "STATUS":"OK",
        "MESSAGE": "SERVER IS RUNNING",
        "QUOTE":"WINTER IS COMING"
    }
    print(json)
    return(json)

@app.post("/analyzation/ndvi")
def ndvi(req: ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndvi(req.place, req.date1, req.date2, dask_client) 
    end =time.time()
    finish=f"{round(end-start, 2)}s"
    json={
        "STATUS":"OK",
        "analyzation": "NDVI",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)


@app.post("/analyzation/ndci")
def ndci(req: ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndci(req.place, req.date1, req.date2, dask_client)
    time.sleep(1)
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDCI",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndti")
def ndti(req: ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndti(req.place, req.date1, req.date2, dask_client)
    time.sleep(1)
    end =time.time()
    finish=f"{round(end-start, 2)}s"
    json={
        "STATUS":"OK",
        "analyzation": "NDTI",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndwi")
def ndwi(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndwi(req.place, req.date1, req.date2, dask_client)
    time.sleep(1)
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDWI",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndmi")
def ndmi(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndmi(req.place, req.date1, req.date2, dask_client)
    time.sleep(1)
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDMI",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndbi")
def ndbi(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndbi(req.place, req.date1, req.date2, dask_client)
    time.sleep(1)
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDBI",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndsi")
def ndsi(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndsi(req.place, req.date1, req.date2, dask_client)
    time.sleep(1)
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDSI",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/wofs")
def wofs(req: ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.flood_wofs(req.place, req.date1, req.date2, dask_client)
    time.sleep(1)
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "WOFS",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/sdd")
def sdd(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.sdd(req.place, req.date1, req.date2, dask_client)
    time.sleep(1)
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "SDD(Secchi Disk Depth)",
        "place":req.place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

def log(data):
    pass

if __name__=="__main__":
   main()