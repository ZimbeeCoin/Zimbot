# src/finance/dependencies.py
from typing import Generator

from finance.client.finance_data_client import FinanceClient
from finance.internal.analysis import AnalysisEngine
from finance.internal.coinapi import CoinAPIClient
from finance.internal.livecoinwatch import LiveCoinWatchClient

finance_client_instance = FinanceClient()


def get_finance_client() -> FinanceClient:
    """
    Dependency provider for FinanceClient.
    Ensures that the same instance is used throughout the request lifecycle.
    """
    return finance_client_instance
