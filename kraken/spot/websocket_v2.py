#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# GitHub: https://github.com/btschwertfeger
#

"""
This module provides the Spot websocket client (Websocket API V2 as
documented in - https://docs.kraken.com/websockets-v2).
"""
from __future__ import annotations

import asyncio
import json

# import logging
# from copy import deepcopy
from typing import Any, Callable, List, Optional

from kraken.base_api import defined  # , ensure_string
from kraken.exceptions import KrakenException

# from kraken.spot.trade import Trade
from kraken.spot.websocket import KrakenSpotWSClientBase


class KrakenSpotWSClientV2(KrakenSpotWSClientBase):
    """
    Class to access public and private/authenticated websocket connections.

    **This client only supports the Kraken Websocket API v2.**

    - https://docs.kraken.com/websockets-v2

    … please use :class:`KrakenSpotWSClient` for accessing the Kraken
    Websockets API v1.

    This class holds up to two websocket connections, one private
    and one public.

    When accessing private endpoints that need authentication make sure,
    that the ``Access WebSockets API`` API key permission is set in the user's
    account.

    :param key: API Key for the Kraken Spot API (default: ``""``)
    :type key: str, optional
    :param secret: Secret API Key for the Kraken Spot API (default: ``""``)
    :type secret: str, optional
    :param url: Set a specific URL to access the Kraken REST API
    :type url: str, optional
    :param no_public: Disables public connection (default: ``False``).
        If not set or set to ``False``, the client will create a public and
        a private connection per default. If only a private connection is
        required, this parameter should be set to ``True``.
    :param beta: Use the beta websocket channels (maybe not supported anymore,
        default: ``False``)
    :type beta: bool

    .. code-block:: python
        :linenos:
        :caption: HowTo: Use the Kraken Spot Websocket Client (v2)

        import asyncio
        from kraken.spot import KrakenSpotWSClientV2


        class Client(KrakenSpotWSClientV2):

            async def on_message(self, event: dict) -> None:
                print(event)


        async def main() -> None:

            client = Client()         # unauthenticated
            client_auth = Client(     # authenticated
                key="kraken-api-key",
                secret="kraken-secret-key"
            )

            # subscribe to the desired feeds:
            await client.subscribe(
                params={"channel": "ticker", "symbol": ["BTC/USD"]}
            )
            # from now on the on_message function receives the ticker feed

            while not client.exception_occur:
                await asyncio.sleep(6)

        if __name__ == "__main__":
            try:
                asyncio.run(main())
            except KeyboardInterrupt:
                pass

    .. code-block:: python
        :linenos:
        :caption: HowTo: Use the websocket client (v2) as instance

        import asyncio
        from kraken.spot import KrakenSpotWSClientV2


        async def main() -> None:
            async def on_message(message) -> None:
                print(message)

            client = KrakenSpotWSClientV2(callback=on_message)
            await client.subscribe(
                params={"channel": "ticker", "symbol": ["BTC/USD"]}
            )

            while not client.exception_occur:
                await asyncio.sleep(10)


        if __name__ == "__main__":
            try:
                asyncio.run(main())
            except KeyboardInterrupt:
                pass


    .. code-block:: python
        :linenos:
        :caption: HowTo: Use the websocket client (v2) as context manager

        import asyncio
        from kraken.spot import KrakenSpotWSClientV2

        async def on_message(msg):
            print(msg)

        async def main() -> None:
            async with KrakenSpotWSClientV2(
                key="api-key",
                secret="secret-key",
                callback=on_message
            ) as session:
                await session.subscribe(
                    params={"channel": "ticker", "symbol": ["BTC/USD"]}
                )

            while True
                await asyncio.sleep(6)


        if __name__ == "__main__":
            try:
                asyncio.run(main())
            except KeyboardInterrupt:
                pass
    """

    def __init__(
        self: KrakenSpotWSClientV2,
        key: str = "",
        secret: str = "",
        callback: Optional[Callable] = None,
        no_public: bool = False,
        beta: bool = False,
    ):
        super().__init__(
            key=key,
            secret=secret,
            callback=callback,
            no_public=no_public,
            beta=beta,
            api_version="v2",
        )

    async def send_message(  # pylint: disable=arguments-differ
        self: KrakenSpotWSClientV2,
        message: dict,
        raw: bool = False,
    ) -> None:
        """
        Sends a message via the websocket connection. For private messages
        the authentication token will be assigned automatically if
        ``raw=False``.

        The user can specify a ``req_d`` within the message to identify
        corresponding responses via websocket feed.

        :param message: The information to send
        :type message: dict
        :param raw: If set to ``True`` the ``message`` will be sent directly.
        :type raw: bool, optional
        """
        if not message.get("method", False):
            raise ValueError(
                """
                The ``message`` must contain the 'method' key with a proper value.
            """
            )
        private: bool = (
            message["method"] in self.private_methods + self.private_channel_names
        )
        if private and not self._is_auth:
            raise KrakenException.KrakenAuthenticationError()

        retries: int = 0
        socket: Any = self._get_socket(private=private)
        while not socket and retries < 12:
            retries += 1
            socket = self._get_socket(private=private)
            await asyncio.sleep(0.4)

        if retries == 12 and not socket:
            raise TimeoutError("Could not get the desired websocket connection!")

        if raw:
            await socket.send(json.dumps(message))
            return

        if private:
            message["params"]["token"] = self._priv_conn.ws_conn_details["token"]

        await socket.send(json.dumps(message))

    async def subscribe(  # pylint: disable=arguments-differ
        self: KrakenSpotWSClientV2, params: dict, req_id: Optional[int] = None
    ) -> None:
        """
        Subscribe to a channel

        Success or failures are sent over the websocket connection and can be
        received via the on_message or callback function.

        When accessing private endpoints and subscription feeds that need
        authentication make sure, that the ``Access WebSockets API`` API key
        permission is set in the users Kraken account.

        - https://docs.kraken.com/websockets-v2/#subscribe

        :param params: The subscription message
        :type params: dict
        :param req_id: Identification number that will be added to the
            response message sent by the websocket feed.
        :type req_id: int, optional
        Initialize your client as described in
        :class:`kraken.spot.KrakenSpotWSClientV2` to run the following example:

        .. code-block:: python
            :linenos:
            :caption: Spot Websocket v2: Subscribe to a websocket feed

            >>> await client.subscribe(
            ...     params={"channel": "ticker", "symbol": ["BTC/USD"]}
            ... )

        """
        payload: dict = {"method": "subscribe"}
        if defined(req_id):
            payload["req_id"] = req_id

        payload["params"] = params

        await self.send_message(message=payload)

    async def unsubscribe(  # pylint: disable=arguments-differ
        self: KrakenSpotWSClientV2, params: dict, req_id: Optional[int] = None
    ) -> None:
        """
        Unsubscribe from a feed

        Success or failures are sent via the websocket connection and can be
        received via the on_message or callback function.

        When accessing private endpoints and subscription feeds that need
        authentication make sure, that the ``Access WebSockets API`` API key
        permission is set in the users Kraken account.

        - https://docs.kraken.com/websockets-v2/#unsubscribe

        :param params: The unsubscription message
        :type params: dict

        Initialize your client as described in
        :class:`kraken.spot.KrakenSpotWSClientV2` to run the following example:

        .. code-block:: python
            :linenos:
            :caption: Spot Websocket v2: Unsubscribe from a websocket feed

            >>> await client.unsubscribe(
            ...     params={"channel": "ticker", "symbol": ["BTC/USD"]}
            ... )
        """
        payload: dict = {"method": "unsubscribe"}
        if defined(req_id):
            payload["req_id"] = req_id

        payload["params"] = params

        await self.send_message(message=payload)

    @property
    def public_channel_names(self: KrakenSpotWSClientV2) -> List[str]:
        """
        Returns the list of valid values for ``channel`` when un-/subscribing
        from/to public feeds without authentication.

        See https://docs.kraken.com/websockets-v2/#channels for all channels.

        The available public channels are listed below:

        - `book <https://docs.kraken.com/websockets-v2/#book>`_
        - `instrument <https://docs.kraken.com/websockets-v2/#instrument>`_
        - `ohlc <https://docs.kraken.com/websockets-v2/#open-high-low-and-close-ohlc>`_
        - `ticker <https://docs.kraken.com/websockets-v2/#ticker>`_
        - `trade <https://docs.kraken.com/websockets-v2/#trade>`_

        :return: List of available public channel names
        :rtype: list[str]
        """
        return ["book", "instrument", "ohlc", "ticker", "trade"]

    @property
    def private_channel_names(self: KrakenSpotWSClientV2) -> List[str]:
        """
        Returns the list of valid values for ``channel`` when un-/subscribing
        from/to private feeds that need authentication.

        See https://docs.kraken.com/websockets-v2/#channels for all channels.

        Currently there is only one private channel (June 2023):

        - `executions <https://docs.kraken.com/websockets-v2/#executions>`_

        :return: List of available private channel names
        :rtype: list[str]
        """
        return ["executions"]

    @property
    def private_methods(self: KrakenSpotWSClientV2) -> List[str]:
        """
        Returns the list of available methods - parameters are  similar to the
        REST API trade methods.

        - `add_order <https://docs.kraken.com/websockets-v2/#add-order>`_
        - `batch_order <https://docs.kraken.com/websockets-v2/#batch-add>`_
        - `batch_cancel <https://docs.kraken.com/websockets-v2/#batch-cancel>`_
        - `cancel_all <https://docs.kraken.com/websockets-v2/#cancel-all-orders>`_
        - `cancel_all_orders_after <https://docs.kraken.com/websockets-v2/#cancel-all-orders-after>`_
        - `cancel_order <https://docs.kraken.com/websockets-v2/#cancel-order>`_
        - `edit_order <https://docs.kraken.com/websockets-v2/#edit-order>`_

        :return: List of available methods
        :rtype: list[str]
        """
        return [
            "add_order",
            "batch_add",
            "batch_cancel",
            "cancel_all",
            "cancel_all_orders_after",
            "cancel_order",
            "edit_order",
        ]