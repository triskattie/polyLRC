class EmailAlreadyExists(Exception):
    pass

class InvalidLogin(Exception):
    pass

class InvalidRefreshToken(Exception):
    pass

class InvalidAccessToken(Exception):
    pass

class WalletNotFound(Exception):
    pass

class FaucetCooldown(Exception):
    pass

class MissingPermission(Exception):
    pass

class MarketNotFound(Exception):
    pass

class MarketOpen(Exception):
    pass