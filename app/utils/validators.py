def validate_request(request):
    errors = []
    if request.requested_amount < 0:
        errors.append("requested_amount must be positive")
    return errors
