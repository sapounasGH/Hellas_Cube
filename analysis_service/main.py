import indexes
import uvicorn
import time
from fastapi import FastAPI, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dask.distributed import Client, LocalCluster
from set_AWS import set_AWS


class ndi_req(BaseModel):
    req_type: str
    place: str
    index: str
    date1: str
    date2: str


class IndexRouter:
    #Class for making the routes of our API dynamicly

    def __init__(self, app: FastAPI, analyzation, needs_dask: bool = True):
        self.app = app
        self.analyzation = analyzation
        self.needs_dask = needs_dask

    def register(self, path: str, label: str, method_name: str):

        #method we are going to execute 
        method = getattr(self.analyzation, method_name)

        async def handler(req: ndi_req, request: Request):
            start = time.time()
            dask_client = request.app.state.dask_client if self.needs_dask else None

            args = (req.place, req.date1, req.date2, dask_client, req.req_type) \
                if self.needs_dask else (req.place, req.date1, req.date2, req.req_type)
            result = method(*args)

            place = req.place if req.req_type == "TARGET" else "Default"
            elapsed = f"{round(time.time() - start, 2)}s"

            response = {
                "STATUS": "OK",
                "analyzation": label,
                "place": place,
                "result": result,
                "time": elapsed,
            }
            print(response)
            return response

        self.app.post(path)(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    set_AWS()  # TODO: security issue — revisit before deploying
    cluster = LocalCluster(n_workers=4, 
                           threads_per_worker=2, 
                           memory_limit="4GB")
    client = Client(cluster)
    app.state.dask_client = client
    print(f"Dask dashboard: {client.dashboard_link}")
    yield
    client.close()
    cluster.close()


app = FastAPI(title="HellasCube", version="0.0.1", lifespan=lifespan)
analyzation = indexes.env_ind()

router = IndexRouter(app, analyzation)
router.register("/analyzation/ndvi", "NDVI", "ndvi")
router.register("/analyzation/ndci", "NDCI", "ndci")
router.register("/analyzation/ndti", "NDTI", "ndti")
router.register("/analyzation/ndwi", "NDWI", "ndwi")
router.register("/analyzation/ndmi", "NDMI", "ndmi")
router.register("/analyzation/ndbi", "NDBI", "ndbi")
router.register("/analyzation/ndsi", "NDSI", "ndsi")
router.register("/analyzation/sdd", "SDD", "sdd")

# WOfS doesn't use the Dask client (per your comment), so give it its own router instance
wofs_router = IndexRouter(app, analyzation, needs_dask=False)
wofs_router.register("/analyzation/wofs", "WOFS", "flood_wofs")


@app.get("/test")
def working():
    return {"STATUS": "OK", "MESSAGE": "SERVER IS RUNNING", "QUOTE": "WINTER IS COMING"}


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


if __name__ == "__main__":
    main()


#old method use it on thesis writing
"""
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
    set_AWS() #seecurity problem here! change this after finishing it working
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
    #CERTAIN FIX ! we can change that and have a json that decodes the analyzation i want to do 
    #Here we will be routing to the functions USE CLASSES dont forget...

class ndi_req(BaseModel):
    req_type:str
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
    ansr=analyzation.ndvi(req.place, req.date1, req.date2, dask_client, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s"
    json={
        "STATUS":"OK",
        "analyzation": "NDVI",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)


@app.post("/analyzation/ndci")
def ndci(req: ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndci(req.place, req.date1, req.date2, dask_client, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDCI",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndti")
def ndti(req: ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndti(req.place, req.date1, req.date2, dask_client, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s"
    json={
        "STATUS":"OK",
        "analyzation": "NDTI",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndwi")
def ndwi(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndwi(req.place, req.date1, req.date2, dask_client, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDWI",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndmi")
def ndmi(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndmi(req.place, req.date1, req.date2, dask_client, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDMI",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndbi")
def ndbi(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndbi(req.place, req.date1, req.date2, dask_client, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDBI",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/ndsi")
def ndsi(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.ndsi(req.place, req.date1, req.date2, dask_client, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "NDSI",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/wofs")
def wofs(req: ndi_req, request: Request):
    start = time.time()
    #dask_client = request.app.state.dask_client #THREADING!dask_client,
    ansr=analyzation.flood_wofs(req.place, req.date1, req.date2, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "WOFS",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

@app.post("/analyzation/sdd")
def sdd(req:ndi_req, request: Request):
    start = time.time()
    dask_client = request.app.state.dask_client #THREADING!
    ansr=analyzation.sdd(req.place, req.date1, req.date2, dask_client, req.req_type)
    if req.req_type=="DEFAULT":
        place: str="Default"
    elif req.req_type=="TARGET":
        place: str=req.place
    end =time.time()
    finish=f"{round(end-start, 2)}s" 
    json={
        "STATUS":"OK",
        "analyzation": "SDD(Secchi Disk Depth)",
        "place":place,
        "result": ansr,
        "time": finish
    }
    print(json)
    return(json)

if __name__=="__main__":
   main()
"""