---
name: refund-processing
description: Steps for handling simulated refunds in our electronics-store demo.
---

# Simulated Refund Procedure

1. Look up the customer using lookup_customer.
2. Retrieve their orders using get_order_history.
3. Check that the requested order is Delivered.
4. Check that the refund amount is positive and within the order total.
5. Call process_refund with the customer ID, order ID, and amount.
6. Clearly explain that the result is a simulation:
   - No real money moved.
   - No stored balance changed.
   - This application cannot issue real refunds.

Keep the answer short. Do not offer real-payment processing or promise
payment timelines.