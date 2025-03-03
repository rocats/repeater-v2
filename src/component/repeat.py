import unicodedata
import sys
import os
import random

from collections import defaultdict
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext
from tool.loader import char_lib, animation_lib, sticker_lib, channel_lib

from component.text_converter import tc


punctuations = "".join(
    list(
        chr(i)
        for i in range(sys.maxunicode)
        if unicodedata.category(chr(i)).startswith("P")
    )
)
last_text = defaultdict(str)
last_sender = defaultdict(int)
cnt = defaultdict(int)
repeated = defaultdict(bool)


def strip_punctuation(s: str):
    return s.strip(punctuations)


def repeat(update: Update, context: CallbackContext):
    global last_text, repeated, cnt
    chat_id = str(update.message.chat.id)
    rand = random.randint(0, int(os.getenv("RAND_UPPER_LIMIT", 10)))

    print(update.message)

    # --- sticker  --- #
    if update.message.sticker is not None:
        sticker_uid = (
            update.message.sticker.file_unique_id
            if update.message.sticker != None
            else ""
        )

        # repeat target sticker
        if sticker_uid in sticker_lib:
            context.bot.send_sticker(
                chat_id=chat_id,
                sticker=update.message.sticker.file_id,
            )

    # --- animation  --- #
    if update.message.animation is not None:
        animation_uid = (
            update.message.animation.file_unique_id
            if update.message.animation != None
            else ""
        )

        # repeat target animation
        if animation_uid in animation_lib:
            context.bot.send_animation(
                chat_id=chat_id,
                animation=update.message.animation.file_id,
            )

    # --- message --- #
    if (
        update.message is None
        or update.message.text is None
        or update.message.from_user is None
    ):
        return
    if len(update.message.text) > 50:
        # do not flood
        return
    if update.message.sender_chat is not None:
        # ignore messages sent on behalf of a channel
        return

    t = update.message.text.strip()
    e = update.message.entities
    f = update.message.from_user.id
    is_traditional = tc.check_traditional(update.message.text)

    # convert traditional char to simplified char
    # only when text_convert is set to t2s for limited channels
    if chat_id in [item["uid"] for item in channel_lib]:
        channel = list(filter(lambda x: x["uid"] == chat_id, channel_lib))
        if len(channel) > 0:
            if is_traditional and (channel[0]["text_convert"] == "t2s"):
                t = tc.convert(t)
    # repeat target text
    if "我" in t and "你" in t:
        t = t.replace("你", "他").replace("我", "你")
    elif "我" in t:
        t = t.replace("我", "你")
    if len([True for char in char_lib if char in t]) > 0:
        repeated[chat_id] = True
        context.bot.send_message(chat_id=chat_id, text=t)
    # repeat with self
    if "复读" in update.message.text:
        repeated[chat_id] = True
        t = t.replace("你", "我")
        t = t.replace("机", "鹅")
        context.bot.send_message(chat_id=chat_id, text=t * 3)
    # repeat 3 times with "!"
    elif 1 <= len(update.message.text) <= 30 and (
        update.message.text.endswith("！") or update.message.text.endswith("!")
    ):
        repeated[chat_id] = True
        context.bot.send_message(chat_id=chat_id, text=(strip_punctuation(t) + "！") * 3)
    # repeat 3 times with "～"
    elif 1 <= len(update.message.text) <= 30 and (
        update.message.text.endswith("～") or update.message.text.endswith("~")
    ):
        repeated[chat_id] = True
        context.bot.send_message(chat_id=chat_id, text=((t + " ") * 3))
    # repeat with "..."
    elif 1 <= len(update.message.text) <= 30 and (
        update.message.text.endswith("...") or update.message.text.endswith("。。。")
    ):
        repeated[chat_id] = True
        context.bot.send_message(chat_id=chat_id, text=t)
    # repeat with "???"
    elif 1 <= len(update.message.text) <= 30 and (
        update.message.text.endswith("??")
        or update.message.text.endswith("???")
        or update.message.text.endswith("？？")
        or update.message.text.endswith("？？？")
    ):
        repeated[chat_id] = True
        context.bot.send_message(chat_id=chat_id, text=t)
    # repeat as follower
    elif (
        f != last_sender[chat_id]
        and update.message.text == last_text[chat_id]
        and cnt[chat_id] >= 1
        and not repeated[chat_id]
    ):
        repeated[chat_id] = True
        context.bot.send_message(chat_id=chat_id, text=t, entities=e)
    last_sender[chat_id] = f
    # repeat text if it wins the lottery
    if rand == int(os.getenv("LUCKY_NUMBER", 0)) and not repeated[chat_id]:
        repeated[chat_id] = True
        context.bot.send_message(chat_id=chat_id, text=t)
    if update.message.text != last_text[chat_id]:
        last_text[chat_id] = update.message.text
        cnt[chat_id] = 1
        repeated[chat_id] = False
    else:
        cnt[chat_id] += 1


# def clean_repeat(update: Update):
#     chat_id = update.effective_chat.id
#     last_text[chat_id] = ""
