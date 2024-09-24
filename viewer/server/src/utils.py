# https://github.com/Venom-Biochem-Lab/venome/blob/main/backend/src/setup.py
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict


def disable_cors(app: FastAPI, origins=["*"]):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


def serve_endpoints(app: FastAPI, modules):
    include_routers(app, [m.router for m in modules])


def include_routers(app: FastAPI, routers: list[APIRouter]):
    for r in routers:
        app.include_router(r)


# https://github.com/zeno-ml/zeno/blob/main/zeno/server.py#L52
def custom_generate_unique_id(route: APIRoute):
    return route.name


def init_fastapi_app() -> FastAPI:
    app = FastAPI(
        title="Backend", generate_unique_id_function=custom_generate_unique_id
    )
    return app


# https://github.com/zeno-ml/zeno-hub/blob/9d2f8b5841d99aeba9ec405b0bc6a5b1272b276f/backend/zeno_backend/classes/base.py#L20
def to_camel(string: str) -> str:
    """Converter for variables from snake_case to camelCase.

    Args:
        string (str): the variable to convert to camelCase.

    Returns:
        str: camelCase representation of the variable.
    """
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


# https://github.com/zeno-ml/zeno-hub/blob/9d2f8b5841d99aeba9ec405b0bc6a5b1272b276f/backend/zeno_backend/classes/base.py#L20
class CamelModel(BaseModel):
    """Converting snake_case pydantic models to camelCase models."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)  # type: ignore
