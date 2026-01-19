class BrokerBase:
    """
    Interface base de qualquer broker.
    O Engine só conhece esta interface.
    """

    def get_market_data(self):
        raise NotImplementedError

    def buy(self, action: dict) -> bool:
        raise NotImplementedError

    def sell(self, action: dict) -> bool:
        raise NotImplementedError
