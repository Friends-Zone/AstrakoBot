from emoji import UNICODE_EMOJI
from google_trans_new import LANGUAGES, google_translator
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, run_async

from AstrakoBot import dispatcher
from AstrakoBot.modules.disable import DisableAbleCommandHandler
from AstrakoBot.modules.helper_funcs.misc import delete
from AstrakoBot.modules.sql.clear_cmd_sql import get_clearcmd


def totranslate(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    text = ""
    problem_lang_code = [key for key in LANGUAGES if "-" in key]
    try:
        if message.reply_to_message:
            args = update.effective_message.text.split(None, 1)
            if message.reply_to_message.text:
                text = message.reply_to_message.text
            elif message.reply_to_message.caption:
                text = message.reply_to_message.caption

            try:
                source_lang = args[1].split(None, 1)[0]
            except (IndexError, AttributeError):
                source_lang = "en"

        else:
            args = update.effective_message.text.split(None, 2)
            text = args[2]
            source_lang = args[1]

        if source_lang.count("-") == 2:
            for lang in problem_lang_code:
                if lang in source_lang:
                    if source_lang.startswith(lang):
                        dest_lang = source_lang.rsplit("-", 1)[1]
                        source_lang = source_lang.rsplit("-", 1)[0]
                    else:
                        dest_lang = source_lang.split("-", 1)[1]
                        source_lang = source_lang.split("-", 1)[0]
        elif source_lang.count("-") == 1:
            for lang in problem_lang_code:
                if lang in source_lang:
                    dest_lang = source_lang
                    source_lang = None
                    break
            if dest_lang is None:
                dest_lang = source_lang.split("-")[1]
                source_lang = source_lang.split("-")[0]
        else:
            dest_lang = source_lang
            source_lang = None

        exclude_list = UNICODE_EMOJI.keys()
        for emoji in exclude_list:
            if emoji in text:
                text = text.replace(emoji, "")

        trl = google_translator()
        if source_lang is None:
            detection = trl.detect(text)
            trans_str = trl.translate(text, lang_tgt=dest_lang)
            delmsg = message.reply_text(
                f"Translated from `{detection[0]}` to `{dest_lang}`:\n`{trans_str}`",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            trans_str = trl.translate(text, lang_tgt=dest_lang, lang_src=source_lang)
            delmsg = message.reply_text(
                f"Translated from `{source_lang}` to `{dest_lang}`:\n`{trans_str}`",
                parse_mode=ParseMode.MARKDOWN,
            )

        deletion(update, context, delmsg)

    except IndexError:
        delmsg = update.effective_message.reply_text(
            "Reply to messages or write messages from other languages ​​for translating into the intended language\n\n"
            "Example: `/tr en-ml` to translate from English to Malayalam\n"
            "Or use: `/tr ml` for automatic detection and translating it into Malayalam.\n"
            "See [List of Language Codes](t.me/OnePunchSupport/12823) for a list of language codes.",
            parse_mode="markdown",
            disable_web_page_preview=True,
        )
        deletion(update, context, delmsg)
    except ValueError:
        delmsg = update.effective_message.reply_text("The intended language is not found!")
        deletion(update, context, delmsg)
    else:
        return


def deletion(update: Update, context: CallbackContext, delmsg):
    chat = update.effective_chat
    if cleartime := get_clearcmd(chat.id, "tr"):
        context.dispatcher.run_async(delete, delmsg, cleartime.time)


__help__ = """
• `/tr` or `/tl` (language code) as reply to a long message
*Example:* 
  `/tr en`*:* translates something to english
  `/tr hi-en`*:* translates hindi to english
"""

TRANSLATE_HANDLER = DisableAbleCommandHandler(["tr", "tl"], totranslate, run_async=True)

dispatcher.add_handler(TRANSLATE_HANDLER)

__mod_name__ = "Translator"
__command_list__ = ["tr", "tl"]
__handlers__ = [TRANSLATE_HANDLER]
