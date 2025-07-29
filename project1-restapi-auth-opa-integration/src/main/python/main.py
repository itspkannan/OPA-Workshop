from restapi_auth_opa_integration.app import startup
import asyncio
import uvloop
from environs import Env

if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    env = Env()
    config_dir = env.str("CONFIG_DIR", '/app/config')
    startup(config_dir)