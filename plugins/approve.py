from pyrogram.errors import UserNotMutualContact, PeerIdInvalid
import random

@Client.on_chat_join_request()
async def approve_new(client, m: ChatJoinRequest):
    global NEW_REQ_MODE
    if not NEW_REQ_MODE:
        return

    try:
        user = await client.get_chat(m.from_user.id)
        bio = user.bio or ""

        # Required tags (case-insensitive)
        required_tags = [
            "@real_pirates",
            "@drama_loverx",
            "@ii_way_to_success_ii",
            "@myownsuccess",
            "@goal_achieverr",
            "@just_vibing_alone"
        ]

        # Stickers list
        stickers = [
            "CAACAgUAAxkBAAKcLmf-E2SXmiXe99nF5KuHMMbeBsEoAALbHAACocj4Vkl1jIJ0iWpmHgQ",
            "CAACAgUAAxkBAAKcH2f94mJ3mIfgQeXmv4j0PlEpIgYMAAJvFAACKP14V1j51qcs1b2wHgQ",
            "CAACAgUAAxkBAAJLXmf2ThTMZwF8_lu8ZEwzHvRaouKUAAL9FAACiFywV69qth3g-gb4HgQ"
        ]

        if any(tag in bio.lower() for tag in required_tags):
            # ✅ Approve join request
            await client.approve_chat_join_request(m.chat.id, m.from_user.id)
            
            chat_info = await client.get_chat(m.chat.id)
            member_count = chat_info.members_count

            approve_text = f"""🔓 <b>Access Granted ✅</b>

<b><blockquote> Cheers, <a href='https://t.me/+H9WC0vSGAVA0MWFl'>{m.from_user.first_name}</a>! 🥂</blockquote></b>  
Your Request To Join <b><blockquote>{m.chat.title}</blockquote></b> Has Been Approved! 🎉  
You are the <b>#{member_count:,}</b> member in this channel. 🚀  
We’re happy to have you with us. 🥰

⚠️⚠️⚠️  
<b><i>||If you remove that Tag from your bio, you will be removed from the channel. 💀||  
This tag is required to remain a verified member of {m.chat.title}.  
Make sure to keep it in your Bio to avoid removal. 😉</i></b>  
<blockquote>Supported by <b>💀 @Real_Pirates 🏴‍☠️</b></blockquote>"""

            approved = False

            # ✅ Send message and sticker to user
            try:
                await client.send_message(m.from_user.id, approve_text)
                await client.send_sticker(m.from_user.id, random.choice(stickers))
            except Exception as e:
                print(f"❌ Error sending message or sticker to user: {e}")

            # ✅ Send message and sticker to log channel
            try:
                await client.send_message(-1002326947174, approve_text)
                await client.send_sticker(-1002326947174, random.choice(stickers))
                approved = True
            except Exception as e:
                print(f"❌ Error sending message or sticker to log channel: {e}")

            if approved:
                return

        # ❌ Reject if not approved
        await client.decline_chat_join_request(m.chat.id, m.from_user.id)

        # 🔒 Send rejection message and sticker
        try:
            await client.send_message(
                m.from_user.id,
                f"""🔒 **Access Denied** ❌  
**{m.from_user.mention}**

Join Any **Request to Join Channel**, in Just **2 Simple Steps** 🤫

🔹 **Step 1️⃣**  
Add **Any One Tag** in your bio from the options below: 👇

To Join
🎬 **Movie Channel:**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰  
• `@Real_Pirates`  
• `@Drama_Loverx`

To Join
📚 **Study / Skills Channel:**
⊱─‌─‌─‌─‌──‌─‌─‌─‌─‌─‌─‌─‌─‌⊰  
• `@II_Way_to_Success_II`  
• `@MyOwnSuccess`  
• `@Just_Vibing_Alone`  
_Tap to Copy ↑_

🔹 **Step 2️⃣**  
Try Joining Again Using The Invite Link. 🥰  
After updating your bio with a required tag —  
**I'll be happy to approve your request!** 😉

||/start|| 🌝
"""
            )
            await client.send_sticker(
                m.from_user.id,
                random.choice(stickers)
            )
        except (UserNotMutualContact, PeerIdInvalid):
            pass
        except Exception as e:
            print(f"❌ Error sending rejection message or sticker: {e}")

    except Exception as e:
        print(f"⚠️ General error in join request: {e}")
