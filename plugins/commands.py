import asyncio 
from pyrogram import Client, filters, enums
from config import *
from .database import db
from .fsub import get_fsub
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import datetime
import time
import logging
from pyrogram.types import ChatJoinRequest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def retry_with_backoff(retries, coroutine, *args, **kwargs):
    delay = 1
    for attempt in range(retries):
        try:
            return await coroutine(*args, **kwargs)
        except (TimeoutError, ConnectionError) as e:
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(delay)
            delay *= 2

@Client.on_message(filters.command("start"))
async def start_message(c, m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(LOG_CHANNEL, f"<b>#NewUser\nID - <code>{m.from_user.id}</code>\nName - {m.from_user.mention}</b>")

    if IS_FSUB and not await get_fsub(c, m): return

    text = (
        f"{m.from_user.mention},\n\n"
        "𝖨 𝖼𝖺𝗇 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖺𝗉𝗉𝗋𝗈𝗏𝖾 𝗇𝖾𝗐 & 𝗉𝖾𝗇𝖽𝗂𝗇𝗀 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗂𝗇 any C𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝗈𝗋 G𝗋𝗈𝗎𝗉𝗌.\n\n"
        "𝖩𝗎𝗌𝗍 𝖺𝖽𝖽 𝗆𝖾 𝗂𝗇 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝖺𝗇𝖽 𝗀𝗋𝗈𝗎𝗉𝗌 𝗐𝗂𝗍𝗁 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝖺𝖽𝖽 𝗇𝖾𝗐 𝗆𝖾𝗆𝖻𝖾𝗋𝗌.\n\n"
        "𝖴𝗌𝖾 /help for Guide\n\n"
        "**<blockquote>ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : @Real_Pirates 🏴‍☠️</blockquote>**"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⇆", url="https://t.me/Music_queen_X_bot?startgroup=true&admin=invite_users")],
        [InlineKeyboardButton("• 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 •", url="https://t.me/+sQXky-6HHq8xMTk1"),
         InlineKeyboardButton("• 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 𝐆𝐫𝐨𝐮𝐩 •", url="https://t.me/Movie_Pirates_x")],
        [InlineKeyboardButton("⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⇆", url="https://t.me/Music_queen_X_bot?startchannel=true&admin=invite_users")],
    ])

    await m.reply_text(text, reply_markup=buttons)

@Client.on_message(filters.command('help'))
async def help_message(c, m):
    await m.reply_text(
        f"""**Dear {m.from_user.mention},**

𝖱𝖾𝖺𝖽 𝗍𝗁𝗂𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝖼𝖺𝗋𝖾𝖿𝗎𝗅𝗅𝗒 𝗌𝗈 𝗒𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗁𝖺𝗏𝖾 𝖺𝗇𝗒 𝗉𝗋𝗈𝖻𝗅𝖾𝗆𝗌 𝗐𝗁𝗂𝗅𝖾 joining channels.

🎯 **Join Any Channel in Just 2 Simple Steps** 🤫

🔹 **Step 1️⃣**  
To get access of any channels,add **any one tag** in your bio.

🎬 **Movie Channels**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰  
• `@Real_Pirates`  
• `@Drama_Loverx`

📚 **Study / Skills Channels**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰  
• `@II_Way_to_Success_II`  
• `@Myownsuccess`  
• `@Just_Vibing_Alone`  
_Tap to Copy ↑_

🔹 **Step 2️⃣**  
Once you've added **Any One** of these in your bio,  
Try joining again using the invite link —  
I'll be happy to approve your request! 🥰
""",
        disable_web_page_preview=True
    )
@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def users(bot, message):
   total_users = await db.total_users_count()
   await message.reply_text(
        text=f'◉ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {total_users}'
   )

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text("Broadcasting your messages...")
    
    start_time = time.time()
    total_users = await db.total_users_count()

    # Initialize Counters
    done, blocked, deleted, failed, success = 0, 0, 0, 0, 0

    async for user in users:
        if 'id' in user:
            user_id = int(user['id'])
            try:
                await retry_with_backoff(5, b_msg.copy, chat_id=user_id)
                success += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                try:
                    await b_msg.copy(chat_id=user_id)
                    success += 1
                except Exception:
                    failed += 1
            except InputUserDeactivated:
                await db.delete_user(user_id)
                logging.info(f"{user_id} - Removed from database (Deleted Account).")
                deleted += 1
            except UserIsBlocked:
                await db.delete_user(user_id)
                logging.info(f"{user_id} - Blocked the bot.")
                blocked += 1
            except PeerIdInvalid:
                await db.delete_user(user_id)
                logging.info(f"{user_id} - PeerIdInvalid")
                failed += 1
            except Exception:
                failed += 1
            
            done += 1
            if not done % 20:
                await sts.edit(f"Broadcast in progress:\n\nTotal Users: {total_users}\nCompleted: {done}/{total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
    
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done}/{total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    show = await message.reply("**Please Wait.....**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**For Accepte Pending Request You Have To /login First.**")
        return
    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
    show = await show.edit("**Now Forward A Message From Your Channel Or Group With Forward Tag\n\nMake Sure Your Logged In Account Is Admin In That Channel Or Group With Full Rights.**")
    vj = await client.listen(message.chat.id)
    if vj.forward_from_chat and not vj.forward_from_chat.type in [enums.ChatType.PRIVATE, enums.ChatType.BOT]:
        chat_id = vj.forward_from_chat.id
        try:
            await retry_with_backoff(5, acc.get_chat, chat_id)
        except:
            await show.edit("**Error - Make Sure Your Logged In Account Is Admin In This Channel Or Group With Rights.**")
    else:
        return await message.reply("**Message Not Forwarded From Channel Or Group.**")
    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    try:
        while True:
            await retry_with_backoff(5, acc.approve_all_chat_join_requests, chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** {str(e)}")

