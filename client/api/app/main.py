import hashlib
import pathlib

import numpy as np
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
from fastapi.responses import JSONResponse
import os
from stat import *

from starlette.websockets import WebSocketDisconnect

from ray_deployment import RayDeployment

PATH = pathlib.Path(__file__).parent.resolve()
RESULTS_PATH = os.path.join(PATH, "ray_results")

BLACKLIST_FILES = ['params', 'progress', 'result', 'event', 'experiment', 'error', 'basic']
LOOKBACK_WINDOW = 40
ASSET_BALANCE_WINDOW = 10

KEY = "1a46f2b7-b2e5-4bfd-a806-5c35c9368aa3"

WHITELIST_ROUTES = ["/api/auth", ]


# fast api functions
def get_application():
    _app = FastAPI(title="RLTraderApi")

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


@app.middleware("http")
async def auth(request: Request, call_next):
    response = await call_next(request)
    path = request.scope.get("path")
    # Verify if the route is whitelisted from middelware
    if path in WHITELIST_ROUTES:
        return response
    request_key = request.headers.get("Authorization", None)
    print(f'\n\nheaders => {request.headers}', flush=True)
    print(f'request_key => {request_key}\n\n', flush=True)

    if request_key:
        request_key = request_key.split(" ")[1]
        hashed_key = hashlib.sha256(KEY.encode()).hexdigest()
        print(f'\n\ncorrect key => {hashed_key}', flush=True)
        print(f'check => {request_key == hashed_key}\n\n', flush=True)
        if hashed_key == request_key:
            return response

    # return None
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"details": "UNAUTHORIZED"},
        headers={"Access-Control-Allow-Origin": "*"}
    )


@app.post("/api/auth")
async def auth(request: Request):
    # Parse request body
    body = await request.json()
    key = body.get("key", None)

    print(f'\n\nprovided key => {key}\n\n', flush=True)
    print(f'\n\ncorrect key => {KEY}\n\n', flush=True)
    print(f'\n\ncheck => {KEY == key}\n\n', flush=True)
    if key:
        # Preparing key stored on server
        if KEY == key:
            hashed_key = hashlib.sha256(KEY.encode()).hexdigest()
            return {"accessToken": hashed_key}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Creds provided are incorrect")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Creds provided are incorrect")


@app.websocket("/api/deploy_ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({'status': 'success', 'action': 'connected'})

    ray_deployment = None
    message = None

    try:
        # waiting for deploy signal
        deploy = False
        while not deploy:
            message = await websocket.receive_json()
            deploy = message and message.get('deploy', False)

        ray_deployment = RayDeployment(
            message.get('expirement'),
            message.get('algo'),
            message.get('reward'),
            message.get('checkpoint')
        )
        df = ray_deployment.env.data_provider.ep_timesteps()

        await websocket.send_json({'status': 'success', 'action': 'deploy'})

        # waiting for the start signal
        start = False
        while not start:
            message = await websocket.receive_json()
            start = message and message.get('start', False)

        current_step, net_worths, benchmarks, trades, balance, asset_held = ray_deployment.start()
        current_price = float(df.iloc[current_step]['Close'])
        assets_held = [asset_held * current_price]
        balances = [balance]
        label = np.datetime_as_string(df['Date'].values[current_step], unit='m')
        # print(f'started {benchmarks}', flush=True)
        await websocket.send_json({
            'status': 'sucess',
            'action': 'start',
            'net_worth': net_worths,
            'balances': balances,
            'assets_held': assets_held,
            'window_start': 0,
            'labels': [label],
            'prices': [float(df.iloc[current_step]['Close'])],
            'trades': [],
        })

        # receiving 'next' messages
        while True:
            message = await websocket.receive_json()
            if message and message.get('next', False):
                current_step, net_worths, benchmarks, trades, balance, asset_held = ray_deployment.next_action()

                current_price = float(df.iloc[current_step]['Close'])

                assets_held.append(asset_held * current_price)
                balances.append(balance)

                prices_period = message.get('price_period', LOOKBACK_WINDOW)

                window_start = max(current_step - prices_period, 0)
                data_range = range(window_start, current_step + 1)
                data_slice = slice(window_start, current_step + 1)

                asset_start = max(current_step - ASSET_BALANCE_WINDOW, 0)
                asset_slice = slice(asset_start, current_step + 1)

                labels = np.datetime_as_string(df['Date'].values[data_slice], unit='m').tolist()
                net_worths = net_worths[data_slice]

                trades = list(filter(lambda trade: trade.get('step', -1) in data_range, trades))

                await websocket.send_json({
                    'status': 'success',
                    'action': 'next',
                    'net_worth': net_worths,
                    'balances': balances[asset_slice],
                    'assets_held': assets_held[asset_slice],
                    'window_start': window_start,
                    'labels': labels,
                    'prices': df.iloc[data_slice]['Close'].tolist(),
                    'trades': trades,
                })
    except WebSocketDisconnect as e:
        if ray_deployment:
            ray_deployment.disconnect()


@app.get("/api/models")
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
