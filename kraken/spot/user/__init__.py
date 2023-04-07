#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# Github: https://github.com/btschwertfeger
#

""" Module that implements the Kraken Spot User client
"""
from typing import List, Union

from kraken.base_api import KrakenBaseSpotAPI


class User(KrakenBaseSpotAPI):
    """
    Class that implements the Kraken Spot User client

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

        >>> from kraken.spot import User
        >>> user = User() # unauthenticated
        >>> auth_user = User(key="api-key", secret="secret-key") # authenticated
    """

    def get_account_balance(self) -> dict:
        """
        Get the current balances of the user.

        - https://docs.kraken.com/rest/#operation/getAccountBalance

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_account_balances()
            {
                'ZUSD': '241983.1415',
                'KFEE': '8020.22',
                'BCH': '0.0000077100',
                'ETHW': '0.0000040',
                'XXLM': '0.00000000',
                'ZEUR': '0.0000',
                'DOT': '32011.21197000',
                ...
            }
        """
        return self._request(method="POST", uri="/private/Balance")

    def get_balances(self, currency: str) -> dict:
        """
        Returns the balance and available balance of a given currency.

        :param currency: The currency to get the balances from
        :type currency: str
        :return: Dictionary containing the ``currency`` (currency as string),
         ``balance`` (inclding value in orders), and ``available_balance``
         (amount that is not in orders)
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_balances(currency="DOT")
            {
                'currency': 'DOT',
                'balance': 32011.21197000,
                'available_balance': 14999.06197000
            }
        """

        balance = float(0)
        curr_opts = (currency, f"Z{currency}", f"X{currency}")
        for symbol, value in self.get_account_balance().items():
            if symbol in curr_opts:
                balance = float(value)
                break

        available_balance = balance
        for order in self.get_open_orders()["open"].values():
            if currency in order["descr"]["pair"][0 : len(currency)]:
                if order["descr"]["type"] == "sell":
                    available_balance -= float(order["vol"])
            elif currency in order["descr"]["pair"][-len(currency) :]:
                if order["descr"]["type"] == "buy":
                    available_balance -= float(order["vol"]) * float(
                        order["descr"]["price"]
                    )

        return {
            "currency": currency,
            "balance": balance,
            "available_balance": available_balance,
        }

    def get_trade_balance(self, asset: str = "ZUSD") -> dict:
        """
        Get the summary of all collateral balances.

        - https://docs.kraken.com/rest/#operation/getTradeBalance

        :param asset: Optional - The base asset to determine the balances (default: ``ZUSD``)
        :type asset: str

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_trade_balance()
            {
                'eb': '983691.5512', # Equivalent balance - all currencies combined
                'tb': '322296.9914', # Trade balance - balance of all equity currencies
                'm': '0.0000',       # Margin amount of open positions
                'uv': '0.0000',      # Unexecuted value of partly filled orders/positions
                'n': '0.0000',       # Unrealized net profit/loss of open positions
                'c': '0.0000',       # Cost basis of open positions
                'v': '0.0000',       # Current floating value of open positions
                'e': '983691.5512',  # Equity ( eb + n )
                'mf': '322296.9914'  # Free margin ( tb / initial margin ) * 100
            }
        """
        params = {}
        if asset is not None:
            params["asset"] = asset
        return self._request(method="POST", uri="/private/TradeBalance", params=params)

    def get_open_orders(
        self, trades: bool = False, userref: Union[int, None] = None
    ) -> dict:
        """
        Get information about the open orders.

        - https://docs.kraken.com/rest/#operation/getOpenOrders

        :param trades: Include trades related to position or not into the response (default: ``False``)
        :type trades: bool
        :param userref: Optional - Filter the results by user reference id
        :type userref: int | None

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_open_orders()
            {
                'open': {
                    'OCUG7Z-4EM5R-7ZCJ47': {
                        'refid': None,
                        'userref': 0,
                        'status':
                        'open',
                        'opentm': 1680777427.576083,
                        'starttm': 0,
                        'expiretm': 0,
                        'descr': {
                            'pair': 'ETHUSD',
                            'type': 'buy',
                            'ordertype': 'limit',
                            'price': '1720.37',
                            'price2': '0',
                            'leverage': 'none',
                            'order': 'buy 0.02000000 ETHUSD @ limit 1720.37',
                            'close': ''
                        },
                        'vol': '0.02000000',
                        'vol_exec': '0.00000000',
                        'cost': '0.00000',
                        'fee': '0.00000',
                        'price': '0.00000',
                        'stopprice': '0.00000',
                        'limitprice': '0.00000',
                        'misc': '',
                        'oflags': 'fciq'
                    },
                    'OFZP3V-UMMUJ-6HMRMB': {
                        ...
                    }
                }
            }
        """
        params = {"trades": trades}
        if userref is not None:
            params["userref"] = userref
        return self._request(method="POST", uri="/private/OpenOrders", params=params)

    def get_closed_orders(
        self,
        trades: bool = False,
        userref: Union[int, None] = None,
        start: Union[int, None] = None,
        end: Union[int, None] = None,
        ofs: Union[int, None] = None,
        closetime: str = "both",
    ) -> dict:
        """
        Get the 50 latest closed (filled or cancelled) orders.

        - https://docs.kraken.com/rest/#operation/getClosedOrders

        :param trades: Include trades related to position into the response or not (default: ``False``)
        :type trades: bool
        :param userref: Optional - Filter the results by user reference id
        :type userref: int | None
        :param start: Optional - Unix timestamp to start the search from
        :type start: int | None
        :param end: Optional - Unix timestamp to define the last result to include
        :type end: int | None
        :param closetime: Optional - Specify the exact time frame, one of: ``both``, ``open``, ``close`` (default: ``both``)
        :type closetime: str

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_closed_orders()
            {
                'closed': {
                    'OBGFYP-XVQNL-P4GMWF': {
                        'refid': None,
                        'userref': 0,
                        'status': 'closed',
                        'opentm': 1680698929.9052045,
                        'starttm': 0,
                        'expiretm': 0,
                        'descr': {
                            'pair': 'ETHUSD',
                            'type': 'buy',
                            'ordertype': 'limit',
                            'price': '1860.76',
                            'price2': '0',
                            'leverage': 'none',
                            'order': 'buy 0.02000000 ETHUSD @ limit 1860.76',
                            'close': ''
                        },
                        'vol': '0.02000000',
                        'vol_exec': '0.02000000',
                        'cost': '37.21520',
                        'fee': '0.05954',
                        'price': '1860.76',
                        'stopprice': '0.00000',
                        'limitprice': '0.00000',
                        'misc': '',
                        'oflags': 'fciq',
                        'reason': None,
                        'closetm': 1680777419.8115675
                    },
                    'OAUHYR-YCVK6-P22G6P': {
                        ...
                    }
                }
            }
        """
        params = {"trades": trades, "closetime": closetime}
        if userref is not None:
            params["userref"] = userref
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if ofs is not None:
            params["ofs"] = ofs

        return self._request(method="POST", uri="/private/ClosedOrders", params=params)

    def get_orders_info(
        self,
        txid: Union[List[str], str],
        trades: bool = False,
        userref: Union[int, None] = None,
        consolidate_taker: bool = True,
    ) -> dict:
        """
        Get information about one or more orders.

        - https://docs.kraken.com/rest/#tag/User-Data/operation/getOrdersInfo

        :param txid: A transaction id of a specific order, a list of txids or a string containing a comma delimited list of txids
        :type txid: str | List[str]
        :param trades: Include trades in the result or not (default: ``False``)
        :type trades: bool
        :param userref: Optional - Filter results by user reference id
        :type userref: int | None
        :param consolidate_taker: Consolidate trdes by individual taker trades (default: ``True``)
        :type consolidate_taker: bool

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_orders_info(txid="OG5IL4-6AR7I-ZAPZEZ")
            {
                'OG5IL4-6AR7I-ZAPZEZ': {
                    'refid': None,
                    'userref': 0,
                    'status': 'open',
                    'opentm': 1680618712.3723278,
                    'starttm': 0,
                    'expiretm': 0,
                    'descr': {
                        'pair': 'MATICUSD',
                        'type': 'buy',
                        'ordertype': 'limit',
                        'price': '1.0922',
                        'price2': '0',
                        'leverage': 'none',
                        'order': 'buy 45.77910000 MATICUSD @ limit 1.0922',
                        'close': ''
                    },
                    'vol': '45.77910000',
                    'vol_exec': '0.00000000',
                    'cost': '0.000000',
                    'fee': '0.000000',
                    'price': '0.000000',
                    'stopprice': '0.000000',
                    'limitprice': '0.000000',
                    'misc': '',
                    'oflags': 'fciq',
                    'reason': None
                }
            }
            >>> user.get_orders_info(txid=["OAUHYR-YCVK6-P22G6P", "OG5IL4-6AR7I-ZAPZEZ"])
            {
                'OAUHYR-YCVK6-P22G6P': {
                    'refid': None,
                    'userref': 0,
                    'status': 'canceled',
                    'opentm': 1680618716.4409518,
                    'starttm': 0,
                    'expiretm': 0,
                    'descr': {
                        'pair': 'MATICUSD',
                        'type': 'buy',
                        'ordertype': 'limit',
                        'price': '1.0501',
                        'price2': '0',
                        'leverage': 'none',
                        'order': 'buy 47.61450000 MATICUSD @ limit 1.0501',
                        'close': ''
                    },
                    'vol': '47.61450000',
                    'vol_exec': '0.00000000',
                    'cost': '0.000000',
                    'fee': '0.000000',
                    'price': '0.000000',
                    'stopprice': '0.000000',
                    'limitprice': '0.000000',
                    'misc': '',
                    'oflags': 'fciq',
                    'reason': 'User requested',
                    'closetm': 1680756419.5768735
                }
            }
        """
        params = {
            "txid": txid,
            "trades": trades,
            "consolidate_taker": consolidate_taker,
        }
        if isinstance(txid, list):
            params["txid"] = self._to_str_list(txid)
        if userref is not None:
            params["userref"] = userref
        return self._request(method="POST", uri="/private/QueryOrders", params=params)

    def get_trades_history(
        self,
        type_: str = "all",
        trades: bool = False,
        start: Union[int, None] = None,
        end: Union[int, None] = None,
        ofs: Union[int, None] = None,
        consolidate_taker: bool = True,
    ) -> dict:
        """
        Get information about the latest 50 trades and fills. Can be paginated.

        - https://docs.kraken.com/rest/#operation/getTradeHistory

        :param type_: Filter by type of trade, one of: ``all``, ``any position``, ``closed position``, ``closing position``, and ``no position`` (default: ``all``)
        :type type_: str
        :param trades: Include trades related to a position or not
        :type trades: bool
        :param start: Optional - Timestamp to start the search
        :type start: int | None
        :param end: Optional - Timestamp to define the last inluded result
        :type end: int | None
        :param consolidate_taker: Consolidate trades by individual taker trades (default: ``True``)
        :type consolidate_taker: bool

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_trades_history()
            {
                'count': 630,
                'trades': {
                    'TPLJ5E-NONOU-5LH7JL': {
                        'ordertxid': 'OBGFYP-XVQNL-P4GMWF',
                        'postxid': 'TKH2SE-M7IF5-CFI7LT',
                        'pair': 'XETHZUSD',
                        'time': 1680777419.8115635,
                        'type': 'buy',
                        'ordertype': 'limit',
                        'price': '1860.76000',
                        'cost': '37.21520',
                        'fee': '0.05954',
                        'vol': '0.02000000',
                        'margin': '0.00000',
                        'leverage': '0',
                        'misc': '',
                        'trade_id': 43914718
                    },
                    'TNGMNU-XQSRA-LKCWOK': { ... },
                    ...
                }
            }
        """
        params = {
            "type": type_,
            "trades": trades,
            "consolidate_taker": consolidate_taker,
        }
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if ofs is not None:
            params["ofs"] = ofs
        return self._request(method="POST", uri="/private/TradesHistory", params=params)

    def get_trades_info(
        self, txid: Union[str, List[str]], trades: bool = False
    ) -> dict:
        """
        Get information about specific trades/filled orders. 20 txids can be queried ad max.

        - https://docs.kraken.com/rest/#operation/getTradesInfo

        :param txid: txid or list of txids or comma delimited list of txids as string
        :type txid: str | List[str]
        :param trades: Include trades related to position in result (default: ``False``)
        :type trades: bool

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_trades_info(txid="TNGMNU-XQSRA-LKCWOK")
            {
                'TNGMNU-XQSRA-LKCWOK': {
                    'ordertxid': 'OHAJCS-ON45W-UIXHT7',
                    'postxid': 'TKH2SE-M7IF5-CFI7LT',
                    'pair': 'XETHZUSD',
                    'time': 1680606470.360982,
                    'type': 'sell',
                    'ordertype': 'limit',
                    'price': '1855.16000',
                    'cost': '37.10320',
                    'fee': '0.05937',
                    'vol': '0.02000000',
                    'margin': '0.00000',
                    'leverage': '0',
                    'misc': '',
                    'trade_id': 43878042
                }
            }
        """
        return self._request(
            method="POST",
            uri="/private/QueryTrades",
            params={
                "trades": trades,
                "txid": self._to_str_list(txid),
            },
        )

    def get_open_positions(
        self,
        txid: Union[str, List[str], None] = None,
        docalcs: bool = False,
        consolidation: str = "market",
    ) -> dict:
        """
        Get information about the open positions.

        - https://docs.kraken.com/rest/#operation/getOpenPositions

        :param txid: Optional - Filter by txid or list of txids or comma delimited list of txids as string
        :type txid: str | List[str], None
        :param docalcs: Include profit and loss calculation into the result (default: ``False``)
        :type docalcs: bool
        :param consolidation: Consolidate positions by market/pair
        :type consolidation: str


        """
        params = {"docalcs": docalcs, "consolidation": consolidation}
        if txid is not None:
            params["txid"] = self._to_str_list(txid)
        return self._request(method="POST", uri="/private/OpenPositions", params=params)

    def get_ledgers_info(
        self,
        asset: Union[str, List[str]] = "all",
        aclass: str = "currency",
        type_: str = "all",
        start: Union[int, None] = None,
        end: Union[int, None] = None,
        ofs: Union[int, None] = None,
    ) -> dict:
        """
        Get information about the users ledger entries.
        50 results can be returned at a time.

        - https://docs.kraken.com/rest/#operation/getLedgers

        :param asset: The asset(s) to filter for (default: ``all``)
        :type asset: str | List[str]
        :param aclass: The asset class (default: ``currency`` )
        :type aclass: str
        :param type_: Optional - Leder type, one of: ``all``, ``deposit``, ``withdrawal``,
         ``trade``, ``margin``, ``rollover``, ``credit``, ``transfer``, ``settled``,
         ``staking``, and ``sale`` (default: ``all``)
        :type type_: str
        :param start: Optional - Unix timestamp to start the search from
        :type start: int | None
        :param end: Optional - Unix timestamp to define the last result
        :type end: int | None
        :param ofs: Optional - Offset for pagination
        :type ofs: int | None

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_ledgers_info(asset=["KFEE","EUR","ETH"])
            {
                'count': 519,
                'ledger': {
                    'LKLSX7-VUXD4-HDLK2P': {
                        'aclass': 'currency',
                        'amount': '0.00',
                        'asset': 'KFEE',
                        'balance': '8020.22',
                        'fee': '5.95',
                        'refid': 'TPLJ5E-NONOU-5LH7JL',
                        'time': 1680777419.8115911,
                        'type': 'trade',
                        'subtype': ''
                    },
                    'L4BF6E-FIFW7-6UB2CI': { ... },
                    ...
                }
            }
        """
        params = {"asset": asset, "aclass": aclass, "type": type_}
        if isinstance(params["asset"], list):
            params["asset"] = self._to_str_list(asset)
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if ofs is not None:
            params["ofs"] = ofs
        return self._request(method="POST", uri="/private/Ledgers", params=params)

    def get_ledgers(self, id_: Union[str, List[str]], trades: bool = False) -> dict:
        """
        Get information about specific ledeger entries.

        - https://docs.kraken.com/rest/#operation/getLedgersInfo

        :param id_: Ledger id as string, list of strings, or comma delimited list of ledger ids as string
        :type id_: str | List[str]
        :param trades: Include trades related to a position or not (default: ``False``)
        :type trades: bool

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_ledgers(id_="LKLSX7-VUXD4-HDLK2P")
            {
                'LKLSX7-VUXD4-HDLK2P': {
                    'aclass': 'currency',
                    'amount': '0.00',
                    'asset': 'FEE',
                    'balance': '8020.22',
                    'fee': '5.95',
                    'refid': 'TPLJ5E-NONOU-5LH7JL',
                    'time': 1680777419.8115911,
                    'type': 'trade',
                    'subtype': ''
                }
            }
        """
        return self._request(
            method="POST",
            uri="/private/QueryLedgers",
            params={"trades": trades, "id": self._to_str_list(id_)},
        )

    def get_trade_volume(
        self, pair: Union[str, List[str], None] = None, fee_info: bool = True
    ) -> dict:
        """
        Get the 30-day user specific trading volume in USD.

        - https://docs.kraken.com/rest/#operation/getTradeVolume

        :param pair: Optional - Asset pair, list of asset pairs or comma delimited list (as string) of asset pairs to filter
        :type pair: str | List[str] | None
        :param fee_info: Optional - Include fee information or not (default: ``True``)
        :type fee_info: bool

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.get_trade_volume()
            {
                'currency': 'ZUSD',
                'volume': '212220.9741',
                'fees': None,
                'fees_maker': None
            }
            >>> u.get_trade_volume(pair="DOTUSD")
            {
                'currency': 'ZUSD',
                'volume': '212243.1210',
                'fees': {
                    'DOTUSD': {
                        'fee': '0.2200',
                        'minfee': '0.1000',
                        'maxfee': '0.2200',
                        'nextfee': '0.2000',
                        'tiervolume': '0.0000',
                        'nextvolume': '250000.0000'
                    }
                },
                'fees_maker': {
                    'DOTUSD': {
                        'fee': '0.1200',
                        'minfee': '0.0000',
                        'maxfee': '0.1200',
                        'nextfee': '0.1000',
                        'tiervolume': '0.0000',
                        'nextvolume': '250000.0000'
                    }
                }
            }

        """
        params = {"fee-info": fee_info}
        if pair is not None:
            params["pair"] = self._to_str_list(pair)
        return self._request(method="POST", uri="/private/TradeVolume", params=params)

    def request_export_report(
        self,
        report: str,
        description: str,
        format_: str = "CSV",
        fields: Union[str, List[str]] = "all",
        starttm: int = None,
        endtm: int = None,
        **kwargs,
    ) -> dict:
        """
        Request to export the trades or ledgers of the user.

        - https://docs.kraken.com/rest/#operation/addExport

        :param report: Kind of report, one of: ``trades`` and ``ledgers``
        :type report: str
        :param format_: The export format of the requesting report, one of ``CSV`` and ``TSV`` (default: ``CSV``)
        :type format_: str
        :param fields: Optional - Fields to include in the report (default: ``all``)
        :type fields: str | List[str]
        :param starttm: Optional - Unix timestamp to start
        :type starttm: int | None
        :param endtm: optional - Unix timestamp of the last result
        :type endtm: int | None
        :return: A dictionary containing the export id
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.request_export_report(
            ...     report="ledgers", description="myLedgers1", format="CSV"
            ... )
            { 'id': 'GEHI' }
        """
        if report not in ["trades", "ledgers"]:
            raise ValueError('report must be one of "trades", "ledgers"')

        params = {
            "report": report,
            "description": description,
            "format": format_,
            "fields": self._to_str_list(fields),
        }
        params.update(kwargs)
        if starttm is not None:
            params["starttm"] = starttm
        if endtm is not None:
            params["endtm"] = endtm
        return self._request(method="POST", uri="/private/AddExport", params=params)

    def get_export_report_status(self, report: str) -> dict:
        """
        Get the status of the current pending report.

        - https://docs.kraken.com/rest/#operation/exportStatus

        :param report: Kind of report, one of: ``trades``, ``ledgers``
        :type report: str
        :return: Information about the pending report
        :rtype: List[dict]

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> response = user.request_export_report(
            ...     report="ledgers", description="myLedgers1", format="CSV"
            ... )
            { 'id': 'GEHI' }
            >>> user.get_export_report_status(report="ledgers")
            [
                {
                    'id': 'GEHI',
                    'descr': 'myLedgers1',
                    'format': 'CSV',
                    'report': 'ledgers',
                    'status': 'Queued',
                    'aclass': 'currency',
                    'fields': 'all',
                    'asset': 'all',
                    'subtype': 'all',
                    'starttm': '1680307200',
                    'endtm': '1680855267',
                    'createdtm': '1680855267',
                    'expiretm': '1682064867',
                    'completedtm': '0',
                    'datastarttm': '1680307200',
                    'dataendtm': '1680855267',
                    'flags': '0'
                }
            ]
        """
        if report not in ["trades", "ledgers"]:
            raise ValueError('report must be one of "trades", "ledgers"')
        return self._request(
            method="POST", uri="/private/ExportStatus", params={"report": report}
        )

    def retrieve_export(self, id_: str) -> dict:
        """
        Get the status of the requested report export by id. Can be used
        to save the transaction history to CSV.

        - https://docs.kraken.com/rest/#operation/retrieveExport

        :param id_: Id of the report that was requested
        :type id_: str
        :return: The reponse - a zipped report
        :rtype: ``requests.Response``

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> response = user.request_export_report(
            ...     report="ledgers", description="myLedgers1", format="CSV"
            ... )
            { 'id': 'GEHI' }
            >>> ledgers_data = user.retrieve_export(id_=response["id"])
            >>> with open("myExport.zip", "wb") as file:
            ...     for chunk in ledgers_data.iter_content(chunk_size=512):
            ...         if chunk:
            ...             file.write(chunk)

        """
        return self._request(
            method="POST",
            uri="/private/RetrieveExport",
            params={"id": id_},
            return_raw=True,
        )

    def delete_export_report(self, id_: str, type_: str) -> dict:
        """
        Delete a report from the Kraken server.

        - https://docs.kraken.com/rest/#operation/removeExport

        :param id_: The id of the report
        :type id_: str
        :param type_: The type of the export, one of: ``trades`` and ``ledgers``
        :type type_: str
        :return: Success or failure
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.delete_export_report(id_="GEHI", type_="trades")
            { 'delete': True }
        """
        return self._request(
            method="POST",
            uri="/private/RemoveExport",
            params={"id": id_, "type": type_},
        )

    def create_subaccount(self, username: str, email: str) -> dict:
        """
        Create a subaccount for trading. This is currently only available
        for institutional clients.

        - https://docs.kraken.com/rest/#tag/User-Subaccounts

        :param username: The username for the new subaccount
        :type username: str
        :param email: The E-Mail address for the new subaccount
        :type email: str
        :return: Success or failunre
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Example

            >>> from kraken.spot import User
            >>> user = User(key="api-key", secret="secret-key")
            >>> user.create_subaccount(username="user", email="user@domain.com")
            { 'result': True }
        """
        return self._request(
            method="POST",
            uri="/private/CreateSubaccount",
            params={"username": username, "email": email},
        )
