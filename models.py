class Loan:
    id = None
    amount = None
    rate = None
    length = None
    monthly_payment = None

    # Initialize a new loan
    def __init__(self, id, amount, rate, length, monthly_payment):
        self.id = id
        self.amount = amount
        self.rate = rate
        self.length = length
        self.monthly_payment = monthly_payment

    # Quick method for easy JSON serialization of loans
    def toJSON(self):
        return {
            'id': self.id, 
            'amount': self.amount,
            'rate': self.rate,
            'length': self.length,
            'monthly_payment': self.monthly_payment
        }