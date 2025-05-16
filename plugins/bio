import random
import logging
import asyncio
import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from pyrogram.errors import UserNotMutualContact, PeerIdInvalid, ChatAdminRequired

# Load environment variables
load_dotenv()

# Map hashtags in channel description to lists of required @tags in user bio
TAG_MAP = {
    "#movie": ["@real_pirates", "@drama_loverx"],  # #movie allows either tag
    "#drama": ["@drama_loverx"],
    "#study": ["@ii_way_to_success_ii"],
    "#success": ["@myownsuccess", "@drama_loverx"],  # #success allows either tag
    "#goal": ["@goal_achieverr"],
    "#alone": ["@just_vibing_alone"],
}

def get_required_tags_from_description(description: str) -> list:
    """Extract required tags based on hashtags in the channel description."""
    description = description.lower()
    required_tags = []
    for hashtag, tags in TAG_MAP.items():
        if hashtag in description:
            required_tags.extend(tags)
    # Remove duplicates while preserving order
    return list(dict.fromkeys(required_tags))

def has_required_tag_in_bio(user_bio: str, required_tags: list) -> bool:
    """Check if the user's bio contains at least one required tag."""
    if not user_bio or not required_tags:
        return False
    user_bio = user_bio.lower()
    return any(tag.lower() in user_bio for tag in required_tags)

async def handle_join_request(client: Client, m: ChatJoinRequest):
    """Handle incoming chat join requests based on user bio tags."""
    if not NEW_REQ_MODE:
        logger.info("NEW_REQ_MODE is disabled, skipping join request handling.")
        return

    try:
        chat = await client.get_chat(m.chat.id)
        description = chat.description or ""
        required_tags = get_required_tags_from_description(description)

        if not required_tags:
            logger.info(f"No required tags found for chat {chat.id}")
            return

        # Fetch user bio with error handling for privacy restrictions
        try:
            user = await client.get_chat(m.from_user.id)
            bio = user.bio or ""
        except Exception as e:
            logger.warning(f"Could not fetch bio for user {m.from_user.id}: {e}")
            bio = ""

        # Create invite link
        try:
            invite_link_obj = await client.create_chat_invite_link(
                chat_id=m.chat.id,
                name=f"Join {chat.title}",
                creates_join_request=True
            )
            invite_link = invite_link_obj.invite_link
        except ChatAdminRequired:
            logger.error(f"Bot lacks admin privileges to create invite link for chat {m.chat.id}")
            return
        except Exception as e:
            logger.error(f"Failed to create invite link for chat {m.chat.id}: {e}")
            return

        if has_required_tag_in_bio(bio, required_tags):
            # Approve join request
            await client.approve_chat_join_request(m.chat.id, m.from_user.id)

            full_name = f"{m.from_user.first_name or ''} {m.from_user.last_name or ''}".strip()
            member_count = chat.members_count

            approve_text = (
                f"🔓 <b>Access Granted ✅</b>\n\n"
                f"<b><blockquote> Cheers, <a href='https://t.me/Real_Pirates'>{full_name}</a> ! 🥂</blockquote></b>\n"
                f"Your Request To Join <b><a href='{invite_link}'> {chat.title} </a></b> Has Been Approved! 🎉\n"
                f"We’re happy to have you with us. 🥰\n\n"
                f"💎 𝐌𝐞𝐦𝐛𝐞𝐫𝐬 𝐂𝐨𝐮𝐧𝐭: <b>{member_count:,}</b> 🚀\n"
                f"┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌┉‌‌\n"
                f"⚠️⚠️⚠️\n"
                f"<b><i>||If you remove the tag(s) {', '.join(required_tags)} from your bio, you will be removed from the channel. 💀||\n"
                f"These tags are required to remain a verified member of ≫  {chat.title}.\n"
                f"Make sure to keep at least one in your Bio to avoid removal. 😉</i></b>\n"
                f"<blockquote>Supported by <b>➩ @Real_Pirates 🏴‍☠️</b></blockquote>"
            )

            approval_stickers = [
                "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ",
                "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ",
                "CAACAgUAAxkBAAKcM2f-FX9lZ6z3z8kJ9fT2bV5qN7kAAALcHAACocj4Vkl1jIJ0iWpmHgQ"
            ]

            # Send approval message to user
            try:
                await client.send_message(m.from_user.id, approve_text, disable_web_page_preview=True, parse_mode="html")
                await asyncio.sleep(0.5)  # Avoid rate limits
                await client.send_sticker(m.from_user.id, random.choice(approval_stickers))
            except Exception as e:
                logger.error(f"Failed to send approval to {m.from_user.id}: {e}")

            # Send log message
            if LOG_GROUP:
                try:
                    await client.send_message(LOG_GROUP, approve_text, disable_web_page_preview=True, parse_mode="html")
                    await asyncio.sleep(0.5)
                    await client.send_sticker(LOG_GROUP, random.choice(approval_stickers))
                except Exception as e:
                    logger.error(f"Failed to send log message to {LOG_GROUP}: {e}")

        else:
            # Decline join request
            await client.decline_chat_join_request(m.chat.id, m.from_user.id)

            reject_text = (
                f"🔒 **Access Denied** ❌\n\n"
                f"Dear **{m.from_user.mention}** 🌝\n\n"
                f"To join <b>{chat.title}</b>, follow these **2 Simple Steps**: 🤫\n\n"
                f"🔹 **Step 1️⃣**\n"
                f"<b>Add one of these tags in your bio</b>: <code>{', '.join(required_tags)}</code> ✅\n\n"
                f"🔹 **Step 2️⃣**\n"
                f"After updating your bio, try joining again using the invite link: <a href='{invite_link}'>Join {chat.title}</a>.  \n"
                f"**I'll approve your request!** 😉\n\n"
                f"||/help|| 🌝"
            )

            rejection_stickers = [
                "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
                "CAACAgUAAxkBAAKcN2f-GH8kZ7y4z9lK0fU3cW6qO8kAAALdHAACocj4Vkl1jIJ0iWpmHgQ",
                "CAACAgUAAxkBAAKcO2f-HI9lZ8z5z0mL1fV4dX7qP9kAAALeHAACocj4Vkl1jIJ0iWpmHgQ"
            ]

            try:
                await client.send_message(m.from_user.id, reject_text, disable_web_page_preview=True, parse_mode="html")
                await asyncio.sleep(0.5)
                await client.send_sticker(m.from_user.id, random.choice(rejection_stickers))
            except (UserNotMutualContact, PeerIdInvalid):
                logger.info(f"User {m.from_user.id} is not a mutual contact or invalid peer, skipping rejection message.")
            except Exception as e:
                logger.error(f"Failed to send rejection to {m.from_user.id}: {e}")

    except Exception as e:
        logger.error(f"Error processing join request for user {m.from_user.id}: {e}")
