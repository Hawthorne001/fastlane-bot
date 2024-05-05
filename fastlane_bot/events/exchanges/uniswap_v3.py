"""
Contains the exchange class for UniswapV3. 

This class is responsible for handling UniswapV3 events and updating the state of the pools.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract, AsyncContract

from fastlane_bot.config.constants import AGNI_V3_NAME, PANCAKESWAP_V3_NAME, FUSIONX_V3_NAME, ECHODEX_V3_NAME, SECTA_V3_NAME
from fastlane_bot.data.abi import UNISWAP_V3_POOL_ABI, UNISWAP_V3_FACTORY_ABI, PANCAKESWAP_V3_POOL_ABI
from ..exchanges.base import Exchange
from ..pools.base import Pool
from ..interfaces.subscription import Subscription


@dataclass
class UniswapV3(Exchange):
    """
    UniswapV3 exchange class
    """
    base_exchange_name: str = "uniswap_v3"
    exchange_name: str = "uniswap_v3"
    router_address: str = None
    exchange_initialized: bool = False

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return UNISWAP_V3_POOL_ABI if self.exchange_name not in [PANCAKESWAP_V3_NAME, AGNI_V3_NAME, FUSIONX_V3_NAME, ECHODEX_V3_NAME, SECTA_V3_NAME] else PANCAKESWAP_V3_POOL_ABI

    @property
    def get_factory_abi(self):
        return UNISWAP_V3_FACTORY_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Swap] if self.exchange_initialized else []

    def get_subscriptions(self, contract: Contract) -> List[Subscription]:
        return [Subscription(contract.events.Swap)]

    async def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        fee = await contract.caller.fee()
        fee_float = float(fee) / 1e6
        return fee, fee_float

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.caller.token0()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.caller.token1()

    def get_pool_function(self, factory_contract: Contract):
        """ Function to get pools from Factory.
            This function is intended to be used with a Multicall. It fetches pools from a Uniswap V3 fork Factory contract.

            Args:
                factory_contract: The factory contract.

            Returns:
                The function.

            """
        return factory_contract.functions.getPool
