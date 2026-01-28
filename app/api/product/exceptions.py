

class ProductAlreadyExistsException(Exception):
    """Exception raised when a product already exists."""

    def __init__(self, description=None):
        self.status_code = 400
        self.description = description or "Authentication Error"

class ProductNotFoundException(Exception):
    """Exception raised when a product is not found."""

    def __init__(self, description=None):
        self.status_code = 404
        self.description = description or "Product Not Found"

class InvalidInventoryUpdateException(Exception):
    """Exception raised for invalid inventory updates."""

    def __init__(self, description=None):
        self.status_code = 400
        self.description = description or "Invalid Inventory Update"