import os
from pyrogram import Client
from aiohttp import web
from config import API_ID, API_HASH, BOT_TOKEN
from plugins.bio import handle_join_request  # Import your handler here


r = web.RouteTableDef()

@r.get("/", allow_head=True)
async def root_route_handler(request):
    return web.Response(text='<h3 align="center"><b>I am Alive</b></h3>', content_type='text/html')

async def web_server():
    app = web.Application(client_max_size=30000000)
    app.add_routes(r)
    return app

class Bot(Client):
    def __init__(self):
        super().__init__(
            "techifybots",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),  # load all plugins in plugins folder
            workers=200,
            sleep_threshold=15
        )

    async def start(self):
        app = web.AppRunner(await web_server())
        await app.setup()

        ba = "0.0.0.0"
        port = int(os.environ.get("PORT", 8080)) or 8080  # Default port

        try:
            await web.TCPSite(app, ba, port).start()
            print(f"Web server started on http://{ba}:{port}")
        except Exception as e:
            print(f"Error starting the web server: {e}")

        await super().start()
        me = await self.get_me()
        self.username = '@' + me.username
        print(f'Bot Started Powered By {self.username}')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

bot = Bot()

# Correct way to register event handlers with your Client instance
@bot.on_chat_join_request()
async def on_join(client, request):
    await handle_join_request(client, request)

if __name__ == "__main__":
    bot.run()
