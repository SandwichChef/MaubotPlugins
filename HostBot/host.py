# HostBot - A Maubot plugin that simply takes a URL and rehosts it on Matrix
# Derivative of httpcat - A maubot that posts http.cats on request. Copyright (C) 2020 Tulir Asokan
# To be reimplemented in a way that doesn't use his method, and under a more permissive license
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Dict, Type, Optional
from io import BytesIO
import asyncio

from aiohttp import ClientResponseError

from PIL import Image
from mimetypes import guess_extension

from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from mautrix.types import MediaMessageEventContent, MessageType, ImageInfo

from maubot import Plugin, MessageEvent
from maubot.handlers import command


class HostBot(Plugin):

    async def _reupload(self, message: str) -> Optional[MediaMessageEventContent]:
        url = message
        self.log.info(f"Reuploading {url}")
        resp = await self.http.get(url, headers={"Referer": url})
        data = await resp.read()
        img = Image.open(BytesIO(data))
        width, height = img.size
        mimetype = Image.MIME[img.format]
        filename = f"{message}{guess_extension(mimetype)}"
        mxc = await self.client.upload_media(data, mimetype, filename=filename)
        return MediaMessageEventContent(msgtype=MessageType.IMAGE, body=filename, url=mxc,
                                        info=ImageInfo(mimetype=mimetype, size=len(data),
                                                       width=width, height=height))

    @command.new("gallanthost", help="Rehost an image")
    @command.argument("message", pass_raw=True)
    async def echo_handler(self, evt: MessageEvent, message: str) -> None:
        pic = await self._reupload(message)
        await evt.respond(pic)
