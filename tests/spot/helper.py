#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# GitHub: https://github.com/btschwertfeger
#

import logging
from asyncio import sleep
from time import time
from typing import Any, Union

from kraken.spot import KrakenSpotWSClient, SpotOrderBookClient


def is_not_error(value: Any) -> bool:
    """Returns True if 'error' as key not in dict."""
    return isinstance(value, dict) and "error" not in value


async def async_wait(seconds: float = 1.0) -> None:
    """Function that waits for ``seconds`` - asynchron."""
    start: float = time()
    while time() - seconds < start:
        await sleep(0.2)
    return


class SpotWebsocketClientTestWrapper(KrakenSpotWSClient):
    """
    Class that creates an instance to test the KrakenSpotWSClient.

    It writes the messages to the log and a file. The log is used
    within the tests, the log file is for local debugging.
    """

    LOG: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self: "SpotWebsocketClientTestWrapper", key: str = "", secret: str = ""
    ) -> None:
        super().__init__(key=key, secret=secret, callback=self.on_message)
        self.LOG.setLevel(logging.INFO)

    async def on_message(
        self: "SpotWebsocketClientTestWrapper", msg: Union[list, dict]
    ) -> None:
        """
        This is the callback function that must be implemented
        to handle custom websocket messages.
        """
        self.LOG.info(msg)  # the log is read within the tests

        log: str = ""
        try:
            with open("spot_ws.log", "r", encoding="utf-8") as logfile:
                log = logfile.read()
        except FileNotFoundError:
            pass

        with open("spot_ws.log", "w", encoding="utf-8") as logfile:
            logfile.write(f"{log}\n{msg}")


class SpotOrderBookClientWrapper(SpotOrderBookClient):
    """
    This class is used for testing the Spot Orderbook client.

    It writes the messages to the log and a file. The log is used
    within the tests, the log file is for local debugging.
    """

    LOG: logging.Logger = logging.getLogger(__name__)

    def __init__(self: "SpotOrderBookClientWrapper") -> None:
        super().__init__()
        self.LOG.setLevel(logging.INFO)

    async def on_message(
        self: "SpotOrderBookClientWrapper", msg: Union[list, dict]
    ) -> None:
        self.ensure_log(msg)
        await super().on_message(msg=msg)

    async def on_book_update(
        self: "SpotOrderBookClientWrapper", pair: str, message: list
    ) -> None:
        """
        This is the callback function that must be implemented
        to handle custom websocket messages.
        """
        self.ensure_log((pair, message))

    @classmethod
    def ensure_log(cls, content: Any) -> None:
        """
        Ensures that the messages are logged.
        Into a file for debugging and general to the log
        to read the logs within the unit tests.
        """
        cls.LOG.info(content)

        log: str = ""
        try:
            with open("spot_orderbook.log", "r", encoding="utf-8") as logfile:
                log = logfile.read()
        except FileNotFoundError:
            pass

        with open("spot_orderbook.log", "w", encoding="utf-8") as logfile:
            logfile.write(f"{log}\n{content}")
