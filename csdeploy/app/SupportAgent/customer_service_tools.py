# Adapted from the AWS Strands workshop, Module 1.

from strands import tool

CUSTOMERS = {
    "C-1001": {
        "name": "Anika Sharma",
        "email": "anika@example.test",
    },
    "C-1002": {
        "name": "Rohan Mehta",
        "email": "rohan@example.test",
    },
}

@tool
def lookup_customer(customer_id: str) -> str:
    """Retrieve sample customer details using an ID such as C-1001."""
    print(f"[TOOL] lookup_customer called for {customer_id}")

    customer = CUSTOMERS.get(customer_id)

    if customer is None:
        return f"No customer found with ID {customer_id}."

    return (
        f"Customer ID: {customer_id}\n"
        f"Name: {customer['name']}\n"
        f"Email: {customer['email']}"
    )

ORDERS = {
    "C-1001": [
        {
            "order_id": "ORD-5521",
            "item": "Wireless Headphones",
            "amount": 79.99,
            "status": "Delivered",
        },
        {
            "order_id": "ORD-5488",
            "item": "USB-C Hub",
            "amount": 45.00,
            "status": "Shipped",
        },
    ],
}


@tool
def get_order_history(customer_id: str) -> str:
    """Retrieve sample orders and their statuses for a customer."""
    print(f"[TOOL] get_order_history called for {customer_id}")

    orders = ORDERS.get(customer_id)

    if not orders:
        return f"No orders found for customer {customer_id}."

    lines = []
    for order in orders:
        lines.append(
            f"{order['order_id']}: {order['item']} | "
            f"USD {order['amount']:.2f} | {order['status']}"
        )

    return "\n".join(lines)

@tool
def process_refund(customer_id: str, order_id: str, amount: float) -> str:
    """Simulate a refund for a customer's delivered order. No money moves."""
    print(f"[TOOL] process_refund called for {order_id}")

    for order in ORDERS.get(customer_id, []):
        if order["order_id"] != order_id:
            continue

        if order["status"] != "Delivered":
            return "Refund rejected: the order must be delivered."

        if not 0 < amount <= order["amount"]:
            return "Refund rejected: amount must be positive and within the order total."

        return (
            f"SIMULATION ONLY: USD {amount:.2f} refund for {order_id}. "
            "No real money moved and no stored balance was changed."
        )

    return "Refund rejected: order not found for this customer."