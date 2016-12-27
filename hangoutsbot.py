#!/usr/bin/env python3

import logging
import asyncio
import re
import sys
import hangups

import settings

from models.user import User
from models.conversation import Conversation
from models.message import Message
from models.command import Command
from models.hook import Hook

from utils.commands import register_commands
from utils.hooks import register_hooks
from utils.enums import EventType, ConversationType
from utils.textutils import spacing

from services.lastfm import Lastfm
from services.gmusic import Gmusic
from services.setlistfm import Setlistfm

from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(name)s - %(levelname)s: %(asctime)s | %(message)s")
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)


class HangoutsBot(object):

    def __init__(self):
        self.command_matcher = re.compile(settings.COMMAND_MATCH_REGEX)
        register_commands()
        register_hooks()
        self.client = hangups.client.Client(self.login())
        self.user = User.get_or_create(id=settings.BOT_ID, defaults={'first_name': settings.BOT_FIRST_NAME, 'last_name': settings.BOT_LAST_NAME})[0]
        self.hooks = Hook.select()
        self.lastfm = Lastfm(self,
                             settings.LAST_API_KEY,
                             settings.LAST_API_SECRET,
                             settings.LAST_USER,
                             settings.LAST_PASS_HASH)
        self.gmusic = Gmusic(self)
        self.gmusic.login(settings.GMUSIC_USER, settings.GMUSIC_PASS)
        self.setlistfm = Setlistfm(self)

    def login(self):
        return hangups.auth.get_auth_stdin(settings.COOKIES_FILE_PATH)

    def run(self):
        logger.debug(self.client)
        self.client.on_state_update.add_observer(self.handle_update)
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.client.connect())
        except KeyboardInterrupt:
            sys.exit(0)

    @asyncio.coroutine
    def handle_update(self, state_update):
        logger.debug("Handling event update")
        if state_update.event_notification.event.event_type == EventType.EVENT_TYPE_REGULAR_CHAT_MESSAGE.value:
            yield from self.handle_message(state_update)
        elif state_update.event_notification.event.event_type == EventType.EVENT_TYPE_CONVERSATION_RENAME.value:
            yield from self.handle_rename(state_update)
        elif state_update.event_notification.event.event_type == EventType.EVENT_TYPE_REMOVE_USER.value:
            yield from self.handle_user_removed(state_update)
        elif state_update.event_notification.event.event_type == EventType.EVENT_TYPE_ADD_USER.value:
            yield from self.handle_user_added(state_update)
        else:
            pass

    @asyncio.coroutine
    def handle_message(self, state_update):
        logger.debug("Handling message")
        conversation = self.get_or_create_conversation(state_update.conversation)
        if state_update.event_notification.event.sender_id.gaia_id == settings.BOT_ID:
            message = Message.create(conversation=conversation, user=self.user, text="".join(
                [seg.text for seg in state_update.event_notification.event.chat_message.message_content.segment]), time=datetime.now())
            message.conversation.logger.info(message.text.replace("\n", " "), extra={
                "username": message.user.username,
                "message_time": datetime.strftime(message.time, "%Y-%m-%d %X"),
            })
            return True
        sending_user = User.get(User.id == state_update.event_notification.event.sender_id.gaia_id)
        message_body = ""
        for seg in state_update.event_notification.event.chat_message.message_content.segment:
            message_body += seg.text
        message = Message.create(conversation=conversation, user=sending_user, text=message_body, time=datetime.now())
        message.conversation.logger.info(message.text.replace("\n", " "), extra={
            "username": message.user.username,
            "message_time": datetime.strftime(message.time, "%Y-%m-%d %X"),
        })
        matched = self.command_matcher.match(message.text)
        if matched:
            try:
                cmd_to_run = Command.get(name=matched.group(1).lower())
                yield from cmd_to_run.run(bot=self,
                                          conversation=message.conversation,
                                          user=message.user,
                                          args=message.text.split(matched.group(1), 1)[-1].split())
            except Command.DoesNotExist:
                pass
        for hook in self.hooks:
            matcher = re.compile(r"{}".format(hook.regex))
            if matcher.match(message.text):
                yield from hook.run(bot=self, conversation=message.conversation, user=message.user, text=message.text)
        return True

    @asyncio.coroutine
    def handle_rename(self, state_update):
        conversation = self.get_or_create_conversation(state_update.conversation)
        try:
            user = User.get(id=state_update.event_notification.event.sender_id.gaia_id)
        except User.DoesNotExist:
            user = self.create_user_from_id(state_update.event_notification.event.sender_id.gaia_id, state_update.conversation)
        new_name = state_update.event_notification.event.conversation_rename.new_name
        conversation.logger.info("{} changed topic to {}".format(user.username, new_name), extra={
            'username': "****",
            "message_time": datetime.strftime(datetime.now(), "%Y-%m-%d %X")
        })
        return True

    @asyncio.coroutine
    def handle_user_removed(self, state_update):
        conversation = self.get_or_create_conversation(state_update.conversation)
        removing_user = User.get(id=state_update.event_notification.event.sender_id.gaia_id)
        removed_user = User.get(id=state_update.event_notification.event.membership_change.participant_ids[0].gaia_id)
        conversation.members.remove(removed_user)
        conversation.logger.info("{} was kicked by {}".format(removed_user.username, removing_user.username), extra={
            "username": "****",
            "message_time": datetime.strftime(datetime.now(), "%Y-%m-%d %X")
        })
        return True

    @asyncio.coroutine
    def handle_user_added(self, state_update):
        conversation = self.get_or_create_conversation(state_update.conversation)
        self.check_conversation_participants(state_update.conversation)
        adding_user = User.get(id=state_update.event_notification.event.sender_id.gaia_id)
        added_user = User.get(id=state_update.event_notification.event.membership_change.participant_ids[0].gaia_id)
        conversation.logger.info("{} was added by {}".format(added_user.username, adding_user.username), extra={
            "username": "****",
            "message_time": datetime.strftime(datetime.now(), "%Y-%m-%d %X")
        })

    def create_user_from_id(self, user_id, conversation):
        logger.debug("Creating User with id {}".format(user_id))
        participant_object = None
        for participant in conversation.participant_data:
            if participant.id.gaia_id == user_id:
                participant_object = participant
                break
        name_split = participant_object.fallback_name.split(" ", 1)
        if len(name_split) > 1:
            user = User.create(id=user_id, first_name=name_split[0], last_name=name_split[1])
        else:
            user = User.create(id=user_id, first_name=name_split[0], last_name="")
        return user

    def get_or_create_conversation(self, conversation):
        return Conversation.get_or_create(id=conversation.conversation_id.id, defaults={
            'group': conversation.type == ConversationType.CONVERSATION_TYPE_GROUP.value
        })[0]

    def check_conversation_participants(self, conversation):
        logger.debug("Checking Conversation participants")
        conv = self.get_or_create_conversation(conversation)
        for participant in conversation.participant_data:
            try:
                user = User.get(User.id == participant.id.gaia_id)
            except User.DoesNotExist:
                user = self.create_user_from_id(participant.id.gaia_id, conversation)
            if user not in conv.members:
                logger.debug("Adding User {} to Conversation {}".format(user.id, conv.id))
                conv.members.add(user)
        return True

    @asyncio.coroutine
    def send_message(self, conversation, message, image_file=None, filter_to_use=None):
        if filter_to_use == "spacing":
            message = spacing(message)
        if image_file:
            image_id = yield from self.client.upload_image(image_file)
        else:
            image_id = None
        request = hangups.hangouts_pb2.SendChatMessageRequest(
            request_header=self.client.get_request_header(),
            event_request_header=hangups.hangouts_pb2.EventRequestHeader(
                conversation_id=hangups.hangouts_pb2.ConversationId(
                    id=conversation.id
                ),
                client_generated_id=self.client.get_client_generated_id(),
            ),
            message_content=hangups.hangouts_pb2.MessageContent(
                segment=[seg.serialize() for seg in hangups.ChatMessageSegment.from_str(message)],
            ),
        )
        if image_id:
            request.existing_media.photo.photo_id = image_id
        try:
            yield from self.client.send_chat_message(request)
        except hangups.exceptions.NetworkError:
            logger.error("Unable to send message to {} with text '{}'".format(conversation, message))


if __name__ == "__main__":
    print("Run the bot using the manage.py file: ./manage.py run")
