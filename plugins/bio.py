import random
import logging
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from pyrogram.errors import UserNotMutualContact, PeerIdInvalid, ChatAdminRequired

# Load .env variables
load_dotenv()
NEW_REQ_MODE = os.getenv("NEW_REQ_MODE", "True").lower() == "true"
LOG_GROUP = int(os.getenv("LOG_GROUP", "0"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required tag map: hashtags in channel → tags needed in user bio
TAG_MAP = {
    "#movie": ["@real_pirates", "@drama_loverx"],
    "#drama": ["@drama_loverx"],
    "#study": ["@ii_way_to_success_ii"],
    "#success": ["@myownsuccess", "@drama_loverx"],
    "#goal": ["@goal_achieverr"],
    "#alone": ["@just_vibing_alone"],
}

def get_required_tags_from_description(description: str) -> list:
    """Extract required tags based on hashtags in the description."""
    description = description.lower()
    required_tags = []
    for hashtag, tags in TAG_MAP.items():
        if hashtag in description:
            required_tags.extend(tags)
    return list(dict.fromkeys(required_tags))  # remove duplicates

def has_required_tag_in_bio(user_bio: str, required_tags: list) -> bool:
    """Check if user's bio has any of the required tags."""
    if not user_bio or not required_tags:
        return False
    user_bio = user_bio.lower()
    return any(tag.lower() in user_bio for tag in required_tags)

async def handle_join_request(client: Client, m: ChatJoinRequest):
    """Main function to handle incoming join requests."""
    if not NEW_REQ_MODE:
        logger.info("NEW_REQ_MODE is disabled.")
        return

    try:
        chat = await client.get_chat(m.chat.id)
        description = chat.description or ""
        required_tags = get_required_tags_from_description(description)

        if not required_tags:
            logger.info(f"No required tags for chat {chat.id}")
            return

        try:
            user = await client.get_chat(m.from_user.id)
            bio = user.bio or ""
        except Exception as e:
            logger.warning(f"Failed to fetch bio of user {m.from_user.id}: {e}")
            bio = ""

        # Create invite link
        try:
            invite = await client.create_chat_invite_link(
                chat_id=m.chat.id,
                name=f"Join {chat.title}",
                creates_join_request=True
            )
            invite_link = invite.invite_link
        except ChatAdminRequired:
            logger.error("Bot lacks permission to create invite link.")
            return
        except Exception as e:
            logger.error(f"Failed to create invite link: {e}")
            return

        if has_required_tag_in_bio(bio, required_tags):
            await client.approve_chat_join_request(m.chat.id, m.from_user.id)

            full_name = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()
            member_count = chat.members_count

            approve_text = (
                f"🔓 <b>Access Granted ✅</b>\n\n"
                f"<blockquote>Cheers, <a href='https://t.me/Real_Pirates'>{full_name}</a>! 🥂</blockquote>\n"
                f"You’re approved to join <a href='{invite_link}'><b>{chat.title}</b></a> 🎉\n"
                f"💎 <b>Members Count:</b> {member_count:,} 🚀\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ <b>Keep this tag in your bio:</b> <code>{', '.join(required_tags)}</code>\n"
                f"If removed, you might get kicked. 💀\n\n"
                f"<i>Supported by</i> ➩ <b>@Real_Pirates 🏴‍☠️</b>"
            )

            stickers = [
                "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ",
                "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ",
                "CAACAgUAAxkBAAKcM2f-FX9lZ6z3z8kJ9fT2bV5qN7kAAALcHAACocj4Vkl1jIJ0iWpmHgQ"
            ]

            try:
                await client.send_message(m.from_user.id, approve_text, disable_web_page_preview=True)
                await asyncio.sleep(0.5)
                await client.send_sticker(m.from_user.id, random.choice(stickers))
            except Exception as e:
                logger.error(f"Failed to DM approved user: {e}")

            if LOG_GROUP:
                try:
                    await client.send_message(LOG_GROUP, approve_text, disable_web_page_preview=True)
                    await asyncio.sleep(0.5)
                    await client.send_sticker(LOG_GROUP, random.choice(stickers))
                except Exception as e:
                    logger.error(f"Failed to log approval: {e}")

        else:
            await client.decline_chat_join_request(m.chat.id, m.from_user.id)

            reject_text = (
                f"🔒 <b>Access Denied ❌</b>\n\n"
                f"Hi {m.from_user.mention}, to join <b>{chat.title}</b>, you must:\n\n"
                f"1️⃣ Add one of these tags to your bio:\n<code>{', '.join(required_tags)}</code>\n\n"
                f"2️⃣ Rejoin using this link:\n<a href='{invite_link}'>Join {chat.title}</a>\n\n"
                f"<i>I'll auto-approve you after that!</i> 😉\n"
            )

            stickers = [
                "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
                "CAACAgUAAxkBAAKcN2f-GH8kZ7y4z9lK0fU3cW6qO8kAAALdHAACocj4Vkl1jIJ0iWpmHgQ",
                "CAACAgUAAxkBAAKcO2f-HI9lZ8z5z0mL1fV4dX7qP9kAAALeHAACocj4Vkl1jIJ0iWpmHgQ"
            ]

            try:
                await client.send_message(m.from_user.id, reject_text, disable_web_page_preview=True)
                await asyncio.sleep(0.5)
                await client.send_sticker(m.from_user.id, random.choice(stickers))
            except (UserNotMutualContact, PeerIdInvalid):
                logger.info(f"Cannot send message to user {m.from_user.id}")
            except Exception as e:
                logger.error(f"Failed to DM rejected user: {e}")

    except Exception as e:
        logger.error(f"Error in join request for user {m.from_user.id}: {e}")
