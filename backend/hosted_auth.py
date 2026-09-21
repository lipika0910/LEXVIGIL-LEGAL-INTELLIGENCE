"""Auth-only database facade for the existing tested PKCE/recovery routes.

This facade never creates schema. Its transaction helper enforces the
restricted auth login, private search path and transaction-local role.
"""
class HostedAuthDatabase:
    def __init__(self, transactions):
        self.transactions = transactions

    def begin(self):
        return self.transactions.transaction('auth')

    def connect(self):
        return self.transactions.transaction('auth')
