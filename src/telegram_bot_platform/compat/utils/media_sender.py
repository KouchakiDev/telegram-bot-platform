import telebot
from telebot.types import InputMediaPhoto, InputMediaVideo
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger
import inspect
import json
from telegram_bot_platform.compat.utils.location_utils import get_location_details
from telegram_bot_platform.compat.config.settings import MESSAGES
log = CustomLogger("media_sender.log")


class MediaSender:
    def __init__(self, bot: telebot.TeleBot):
        log.info(
            f"Function '{inspect.currentframe().f_code.co_name}' executed.")
        self.bot = bot
        self.media_methods = {
            'photo': self.send_photo,
            'video': self.send_video,
            'animation': self.send_animation,
            'audio': self.send_audio,
            'voice': self.send_voice,
            'document': self.send_document,
            'sticker': self.send_sticker,
            'video_note': self.send_video_note,
            'location': self.send_location,
            'contact': self.send_contact,
            'poll': self.send_poll,
            'dice': self.send_dice,
            'media_group': self.send_media_group,
        }

    def send_photo(self, chat_id, photo, caption=None, reply_markup=None):
        self._safe_send(self.bot.send_photo, chat_id,
                        photo, caption, reply_markup)

    def send_video(self, chat_id, video, caption=None, reply_markup=None):
        self._safe_send(self.bot.send_video, chat_id,
                        video, caption, reply_markup)

    def send_animation(self, chat_id, animation, caption=None, reply_markup=None):
        self._safe_send(self.bot.send_animation, chat_id,
                        animation, caption, reply_markup)

    def send_audio(self, chat_id, audio, caption=None, reply_markup=None):
        self._safe_send(self.bot.send_audio, chat_id,
                        audio, caption, reply_markup)

    def send_voice(self, chat_id, voice, caption=None, reply_markup=None):
        self._safe_send(self.bot.send_voice, chat_id,
                        voice, caption, reply_markup)

    def send_document(self, chat_id, document, caption=None, reply_markup=None):
        self._safe_send(self.bot.send_document, chat_id,
                        document, caption, reply_markup)

    def send_sticker(self, chat_id, sticker, reply_markup=None):
        self._safe_send(self.bot.send_sticker, chat_id,
                        sticker, None, reply_markup)

    def send_video_note(self, chat_id, video_note, reply_markup=None):
        try:
            self.bot.send_video_note(chat_id, video_note)
            log.info(
                f"Video note sent successfully to chat {chat_id} with message_id {video_note}.")

        except Exception as e:
            log.error(
                f"Unexpected error sending video note to chat {chat_id}: {e}")

    def send_location(self, chat_id, location, reply_markup=None):
        try:
            if isinstance(location, str):
                location = json.loads(location)
                location_details = get_location_details(
                    int(location['latitude']), int(location['longitude']))
                province = location_details['province']
                city = location_details['city']
                area = location_details['area'].replace(",", " - ")
            self.bot.send_location(chat_id, int(location['latitude']), int(
                location['longitude']), reply_markup=reply_markup)
            self.bot.send_message(chat_id, MESSAGES["loc_address"].format(
                pro=province, cit=city, are=area))

        except Exception as e:
            log.error(f"Error sending location to chat {chat_id}: {e}")
        else:
            log.info(f"Location sent successfully to chat {chat_id}.")

    def send_contact(self, chat_id, phone_number, first_name, last_name=None, reply_markup=None):
        try:
            self.bot.send_contact(
                chat_id, phone_number, first_name, last_name, reply_markup=reply_markup)
        except Exception as e:
            log.error(f"Error sending contact to chat {chat_id}: {e}")
        else:
            log.info(f"Contact sent successfully to chat {chat_id}.")

    def send_poll(self, chat_id, question, options, reply_markup=None):
        try:
            self.bot.send_poll(chat_id, question, options,
                               reply_markup=reply_markup)
        except Exception as e:
            log.error(f"Error sending poll to chat {chat_id}: {e}")
        else:
            log.info(f"Poll sent successfully to chat {chat_id}.")

    def send_dice(self, chat_id, emoji='🎲', reply_markup=None):
        try:
            self.bot.send_dice(chat_id, emoji=emoji, reply_markup=reply_markup)
        except Exception as e:
            log.error(f"Error sending dice to chat {chat_id}: {e}")
        else:
            log.info(f"Dice sent successfully to chat {chat_id}.")
            
    def send_media_group(self, chat_id, media_list):
        """Legacy-compatible behavior preserved for this callable."""

        try:
            if isinstance(media_list, str):
                try:
                    media_list = json.loads(media_list)
                except json.JSONDecodeError:
                    log.error("❌ media_list string is not valid JSON.")
                    return
            # Internal implementation note: legacy behavior is preserved during modernization.
            prepared_media = []

            for item in media_list:
                # Internal implementation note: legacy behavior is preserved during modernization.
                if isinstance(item, str):
                    prepared_media.append(InputMediaPhoto(media=item.strip()))
                # Internal implementation note: legacy behavior is preserved during modernization.
                elif isinstance(item, (tuple, list)) and len(item) == 3:
                    media_type, media_file, caption = item
                    if media_type == 'photo':
                        prepared_media.append(InputMediaPhoto(media_file.strip(), caption=caption))
                    elif media_type == 'video':
                        prepared_media.append(InputMediaVideo(media_file.strip(), caption=caption))
                    else:
                        log.warning(f"❌ Unsupported media type: {media_type}")
                else:
                    log.warning(f"⚠️ Invalid media entry: {item}")

            # Internal implementation note: legacy behavior is preserved during modernization.
            if not prepared_media:
                self.bot.send_message(chat_id, "❌ هیچ مدیایی برای ارسال وجود ندارد.")
                return

            # Internal implementation note: legacy behavior is preserved during modernization.
            if len(prepared_media) == 1:
                media = prepared_media[0]
                if isinstance(media, InputMediaPhoto):
                    self.bot.send_photo(chat_id, media.media, caption=media.caption)
                elif isinstance(media, InputMediaVideo):
                    self.bot.send_video(chat_id, media.media, caption=media.caption)
            else:
                self.bot.send_media_group(chat_id, prepared_media)

        except Exception as e:
            log.error(f"❌ Error sending media group to chat {chat_id}: {e}")
        else:
            log.info(f"✅ Media group sent successfully to chat {chat_id}")

    def send_by_auto_detect(self, chat_id, file_id, caption=None, reply_markup=None):
        for media_type, send_method in self.media_methods.items():
            if media_type in ['location', 'contact', 'poll', 'dice', 'media_group']:
                continue
            try:
                sig = inspect.signature(send_method)
                params = {'chat_id': chat_id}
                file_param = list(sig.parameters.keys())[1]
                params[file_param] = file_id
                if 'caption' in sig.parameters and caption:
                    params['caption'] = caption
                if 'reply_markup' in sig.parameters and reply_markup:
                    params['reply_markup'] = reply_markup
                log.debug(
                    f"Attempting to send '{file_id}' as '{media_type}' to chat {chat_id}...")
                message = send_method(**params)
                log.info(
                    f"✅ Successfully sent file_id '{file_id}' as '{media_type}' to chat {chat_id} with message_id {message.message_id}.")
                return True
            except telebot.apihelper.ApiException as e:
                log.warning(
                    f"⚠️ Failed sending '{file_id}' as '{media_type}' to chat {chat_id}: {e}")
                continue
            except Exception as e:
                log.error(
                    f"❌ Unexpected error sending '{file_id}' as '{media_type}' to chat {chat_id}: {e}")
                continue
        log.error(
            f"❌ All attempts failed to send file_id '{file_id}' to chat {chat_id}.")
        return False

    def _safe_send(self, send_func, chat_id, file_or_media, caption=None, reply_markup=None):
        try:
            sig = inspect.signature(send_func)
            params = {'chat_id': chat_id}
            file_param = list(sig.parameters.keys())[1]
            params[file_param] = file_or_media
            if 'caption' in sig.parameters and caption:
                params['caption'] = caption
            if 'reply_markup' in sig.parameters and reply_markup:
                params['reply_markup'] = reply_markup
            result = send_func(**params)
            if result:
                log.info(
                    f"{send_func.__name__.replace('send_', '').capitalize()} sent successfully to chat {chat_id} with message_id {result.message_id}.")
            else:
                log.warning(
                    f"{send_func.__name__.replace('send_', '').capitalize()} sent to chat {chat_id} but no result returned.")
            return result
        except telebot.apihelper.ApiException as e:
            log.error(
                f"Error sending via '{send_func.__name__}' to chat {chat_id}: {e}")
            raise
        except Exception as e:
            log.error(
                f"Unexpected error in '{send_func.__name__}' to chat {chat_id}: {e}")
            raise

    def get_method(self, media_type: str):
        """
        Retrieve a specific send method by media type.

        :param media_type: The type of media (e.g., 'photo', 'video').
        :return: The corresponding send method if available, otherwise None.
        """
        return self.media_methods.get(media_type)
