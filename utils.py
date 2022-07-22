# Validate incoming data from user
def validate_loan_data(loan_data):
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