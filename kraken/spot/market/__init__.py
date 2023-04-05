#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# Github: https://github.com/btschwertfeger
#

"""Module that implements the Kraken Spot market client"""
from typing import List, Union

from kraken.base_api import KrakenBaseSpotAPI


class Market(KrakenBaseSpotAPI):
    """
    Class that implements the Kraken Spot Market client. Can be used to access
    the Kraken Spot market data.

    :param key: Optional Spot API public key (default: ``""``)
    :type key: str
    :param secret: Optional Spot API secret key (default: ``""``)
    :type secret: str
    :param url: Optional url to access the Kraken API (default: https://api.kraken.com)
    :type url: str
    :param sandbox: Optional use of the sandbox (not supported so far, default: ``False``)
    :type sandbox: bool

    .. code-block:: python
        :linenos:
        :caption: Example

        >>> from kraken.spot import Market
        >>> market = Market() # unauthenticated
        >>> auth_market = Market(key="api-key", secret="secret-key") # authenticated
    """

    def get_assets(
        self,
        assets: Union[str, List[str], None] = None,
        aclass: Union[str, None] = None,
    ) -> dict:
        """
        Get information about all available assets for trading, staking, deposit,
        and withdraw.

        - https://docs.kraken.com/rest/#operation/getAssetInfo

        :param asset: Optional - Filter by asset(s)
        :type asset: str | List[str] | None
        :param aclass: Optional - Filter by asset class
        :type aclass: str | None
        :return: Information about the requested assets
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import Market
            >>> market = Market()
            >>> market.get_assets(assets="DOT")
            {
                'DOT': {
                    'aclass': 'currency',
                    'altname': 'DOT',
                    'decimals': 10,
                    'display_decimals': 8,
                    'collateral_value': 0.9,
                    'status': 'enabled'
                }
            }
            >>> market.get_assets(assets=["MATIC", "XBT"])
            {
                'MATIC': {
                    'aclass': 'currency',
                    'altname': 'MATIC',
                    'decimals': 10,
                    'display_decimals': 5,
                    'collateral_value': 0.7,
                    'status': 'enabled'
                },
                'XXBT': {
                    'aclass': 'currency',
                    'altname': 'XBT',
                    'decimals': 10,
                    'display_decimals': 5,
                    'collateral_value': 1.0,
                    'status': 'enabled'
                }
            }
        """
        params = {}
        if assets is not None:
            params["asset"] = self._to_str_list(assets)
        if aclass is not None:
            params["aclass"] = aclass
        return self._request(
            method="GET", uri="/public/Assets", params=params, auth=False
        )

    def get_tradable_asset_pair(
        self, pair: Union[str, List[str]], info: Union[str, None] = None
    ) -> dict:
        """
        Get information about the tradable asset pairs.

        - https://docs.kraken.com/rest/#operation/getTradableAssetPairs

        :param asset: Filter by asset pair(s)
        :type asset: str | List[str]
        :param info: Optional - Filter by info, can be one of: `info` (all info), `leverage` (leverage info), `fees` (fee info), and `margin` (margin info)
        :type info: str | None
        :return: Information about the asset pair
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import Market
            >>> Market().get_tradeable_asset_pair(pair="XBTUSD")
            {
                'XXBTZUSD': {
                    'altname': 'XBTUSD',
                    'wsname': 'XBT/USD',
                    'aclass_base': 'currency',
                    'base': 'XXBT',
                    'aclass_quote': 'currency',
                    'quote': 'ZUSD',
                    'lot': 'unit',
                    'cost_decimals': 5,
                    'pair_decimals': 1,
                    'lot_decimals': 8,
                    'lot_multiplier': 1,
                    'leverage_buy': [2, 3, 4, 5],
                    'leverage_sell': [2, 3, 4, 5],
                    'fees': [
                        [0, 0.26], [50000, 0.24], [100000, 0.22],
                        [250000, 0.2], [500000, 0.18], [1000000, 0.16],
                        [2500000, 0.14], [5000000, 0.12], [10000000, 0.1]
                    ],
                    'fees_maker': [
                        [0, 0.16], [50000, 0.14], [100000, 0.12],
                        [250000, 0.1], [500000, 0.08], [1000000, 0.06],
                        [2500000, 0.04], [5000000, 0.02], [10000000, 0.0]
                    ],
                    'fee_volume_currency': 'ZUSD',
                    'margin_call': 80,
                    'margin_stop': 40,
                    'ordermin': '0.0001',
                    'costmin': '0.5',
                    'tick_size': '0.1',
                    'status': 'online',
                    'long_position_limit': 270,
                    'short_position_limit': 180
                }
            }
        """
        params = {}
        params["pair"] = self._to_str_list(pair)
        if info is not None:
            params["info"] = info

        return self._request(
            method="GET", uri="/public/AssetPairs", params=params, auth=False
        )

    def get_ticker(self, pair: Union[str, List[str], None] = None) -> dict:
        """
        Returns all tickers if pair is not specified - else just
        the ticker of the ``pair``. Multiple pairs can be specified.

        https://docs.kraken.com/rest/#operation/getTickerInformation

        :param pair: Optional - Filter by pair(s)
        :type pair: str | List[str] | None
        :return: The ticker(s) including ask, bid, close, volume, vwap, high, low, todays open and more
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import Market
            >>> Market().get_ticker(pair="XBTUSD")
            {
                'XXBTZUSD': {
                    'a': ['27948.00000', '3', '3.000'], # ask
                    'b': ['27947.90000', '1', '1.000'], # bid
                    'c': ['27947.90000', '0.00842808'], # last trade close, lot volume
                    'v': ['3564.58017484', '4138.93906134'], # volume today and last 24h
                    'p': ['28351.31431', '28329.55480'], # vwap today and last 24h
                    't': [33574, 43062], # number of trades today and last 24h
                    'l': ['27813.10000', '27813.10000'], # low today and last 24h
                    'h': ['28792.30000', '28792.30000'], # high today and last 24
                    'o': '28173.00000' # today's opening price
                }
            }
        """
        params = {}
        if pair is not None:
            params["pair"] = self._to_str_list(pair)
        return self._request(
            method="GET", uri="/public/Ticker", params=params, auth=False
        )

    def get_ohlc(
        self,
        pair: str,
        interval: Union[int, str] = 1,
        since: Union[int, str, None] = None,
    ) -> dict:
        """
        Get the open, high, low, and close data for a specific trading pair.
        Returns at max 720 time stamps per request.

        - https://docs.kraken.com/rest/#operation/getOHLCData

        :param pair: The pair to get the ohlc from
        :type pair: str
        :param interval: Optional - the Interval in minutes (default: ``1``)
        :type interval: str | int
        :param since: Timestamp to start from
        :type since: int | str | None
        :return: The OHLC data of a given asset pair
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import Market
            >>> Market().get_ohlc(pair="XBTUSD")
            {
                "XXBTZUSD": [
                    [
                        1680671100,
                        "28488.9",
                        "28489.0",
                        "28488.8",
                        "28489.0",
                        "28488.9",
                        "1.03390376",
                        8
                    ], ...
                ]
            }
        """
        params = {"pair": pair, "interval": interval}
        if since is not None:
            params["since"] = since
        return self._request(
            method="GET", uri="/public/OHLC", params=params, auth=False
        )

    def get_order_book(self, pair: str, count: int = 100) -> dict:
        """
        Get the current orderbook of a specified trading pair.

        - https://docs.kraken.com/rest/#operation/getOrderBook

        :param pair: The pair to get the orderbook
        :type pair: str
        :param count: Number of asks and bids, must be one of {1...500} (default: 100)
        :type count: int

        :return:
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import Market
            >>> Market().get_order_book(pair="XBTUSD", count=2)
            {
                'XXBTZUSD': {
                    'asks': [
                        ['28000.00000', '1.091', 1680714417],
                        ['28001.00000', '0.001', 1680714413]
                    ],
                    'bids': [
                        ['27999.90000', '2.240', 1680714419],
                        ['27999.50000', '0.090', 1680714418]
                    ]
                }
            }
        """
        return self._request(
            method="GET",
            uri="/public/Depth",
            params={"pair": pair, "count": count},
            auth=False,
        )

    def get_recent_trades(self, pair: str, since: Union[str, int, None] = None) -> dict:
        """
        Get the latest trades for a specific trading pair (up to 1000).

        - https://docs.kraken.com/rest/#operation/getRecentTrades

        :param pair: Pair to get the recend trades
        :type pair: str
        :param since: Filter trades since given timestamp (default: None)
        :type str | int | None

        :return: The last public trades (up to 1000 results)
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import Market
            >>> Market().get_recent_trades(pair="XBTUSD")
            {
                "XXBTZUSD": [
                    ["27980.90000", "0.00071054", 1680712703.2524643, "b", "l", "", 57811127],
                    ["27981.00000", "0.03180000", 1680712715.1806278, "b", "l", "", 57811128],
                    ["27980.90000", "0.00010000", 1680712715.469506, "s", "m", "", 57811129],
                    ...
                ]
            }

        """
        params = {"pair": pair}
        if since is not None:
            params["since"] = None
        return self._request(
            method="GET", uri="/public/Trades", params=params, auth=False
        )

    def get_recend_spreads(
        self, pair: str, since: Union[str, int, None] = None
    ) -> dict:
        """
        Get the latest spreads for a specific trading pair.

        - https://docs.kraken.com/rest/#operation/getRecentSpreads

        :param pair: Pair to get the recend spreads
        :type pair: str
        :param since: Filter trades since given timestamp (default: None)
        :type str | int | None
        :return: The last n spreads of the asset pair
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import Market
            >>> Market().get_recend_spreads(pair="XBTUSD")
            {
                "XXBTZUSD": [
                    [1680714601, "28015.00000", "28019.40000"],
                    [1680714601, "28015.00000", "28017.00000"],
                    [1680714601, "28015.00000", "28016.90000"],
                    ...
                ]
            }
        """
        params = {"pair": pair}
        if since is not None:
            params["since"] = since
        return self._request(
            method="GET", uri="/public/Spread", params=params, auth=False
        )

    def get_system_status(self) -> dict:
        """
        Returns the system status of the Kraken Spot API.

        - https://docs.kraken.com/rest/#section/General-Usage/Requests-Responses-and-Errors

        :return: Success or failure
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import Market
            >>> Market().get_system_status()
            {'status': 'online', 'timestamp': '2023-04-05T17:12:31Z'}
        """
        return self._request(method="GET", uri="/public/SystemStatus", auth=False)
