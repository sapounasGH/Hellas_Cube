"""
File: data_manager.py
Author: Christos Sapounas
Latest Description Change: 04/07/2026 
Description: This is the data manager, it helps us load the dataset, expoort statistics for our results
"""

#imports
import indexes
import uvicorn
import time
from fastapi import FastAPI, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dask.distributed import Client, LocalCluster
from set_AWS import set_AWS

#A class model for our requests
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

        #method we are going to execute (name of the method)
        method = getattr(self.analyzation, method_name)

        #asynchronus function
        async def handler(req: ndi_req, request: Request):

            #start of timing the function
            start = time.time()

            #threading calling the dask_client, we are going to use multiple threads with dask client
            dask_client = request.app.state.dask_client if self.needs_dask else None

            #calling the methods with the arguments required
            args = (req.place, req.date1, req.date2, dask_client, req.req_type) \
                if self.needs_dask else (req.place, req.date1, req.date2, req.req_type)
            
            result = method(*args)


            #We have 2 requests type default for the users, target for the ones that used the systems targeted areas
            if req.req_type=="DEFAULT":

                #just passing the default string
                place: str="Default"
            elif req.req_type=="TARGET":

                #passing the areas string name
                place: str=req.place

            #end of timing the function
            elapsed = f"{round(time.time() - start, 2)}s"

            #Declaring the response
            response = {
                "STATUS": "OK",
                "analyzation": label,
                "place": place,
                "result": result,
                "time": elapsed,
            }

            #sending back the response
            print(response)
            return response

        #setting the api end points
        self.app.post(path)(handler)


#Declaring what the API will do in it's life cycle
#On Start up method of the Fast API
@asynccontextmanager
async def lifespan(app: FastAPI):

    # TODO: security issue (use enviromental variables) revisit before deploying
    #setting the aws credentials
    set_AWS()

    #cluster workers for mutliple threads now we use 8 (4*2) threads with a limit of 4 GB of memory usage
    cluster = LocalCluster(n_workers=4, 
                           threads_per_worker=2,
                           #memory limit per worker, from documendation : (Sets the memory limit per worker) 
                           memory_limit="4GB") 

    #From Client Documendation:    The Client connects users to a Dask cluster.
    client = Client(cluster)

    #setting the dask client with the client we just crated
    app.state.dask_client = client
    print(f"Dask dashboard: {client.dashboard_link}")

    #On close
    yield
    client.close()
    cluster.close()


app = FastAPI(title="HellasCube", version="0.0.1", lifespan=lifespan)

#TODO: Change the names analyzation to analysis whole api will change of course
#object fo analysis indexes
analyzation = indexes.env_ind()

#Constructing a router with a dask
router = IndexRouter(app, analyzation)
router.register("/analyzation/ndvi", "NDVI", "ndvi")
router.register("/analyzation/ndci", "NDCI", "ndci")
router.register("/analyzation/ndti", "NDTI", "ndti")
router.register("/analyzation/ndwi", "NDWI", "ndwi")
router.register("/analyzation/ndmi", "NDMI", "ndmi")
router.register("/analyzation/ndbi", "NDBI", "ndbi")
router.register("/analyzation/ndsi", "NDSI", "ndsi")

# Landsat data do not use the Dask client
no_duck_router = IndexRouter(app, analyzation, needs_dask=False)
no_duck_router.register("/analyzation/wofs", "WOFS", "flood_wofs")
no_duck_router.register("/analyzation/sdd", "SDD", "sdd")

#test point
@app.get("/test")
def working():
    return {"STATUS": "OK", "MESSAGE": "SERVER IS RUNNING", "QUOTE": "WINTER IS COMING"}

#running the server
def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

#executing the main method on python main.py
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