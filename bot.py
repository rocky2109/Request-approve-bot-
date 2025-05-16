import os
import logging
import asyncio
from dotenv import load_dotenv
from pyrogram import Client
from aiohttp import web

# Required dependencies: pip install pyrogram aiohttp python-dotenv

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

# Load environment variables from .env file
load_dotenv()

# Bot configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Define routes for aiohttp web server
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    """Handle root URL and return a simple HTML response."""
    return web.Response(
        text='<h3 align="center"><b>I am Alive</b></h3>',
        content_type='text/html'
    )

async def setup_web_server():
    """Set up the aiohttp web server."""
    web_app = web.Application(client_max_size=30000000)  # 30MB max size for client requests
    web_app.add_routes(routes)
    return web_app

class Bot(Client):
    def __init__(self):
        """Initialize the Pyrogram bot client."""
        super().__init__(
            "auto_approve_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=10
        )
        self.web_runner = None
        self.username = None

    async def start(self):
        """Start the aiohttp web server and Pyrogram client."""
        # Start aiohttp web server
        try:
            web_app = await setup_web_server()
            self.web_runner = web.AppRunner(web_app)
            await self.web_runner.setup()
            bind_address = "0.0.0.0"
            port = int(os.environ.get("PORT", 8080))
            if not (1 <= port <= 65535):
                raise ValueError(f"Invalid port number: {port}")
            await web.TCPSite(self.web_runner, bind_address, port).start()
            logger.info(f"Web server started on http://{bind_address}:{port}")
        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            raise

        # Start Pyrogram client
        try:
            await super().start()
            me = await self.get_me()
            self.username = '@' + me.username
            logger.info(f"Bot started as {self.username}. Powered by @Techify  Powered by @TechifyBots")
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

    async def stop(self):
        """Stop the Pyrogram client and aiohttp web server."""
        # Stop Pyrogram client
        try:
            await super().stop()
            logger.info("Bot stopped successfully.")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")

        # Stop aiohttp web server
        if self.web_runner:
            try:
                await self.web_runner.cleanup()
                logger.info("Web server stopped successfully.")
            except Exception as e:
                logger.error(f"Error stopping web server: {e}")

async def main():
    """Run the bot and handle startup/shutdown."""
    bot = Bot()
    try:
        await bot.start()
        await bot.idle()  # Keep the bot running
    except KeyboardInterrupt:
        logger.info("Received shutdown signal.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
