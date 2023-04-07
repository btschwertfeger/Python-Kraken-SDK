#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# Github: https://github.com/btschwertfeger
#

"""Module that implements the Spot Kraken Websocket client"""
import logging
from typing import Coroutine, List, Union

from kraken.base_api import KrakenBaseSpotAPI


class SpotWsClientCl(KrakenBaseSpotAPI):
    """
    Class that implements the Spot Kraken Websocket client

    :param key: Optional Spot API public key (default: ``""``)
    :type key: str
    :param secret: Optional Spot API secret key (default: ``""``)
    :type secret: str
    :param url: Optional url to access the Kraken API (default: "https://api.kraken.com")
    :type url: str
    :param sandbox: Optional use of the sandbox (not supported so far, default: ``False``)
    :type sandbox: bool
    """

    def __init__(
        self, key: str = "", secret: str = "", url: str = "", sandbox: bool = False
    ):
        super().__init__(key=key, secret=secret, url=url, sandbox=sandbox)

        self._pub_conn = None
        self._priv_conn = None

    def get_ws_token(self) -> dict:
        """
        Get the authentication token to establish the authenticated
        websocket connection.

        - https://docs.kraken.com/rest/#tag/Websockets-Authentication

        :returns: The authentication token
        :rtype: dict
        """
        return self._request("POST", "/private/GetWebSocketsToken")

    async def create_order(
        self,
        ordertype: str,
        side: str,
        pair: str,
        volume: Union[str, int, float],
        price: Union[str, int, float, None] = None,
        price2: Union[str, int, float, None] = None,
        leverage: Union[str, int, float, None] = None,
        oflags: Union[str, List[str], None] = None,
        starttm: Union[str, int, None] = None,
        expiretm: Union[str, int, None] = None,
        deadline: str = None,
        userref: Union[str, int, None] = None,
        validate: bool = False,
        close_ordertype: Union[str, None] = None,
        close_price: Union[str, int, float, None] = None,
        close_price2: Union[str, int, float, None] = None,
        timeinforce: Union[str, int, None] = None,
    ) -> Coroutine:
        """
        Create an order and submit it.

        - https://docs.kraken.com/websockets/#message-addOrder

        :param ordertype: The type of order, one of: ``limit``, ``market`` ``stop-loss``, ``take-profit``, ``stop-loss-limit``, ``settle-position``, ``take-profit-limit``
        :type ordertype: str
        :param side: The side - one of ``buy``, ``sell``
        :type side: str
        :param pair: The asset pair to trade
        :type pair: str
        :param volume: The volume of the order that is being created
        :type volume: str | int | float
        :param price: Optional - The limit price for ``limit`` orders or the trigger price for orders with ``ordertype`` one of ``stop-loss``, ``stop-loss-limit``, ``take-profit``, and ``take-profit-limit``
        :type price: str | int | float | None
        :param price2: Optional - The second price for ``stop-loss-limit`` and ``take-profit-limit`` orders (see the referenced Kraken documentaion for more information)
        :type price2: str | int | float | None
        :param leverage: Optional - The leverage
        :type leverage: str | int | float | None
        :param oflags: Order flags like ``post``, ``fcib``, ``fciq``, ``nomp``, ``viqc`` (see the referenced Kraken documentaion for more information)
        :type oflags: str | List[str] | None
        :param starttm: Unix timestamp or seconds defining the start time (default: ``"0"``)
        :type starttm: str | int | None
        :param expiretim: Unix timestamp or time in seconds defining the expiration of the order, (default: ``"0"`` - i.e., no expiration)
        :type expiretim: str
        :param deadline: (see the referenced Kraken documentaion for more information)
        :type deadline: str
        :param userref: User reference id for example to group orders
        :type userref: int
        :param validate: Optinal - Validate the order without placing on the market (default: ``False``)
        :type validate: bool
        :param close_ordertype:  Optional - Conditional close order type, one of: ``limit``, ``stop-loss``, ``take-profit``, ``stop-loss-limit``, ``take-profit-limit`` (see the referenced Kraken documentaion for more information)
        :type close_ordertype: str | None
        :param close_price: Optional - Conditional close price
        :type close_price: str | int | float | None
        :param close_price2: Optional - Second conditional close price
        :type close_price2: str | int | float | None
        :param timeinforce: Optional - how long the order raimains in the orderbook, one of: ``GTC``, `ÌOC``, ``GTD`` (see the referenced Kraken documentaion for more information)
        :type timeinforce: str | None

        :raises ValueError: If input is not correct
        :rtype: None
        """
        if not self._priv_conn:
            logging.warning("Websocket not connected!")
            return
        if not self._priv_conn.is_auth:
            raise ValueError("Cannot create_order on public websocket client!")

        payload = {
            "event": "addOrder",
            "ordertype": str(ordertype),
            "type": str(side),
            "pair": str(pair),
            "price": str(price),
            "volume": str(volume),
            "validate": str(validate),
        }
        if price2 is not None:
            payload["price2"] = str(price2)
        if oflags is not None:
            if isinstance(oflags, str):
                payload["oflags"] = oflags
            elif isinstance(oflags, list):
                payload["oflags"] = self._to_str_list(oflags)
            else:
                raise ValueError(
                    "oflags must be type List[str] or comma delimited list of order flags as str. Available flags: viqc, fcib, fciq, nompp, post"
                )
        if starttm is not None:
            payload["starttm"] = str(starttm)
        if expiretm is not None:
            payload["expiretm"] = str(expiretm)
        if deadline is not None:
            payload["deadline"] = str(deadline)
        if userref is not None:
            payload["userref"] = str(userref)
        if leverage is not None:
            payload["leverage"] = str(leverage)
        if close_ordertype is not None:
            payload["close[ordertype]"] = close_ordertype
        if close_price is not None:
            payload["close[price]"] = str(close_price)
        if close_price2 is not None:
            payload["close[price2]"] = str(close_price2)
        if timeinforce is not None:
            payload["timeinforce"] = timeinforce

        await self._priv_conn.send_message(msg=payload, private=True)

    async def edit_order(
        self,
        orderid: str,
        reqid: Union[str, int, None] = None,
        pair: Union[str, None] = None,
        price: Union[str, int, float, None] = None,
        price2: Union[str, int, float, None] = None,
        volume: Union[str, int, float, None] = None,
        oflags: Union[str, List[str], None] = None,
        newuserref: Union[str, int, None] = None,
        validate: bool = False,
    ) -> Coroutine:
        """
        Edit an open order that was placed on the Spot market.

        - https://docs.kraken.com/websockets/#message-editOrder

        :param orderId: The orderId of the order to edit
        :type orderId: str
        :param reqid: Optional - Filter by reqid
        :type reqid: str | int | None
        :param pair: Optional - Filter by pair
        :type pair: str | None
        :param price: Optional - Set a new price
        :type price: str | int | float | None
        :param price2: Optional - Set a new second price
        :type price2: str | int | float | None
        :param volume: Optional - Set a new volume
        :type volume: str | int | float | None
        :param oflags: Optional - Set new oflags (overwrite old ones)
        :type oflags: str | List[str] | None
        :param newuserref: Optional set a new user reference id
        :type newuserref: str | int | None
        :param validate: Optional - Validate the input without applying the changes (default: ``False``)
        :type validate: bool
        :raises ValueError: If input is not correct
        :rtype: None
        """
        if not self._priv_conn:
            logging.warning("Websocket not connected!")
            return
        if not self._priv_conn.is_auth:
            raise ValueError("Cannot edit_order on public websocket client!")

        payload = {"event": "editOrder", "orderid": orderid, "validate": str(validate)}
        if reqid is not None:
            payload["reqid"] = reqid
        if pair is not None:
            payload["pair"] = pair
        if price is not None:
            payload["price"] = str(price)
        if price2 is not None:
            payload["price2"] = str(price2)
        if volume is not None:
            payload["volume"] = str(volume)
        if oflags is not None:
            payload["oflags"] = self._to_str_list(oflags)
        if newuserref is not None:
            payload["newuserref"] = str(newuserref)

        await self._priv_conn.send_message(msg=payload, private=True)

    async def cancel_order(self, txid: Union[str, List[str]]) -> Coroutine:
        """
        Cancel a specific order or a list of orders.

        - https://docs.kraken.com/websockets/#message-cancelOrder

        :param txid: Transaction id or list of txids or comma delimted list as string
        :type txid: str | List[str]
        :return: None
        :raises ValueError: If the websocket is not connected or the connection is not authenticated
        """
        if not self._priv_conn:
            logging.warning("Websocket not connected!")
            return
        if not self._priv_conn.is_auth:
            raise ValueError("Cannot cancel_order on public websocket client!")
        await self._priv_conn.send_message(
            msg={"event": "cancelOrder", "txid": self._to_str_list(txid)}, private=True
        )

    async def cancel_all_orders(self) -> Coroutine:
        """
        Cancel all open Spot orders.

        - https://docs.kraken.com/websockets/#message-cancelAll

        :return: None
        :raises ValueError: If the websocket is not connected or the connection is not authenticated
        """

        if not self._priv_conn:
            logging.warning("Websocket not connected!")
            return
        if not self._priv_conn.is_auth:
            raise ValueError("Cannot use cancel_all_orders on public websocket client!")
        await self._priv_conn.send_message(msg={"event": "cancelAll"}, private=True)

    async def cancel_all_orders_after(self, timeout: int) -> Coroutine:
        """
        Set a Death Man's Switch

        - https://docs.kraken.com/websockets/#message-cancelAllOrdersAfter

        :param timeout: Set the timeout in seconds to cancel the orders after, set to ``0`` to reset.
        :type timeout: int
        :return: None
        :raises ValueError: If the websocket is not connected or the connection is not authenticated
        """
        if not self._priv_conn:
            logging.warning("Websocket not connected!")
            return
        if not self._priv_conn.is_auth:
            raise ValueError(
                "Cannot use cancel_all_orders_after on public websocket client!"
            )
        await self._priv_conn.send_message(
            msg={"event": "cancelAllOrdersAfter", "timeout": timeout}, private=True
        )
