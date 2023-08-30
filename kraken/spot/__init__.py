#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# GitHub: https://github.com/btschwertfeger

"""Module that provides the Spot REST clients and utility functions."""

# pylint: disable=unused-import
from kraken.spot.funding import Funding
from kraken.spot.market import Market
from kraken.spot.orderbook_v1 import OrderbookClientV1
from kraken.spot.orderbook_v2 import OrderbookClientV2
from kraken.spot.staking import Staking
from kraken.spot.trade import Trade
from kraken.spot.user import User
from kraken.spot.websocket_v1 import KrakenSpotWSClient
from kraken.spot.websocket_v2 import KrakenSpotWSClientV2

__all__ = [
    "Funding",
    "Market",
    "Staking",
    "Trade",
    "User",
    "OrderbookClientV1",
    "OrderbookClientV2",
    "KrakenSpotWSClient",
    "KrakenSpotWSClientV2",
]
