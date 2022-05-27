from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket


# from app.ga.tsp_app import TspAPP

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
