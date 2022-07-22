class Loan:
    amount = None
    rate = None
    length = None
    monthly_payment = None

    # Initialize a new loan
    def __init__(self, loan_data):
        # Validate that the necessary data is provided
        (valid_data, error_message) = self.validate_loan_data(loan_data)
        if valid_data:
            self.amount = loan_data['amount']
            self.rate = loan_data['rate']
            self.length = loan_data['length']
            self.monthly_payment = loan_data['monthly_payment']
        # Throw an error if there's invalid data
        else:
            raise ValueError(error_message)

    # Data validation method
    def validate_loan_data(self, loan_data):
        if loan_data is None:
            return (False, "No loan data provided")
        if 'amount' not in loan_data:
            return (False, "No amount provided")
        if 'rate' not in loan_data:
            return (False, "No interest rate provided")
        if 'length' not in loan_data:
            return (False, "No length of loan provided")
        if 'monthly_payment' not in loan_data:
            return (False, "No monthly payment amount provided")
        return (True, None)