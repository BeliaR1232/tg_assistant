import logging

from arq import create_pool, cron
from arq.connections import RedisSettings
from pytz import timezone
from telegram import Bot

from src.configs import settings
from src.scheduler.tasks import check_events, send_reminder

redis_settings = RedisSettings(host="redis")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def startup(ctx):
    ctx["bot"] = Bot(settings.bot.reminder_token)
    ctx["redis"] = await create_pool(redis_settings)


async def shutdown(ctx):
    await ctx["bot"].shutdown()
    await ctx["redis"].aclose()


async def main():
    redis = await create_pool(RedisSettings())
    await redis.enqueue_job("download_content", "https://httpbin.org/status/503")


class WorkerSettings:
    functions = [send_reminder]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = redis_settings
    cron_jobs = [cron(check_events, second={1, 30})]
    timezone = timezone("Europe/Moscow")
