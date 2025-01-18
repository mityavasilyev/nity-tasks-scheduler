from aiohttp import web

from utils.logger import AppLogger

logger = AppLogger.get_logger(__name__)


async def health_handler(request):
    return web.Response(text='OK', status=200)


app = web.Application()
app.router.add_get('/health', health_handler)


async def run_health_server():
    logger.info('Starting health server')
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8080)
    await site.start()
    logger.info('Health server started at http://localhost:8080/health')
