class BaseProvider:
    def fetch_balance(self, account):
        """
        Every provoder module must override this
        """
        raise NotImplementedError