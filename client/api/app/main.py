import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import sys
import os
from stat import *

# from app.ga.tsp_app import TspAPP

PATH = pathlib.Path(__file__).parent.resolve()
RESULTS_PATH = os.path.join(PATH, "ray_results_deployed")

BLACKLIST_FILES = ['params', 'progress', 'result', 'event', 'experiment', 'error', 'basic']


# fast api functions
def get_application():
    _app = FastAPI(title="raspApi")

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


@app.websocket("/routes_ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if "start" in data:
            # tsp = TspAPP(
            #     k_mut_prob=k_mut_prob,
            #     n_generations=k_n_generations,
            #     pop_size=k_population_size,
            #     tournament_size=tournament_size,
            #     elitism=elitism,
            #     csv_file="/api/app/algeria-cities.csv",
            #     websocket=websocket
            # )
            # send chain of routes until it done iterating
            # await tsp.GA_loop()
            await websocket.send_text('good job connecting to this websocket')


@app.get("/models")
def get_models():
    # get list of folders and models
    file_structures = path_to_dict(RESULTS_PATH)
    return file_structures


# recursive function to get files
# structures
def path_to_dict(path):
    st = os.stat(path)
    result = {'full_path': path}
    if S_ISDIR(st.st_mode):
        result['type'] = 'd'
        if "checkpoint" not in path:
            result['items'] = {
                name: path_to_dict(os.path.join(path, name))
                for name in list(filter(lambda name: not file_blacklisted(name), os.listdir(path)))}
    else:
        result['type'] = 'f'
    return result


def file_blacklisted(name):
    for item in BLACKLIST_FILES:
        if item in name:
            return True
    return False
