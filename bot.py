import os
import logging
import asyncio
from pyrogram import Client
from pyrogram.handlers import ChatJoinRequestHandler
from pyrogram.errors import AuthKeyUnregistered, FloodWait
from aiohttp import web
from config import API_ID, API_HASH, BOT_TOKEN
from plugins.bio import handle_join_request  # Import from bio.py

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define routes for aiohttp web server
r = web.RouteTableDef()

@r.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text='<h3 align="center"><b>I am Alive</b></h3>', content_type='text/html')

async def wsrvr():
    wa = web.Application(client_max_size=30000000)
    wa.add_routes(r)
    return wa

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="auto_approve_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        # Start aiohttp web server
        try:
            app = web.AppRunner(await wsrvr())
            await app.setup()
            ba = "0.0.0.0"
            port = int(os.environ.get("PORT", 8080)) or 8080
            await web.TCPSite(app, ba, port).start()
            logger.info(f"Web server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start web server: {type(e).__name__}: {e}", exc_info=True)
            raise

        # Start Pyrogram client
        try:
            logger.info("Starting bot...")
            await super().start()
            me = await self.get_me()
            self.username = '@' + me.username
            logger.info(f"Bot started as {self.username} | Powered By @TechifyBots")
        except FloodWait as e:
            wait_time = e.value + 10  # Add buffer
            logger.warning(f"FloodWait: Waiting for {wait_time} seconds before retrying")
            await asyncio.sleep(wait_time)
            logger.info("Retrying bot start after FloodWait")
            await self.start()  # Retry
        except AuthKeyUnregistered:
            logger.error("Invalid or revoked bot token. Please check with @BotFather.")
            raise
        except Exception as e:
            logger.error(f"Failed to start bot: {type(e).__name__}: {e}", exc_info=True)
            raise

    async def stop(self, *args):
        logger.info("Stopping bot...")
        await super().stop()
        logger.info("Bot stopped | Bye")

async def main():
    bot = Bot()
    # Register the join request handler
    bot.add_handler(ChatJoinRequestHandler(
        lambda client, m: handle_join_request(client, m, NEW_REQ_MODE=True, LOG_GROUP=-100123456789)  # Replace LOG_GROUP
    ))
    await bot.start()
    logger.info("Bot is running...")
    await bot.idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to run bot: {type(e).__name__}: {e}", exc_info=True)
