#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Benjamin Thomas Schwertfeger
# GitHub: https://github.com/btschwertfeger

"""Module that implements the Kraken Futures Funding client"""

from __future__ import annotations

from typing import Optional, Union

from kraken.base_api import KrakenBaseFuturesAPI


class Funding(KrakenBaseFuturesAPI):
    """
    Class that implements the Kraken Futures Funding client

    If the sandbox environment is chosen, the keys must be generated from here:
    https://demo-futures.kraken.com/settings/api

    :param key: Futures API public key (default: ``""``)
    :type key: str, optional
    :param secret: Futures API secret key (default: ``""``)
    :type secret: str, optional
    :param url: Alternative URL to access the Futures Kraken API (default: https://futures.kraken.com)
    :type url: str, optional
    :param sandbox: If set to ``True`` the URL will be https://demo-futures.kraken.com (default: ``False``)
    :type sandbox: bool, optional

    .. code-block:: python
        :linenos:
        :caption: Futures Funding: Create the funding client

        >>> from kraken.futures import Funding
        >>> funding = Funding() # unauthenticated
        >>> funding = Funding(key="api-key", secret="secret-key") # authenticated

    .. code-block:: python
        :linenos:
        :caption: Futures Funding: Create the funding client as context manager

        >>> from kraken.futures import Funding
        >>> with Funding(key="api-key", secret="secret-key") as funding:
        ...     print(funding.get_historical_funding_rates(symbol="PI_XBTUSD"))
    """

    def __init__(
        self,
        key: str = "",
        secret: str = "",
        url: str = "",
        sandbox: bool = False,
    ) -> None:
        super().__init__(key=key, secret=secret, url=url, sandbox=sandbox)

    def __enter__(self: Funding) -> Funding:
        super().__enter__()
        return self

    def get_historical_funding_rates(self: Funding, symbol: str) -> dict:
        """
        Retrieve information about the historical funding rates of a specific ``symbol``

        - https://docs.futures.kraken.com/#http-api-trading-v3-api-historical-funding-rates-historicalfundingrates

        :param symbol: The futures symbol to filter for
        :type symbol: str
        :return: The funding rates for a specific asset/contract
        :rtype: dict

        .. code-block:: python
            :linenos:
            :caption: Futures Funding: Get the historical funding rates

            >>> from kraken.futures import Funding
            >>> Funding().get_historical_funding_rates(symbol="PI_XBTUSD")
            {
                'rates': [
                    {
                        'timestamp': '2019-02-27T16:00:00.000Z',
                        'fundingRate': 1.31656208775e-07,
                        'relativeFundingRate': 0.0005
                    }, {
                        'timestamp': '2019-02-27T20:00:00.000Z',
                        'fundingRate': 1.30695377827e-07,
                        'relativeFundingRate': 0.0005
                    }, ...
                ]
            }
        """
        return self._request(  # type: ignore[return-value]
            method="GET",
            uri="/derivatives/api/v4/historicalfundingrates",
            query_params={"symbol": symbol},
            auth=False,
        )

    def initiate_wallet_transfer(
        self: Funding,
        amount: Union[str, int, float],
        fromAccount: str,
        toAccount: str,
        unit: str,
    ) -> dict:
        """
        Submit a wallet transfer request to transfer funds between margin accounts.

        Requires the ``General API - Full Access`` and ``Withdrawal API - Full access``
        permissions in the API key settings.

        - https://docs.futures.kraken.com/#http-api-trading-v3-api-transfers-initiate-wallet-transfer

        :param amount: The volume to transfer
        :type amount: str | int | float
        :param fromAccount: The account to withdraw from
        :type fromAccount: str
        :param fromAccount: The account to deposit to
        :type fromAccount: str
        :param unit: The currency or asset to transfer
        :type unit: str

        .. code-block:: python
            :linenos:
            :caption: Futures Funding: Transfer funds between wallets

            >>> from kraken.futures import Funding
            >>> funding = Funding(key="api-key", secret="secret-key")
            >>> funding.initiate_wallet_transfer(
            ...     amount='100',
            ...     fromAccount='some cash or margin account',
            ...     toAccount='another cash or margin account',
            ...     unit='ADA'
            ... ))
            {
                'result': 'success',
                'serverTime': '2023-04-07T15:23:45.196Z"
            }
        """
        return self._request(  # type: ignore[return-value]
            method="POST",
            uri="/derivatives/api/v3/transfer",
            post_params={
                "amount": str(amount),
                "fromAccount": fromAccount,
                "toAccount": toAccount,
                "unit": unit,
            },
            auth=True,
        )

    def initiate_subaccount_transfer(
        self: Funding,
        amount: Union[str, int, float],
        fromAccount: str,
        fromUser: str,
        toAccount: str,
        toUser: str,
        unit: str,
    ) -> dict:
        """
        Submit a request to transfer funds between the regular and subaccount.

        Requires the ``General API - Full Access`` and ``Withdrawal API - Full access``
        permissions in the API key settings.

        - https://docs.futures.kraken.com/#http-api-trading-v3-api-transfers-initiate-sub-account-transfer

        :param amount: The volume to transfer
        :type amount: str | int | float
        :param fromAccount: The account to withdraw from
        :type fromAccount: str
        :param fromUser: The user account to transfer from
        :type fromUser: str
        :param toAccount: The account to deposit to
        :type toAccount: str
        :param unit: The asset to transfer
        :type unit: str

        .. code-block:: python
            :linenos:
            :caption: Futures Funding: Transfer funds between subaccounts

            >>> from kraken.futures import Funding
            >>> funding = Funding(key="api-key", secret="secret-key")
            >>> funding.initiate_subaccount_transfer(
            ...     amount='2',
            ...     fromAccount='MyCashWallet',
            ...     fromUser='Subaccount1',
            ...     toAccount='MyCashWallet',
            ...     toUser='Subaccount2',
            ...     unit='XBT'
            ... ))
        """
        return self._request(  # type: ignore[return-value]
            method="POST",
            uri="/derivatives/api/v3/transfer/subaccount",
            post_params={
                "amount": str(amount),
                "fromAccount": fromAccount,
                "fromUser": fromUser,
                "toAccount": toAccount,
                "toUser": toUser,
                "unit": unit,
            },
            auth=True,
        )

    def initiate_withdrawal_to_spot_wallet(
        self: Funding,
        amount: Union[str, int, float],
        currency: str,
        sourceWallet: Optional[str] = None,
        **kwargs: dict,
    ) -> dict:
        """
        Enables the transfer of funds between the futures and spot wallet.

        Requires the ``General API - Full Access`` and ``Withdrawal API - Full access``
        permissions in the API key settings.

        - https://docs.futures.kraken.com/#http-api-trading-v3-api-transfers-initiate-withdrawal-to-spot-wallet

        :param amount: The volume to transfer
        :type amount: str | int | float
        :param currency: The asset or currency to transfer
        :type currency: str
        :param sourceWallet: The wallet to withdraw from (default: ``cash``)
        :type sourceWallet: str, optional
        :raises ValueError: If this function is called within the sandbox/demo environment

        .. code-block:: python
            :linenos:
            :caption: Futures Funding: Transfer funds between Spot and Futures wallets

            >>> from kraken.futures import Funding
            >>> funding = Funding(key="api-key", secret="secret-key")
            >>> funding.initiate_withdrawal_to_spot_wallet(
            ...     amount=100,
            ...     currency='USDT',
            ...     sourceWallet='cash'
            ... ))
        """
        if self.sandbox:
            raise ValueError("This function is not available in sandbox mode.")
        params: dict = {
            "amount": str(amount),
            "currency": currency,
        }
        if sourceWallet is not None:
            params["sourceWallet"] = sourceWallet
        params.update(kwargs)
        return self._request(  # type: ignore[return-value]
            method="POST",
            uri="/derivatives/api/v3/withdrawal",
            post_params=params,
            auth=True,
        )


__all__ = ["Funding"]
