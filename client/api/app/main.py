import pathlib

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import os
from stat import *

from starlette.websockets import WebSocketDisconnect

from ray_deployment import RayDeployment

PATH = pathlib.Path(__file__).parent.resolve()
RESULTS_PATH = os.path.join(PATH, "ray_results")

BLACKLIST_FILES = ['params', 'progress', 'result', 'event', 'experiment', 'error', 'basic']
LOOKBACK_WINDOW = 40


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


@app.websocket("/deploy_ws")
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
        label = np.datetime_as_string(df['Date'].values[current_step], unit='m')
        print(f'started {benchmarks}', flush=True)
        await websocket.send_json({
            'status': 'sucess',
            'action': 'start',
            'net_worth': net_worths,
            'balance': balance,
            'asset_held': asset_held,
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

                prices_period = message.get('price_period', LOOKBACK_WINDOW)

                window_start = max(current_step - prices_period, 0)
                data_range = range(window_start, current_step + 1)
                data_slice = slice(window_start, current_step + 1)

                labels = np.datetime_as_string(df['Date'].values[data_slice], unit='m').tolist()
                net_worths = net_worths[data_slice]

                trades = list(filter(lambda trade: trade.get('step', -1) in data_range, trades))

                await websocket.send_json({
                    'status': 'success',
                    'action': 'next',
                    'net_worth': net_worths,
                    'balance': balance,
                    'asset_held': asset_held,
                    'window_start': window_start,
                    'labels': labels,
                    'prices': df.iloc[data_slice]['Close'].tolist(),
                    'trades': trades,
                })
    except WebSocketDisconnect as e:
        if ray_deployment:
            ray_deployment.disconnect()


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
