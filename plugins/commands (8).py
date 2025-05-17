import asyncio
import random
import logging
import datetime
import time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from config import *
from .database import db
from pyrogram.types import Message
from .fsub import get_fsub
from threading import Thread

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define NEW_REQ_MODE (configurable)
NEW_REQ_MODE = True  # Set to False to disable auto-approval

async def retry_with_backoff(retries, coroutine, *args, **kwargs):
    """Retry a coroutine with exponential backoff."""
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
    """Handle /start command and initialize user."""
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id, m.from_user.first_name)
        await c.send_message(
            LOG_CHANNEL,
            f"<b>#NewUser\nID - <code>{m.from_user.id}</code>\nName - {m.from_user.mention}</b>"
        )

    if IS_FSUB and not await get_fsub(c, m):
        return

    text = (
        f"Ahoy 👋 {m.from_user.mention},\n\n"
        "𝖨 𝖼𝖺𝗇 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖺𝗉𝗉𝗋𝗈𝗏𝖾 𝗇𝖾𝗐 & 𝗉𝖾𝗇𝖽𝗂𝗇𝗀 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗂𝗇 any C𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝗈𝗋 G𝗋𝗈𝗎𝗉𝗌.\n\n"
        "𝖩𝗎𝗌𝗍 𝖺𝖽𝖽 𝗆𝖾 𝗂𝗇 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌 𝖺𝗇𝖽 𝗀𝗋𝗈𝗎𝗉𝗌 𝗐𝗂𝗍𝗁 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇 𝗍𝗈 𝖺𝖽𝖽 𝗇𝖾𝗐 𝗆𝖾𝗆𝖻𝖾𝗋𝗌.\n\n"
        "𝖴𝗌𝖾 /help for Guide\n\n"
        "**<blockquote>ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ : @Real_Pirates 🏴‍☠️</blockquote>**"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⇆",
            url="https://t.me/Music_queen_X_bot?startgroup=true&admin=invite_users"
        )],
        [
            InlineKeyboardButton("• 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 •", url="https://t.me/+sQXky-6HHq8xMTk1"),
            InlineKeyboardButton("• 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 𝐆𝐫𝐨𝐮𝐩 •", url="https://t.me/Movie_Pirates_x")
        ],
        [InlineKeyboardButton(
            "⇆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ⇆",
            url="https://t.me/Music_queen_X_bot?startchannel=true&admin=invite_users"
        )],
    ])

    await m.reply_text(text, reply_markup=buttons)

@Client.on_message(filters.command('help'))
async def help_message(c, m):
    """Provide help instructions for joining channels."""
    await m.reply_text(
        f"""**Dear {m.from_user.mention},**

𝖱𝖾𝖺𝖽 𝗍𝗁𝗂𝗌 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝖼𝖺𝗋𝖾𝖿𝗎𝗅𝗅𝗒 𝗌𝗈 𝗒𝗈𝗎 𝖽𝗈𝗇'𝗍 𝗁𝖺𝗏𝖾 𝖺𝗇𝗒 𝗉𝗋𝗈𝖻𝗅𝖾𝗆𝗌 𝗐𝗁𝗂𝗅𝖾 joining channels.

🎯 **Join Any Channel in Just 2 Simple Steps** 🤫

🔹 **Step 1️⃣**  
To get access of any <b>Request to Join Channel</b>, add **Any One Tag** in your Bio,from below 👇

To Join
🎬 **Movie Channels**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰  
<blockquote>• `@Real_Pirates`</blockquote>  
<blockquote>• `@Drama_Loverx`</blockquote>

To Join
📚 **Study / Skills Channels**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰  
<blockquote>• `@II_Way_to_Success_II`</blockquote>  
<blockquote>• `@Myownsuccess`</blockquote>  
<blockquote>• `@Just_Vibing_Alone`</blockquote>  
<b><i>Tap to Copy 👆</i></b>

🔹 **Step 2️⃣**  
Once you've added **Any One** of these in your bio,  
Try joining again using the invite link —  
I'll be happy to approve your request! 🥰
""",
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def users(bot, message):
    """Display total number of users (admin only)."""
    total_users = await db.total_users_count()
    await message.reply_text(f'◉ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {total_users}')

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    """Broadcast a message to all users (.ConcurrentModificationException admin only)."""
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text("Broadcasting your messages...")
    
    start_time = time.time()
    total_users = await db.total_users_count()
    done = blocked = deleted = failed = success = 0

    async for user in users:
        if 'id' not in user:
            continue
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
            logger.info(f"{user_id} - Removed from database (Deleted Account).")
            deleted += 1
        except UserIsBlocked:
            await db.delete_user(user_id)
            logger.info(f"{user_id} - Blocked the bot.")
            blocked += 1
        except PeerIdInvalid:
            await db.delete_user(user_id)
            logger.info(f"{user_id} - PeerIdInvalid")
            failed += 1
        except Exception as e:
            logger.error(f"Failed to broadcast to {user_id}: {e}")
            failed += 1
        
        done += 1
        if done % 20 == 0:
            await sts.edit(
                f"Broadcast in progress:\n\n"
                f"Total Users: {total_users}\n"
                f"Completed: {done}/{total_users}\n"
                f"Success: {success}\n"
                f"Blocked: {blocked}\n"
                f"Deleted: {deleted}"
            )
    
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"Broadcast Completed:\n"
        f"Completed in {time_taken} seconds.\n\n"
        f"Total Users: {total_users}\n"
        f"Completed: {done}/{total_users}\n"
        f"Success: {success}\n"
        f"Blocked: {blocked}\n"
        f"Deleted: {deleted}"
    )

@Client.on_message(filters.command('accept') & filters.private)
async def accept(client, message):
    """Accept all pending join requests for a channel/group."""
    show = await message.reply("**Please Wait...**")
    user_data = await db.get_session(message.from_user.id)
    if user_data is None:
        await show.edit("**To accept pending requests, you must /login first.**")
        return

    try:
        acc = Client("joinrequest", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except Exception as e:
        await show.edit(f"**Login failed: {e}. Please /logout and /login again.**")
        return

    await show.edit(
        "**Forward a message from your channel or group with the forward tag.\n"
        "Ensure the logged-in account is an admin with full rights.**"
    )
    vj = await client.listen(message.chat.id)
    if not (vj.forward_from_chat and vj.forward_from_chat.type not in [enums.ChatType.PRIVATE, enums.ChatType.BOT]):
        await vj.delete()
        await show.edit("**Message not forwarded from a channel or group.**")
        return

    chat_id = vj.forward_from_chat.id
    try:
        await retry_with_backoff(5, acc.get_chat, chat_id)
    except Exception as e:
        await vj.delete()
        await show.edit(f"**Error: Ensure the logged-in account is an admin with rights. {e}**")
        return

    await vj.delete()
    msg = await show.edit("**Accepting all join requests... Please wait.**")
    
    max_attempts = 100  # Prevent infinite loop
    attempts = 0
    try:
        while attempts < max_attempts:
            await retry_with_backoff(5, acc.approve_all_chat_join_requests, chat_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(chat_id)]
            if not join_requests:
                break
            attempts += 1
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**Error occurred: {e}**")
    finally:
        await acc.disconnect()

user_bios = {}

# Function to check the user's bio every 2 minutes
async def check_bio_periodically(client, chat_id, user_id, original_bio, required_tags):
    """Check the user's bio every 2 minutes to see if it contains required tags."""
    await asyncio.sleep(120)  # Wait for 2 minutes asynchronously
    
    # Get the user's bio again asynchronously
    user = await client.get_users(user_id)
    updated_bio = user.bio if user.bio else ""

    # If the bio doesn't contain required tags, remove the user
    if not any(tag in updated_bio.lower() for tag in required_tags):
        await client.kick_chat_member(chat_id, user_id)
        print(f"User {user_id} does not have required tags, removed from the group.")

@Client.on_chat_join_request()
async def approve_new(client, m: ChatJoinRequest):
    """Automatically approve or decline join requests based on user bio."""
    if not NEW_REQ_MODE:
        return

    try:
        user = await client.get_chat(m.from_user.id)
        bio = user.bio or ""
        required_tags = [
            "@real_pirates",
            "@drama_loverx",
            "@ii_way_to_success_ii",
            "@myownsuccess",
            "@goal_achieverr",
            "@just_vibing_alone"
        ]

        if any(tag in bio.lower() for tag in required_tags):
            # Approve join request
            await retry_with_backoff(
                5, client.approve_chat_join_request, m.chat.id, m.from_user.id
            )
            
            chat_info = await client.get_chat(m.chat.id)
            member_count = chat_info.members_count
            full_name = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()


            approve_text = (
                f"🔓 <b>Access Granted ✅</b>\n\n"
                f"<b><blockquote> Cheers, <a href='https://t.me/Real_Pirates'>{full_name}</a> ! 🥂</blockquote></b>\n"
                f"Your Request To Join <b>{m.chat.title}</b> Has Been Approved! 🎉\n"
               
                f"We’re happy to have you with us. 🥰\n\n"
                f"💎 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 𝐂𝐨𝐮𝐧𝐭: <b>{member_count:,}</b> 🚀\n"
                f"┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌\n"
                
                f"⚠️⚠️⚠️\n"
                f"<b><i>||If you remove that Tag from your bio, you will be removed from the channel. 💀||\n"
                f"This tag is required to remain a verified member of ≫  {m.chat.title}.\n"
                f"Make sure to keep it in your Bio to avoid removal. 😉</i></b>\n"
                f"<blockquote>Supported by <b>➩ @Real_Pirates 🏴‍☠️</b></blockquote>"
               
            )

            stickers = [
                "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ",
                "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
                "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
            ]

            # Send approval message and sticker to user
            try:
                await client.send_message(m.from_user.id, approve_text, disable_web_page_preview=True)
                await client.send_sticker(m.from_user.id, random.choice(stickers))
            except Exception as e:
                logger.error(f"Failed to send approval to {m.from_user.id}: {e}")

            # Send approval message and sticker to log channel
            try:
                await client.send_message(-1002479860602, approve_text, disable_web_page_preview=True)
                await client.send_sticker(-1002479860602, random.choice(stickers))
            except Exception as e:
                logger.error(f"Failed to send to log channel: {e}")
        else:
            # Decline join request
            await retry_with_backoff(
                5, client.decline_chat_join_request, m.chat.id, m.from_user.id
            )

            # Send rejection message
            reject_text = f"""
🔒 **Access Denied** ❌

Dear **{m.from_user.mention}** 🌝

To join,<b>{m.chat.title}</b>
Follow These **2 Simple Steps**: 🤫

🔹 **Step 1️⃣**
**Add Any One Required Tag in your bio from the options below:** 👇

if it's 
🎬 **Movie Channel:**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰
<blockquote>• `@Real_Pirates`</blockquote>
<blockquote>• `@Drama_Loverx`</blockquote>

if it's 
📚 **Study / Skills Channel:**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰
<blockquote>• `@II_Way_to_Success_II`</blockquote>
<blockquote>• `@MyOwnSuccess`</blockquote>
<blockquote>• `@Just_Vibing_Alone`</blockquote>
<b><i>Tap to Copy 👆</i></b>

🔹 **Step 2️⃣**
Once You Update Your Bio With The **Required Tag**,
Try joining again using the invite link 🥰
 **I'll Approve Your Request!** 😉
||/help|| 🌝
"""

            try:
                await client.send_message(m.from_user.id, reject_text, disable_web_page_preview=True)
                await client.send_sticker(
                    m.from_user.id,
                    "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ"
                )
            except (UserNotMutualContact, PeerIdInvalid):
                pass
            except Exception as e:
                logger.error(f"Failed to send rejection to {m.from_user.id}: {e}")

    except Exception as e:
        logger.error(f"Error processing join request for {m.from_user.id}: {e}")
