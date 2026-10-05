import re
print("Finance Inbox AI — V0.1")

email_text = """
Hi Accounts,

Could you send me a copy of our latest statement?

Thanks,
ABC Supplies
"""

print(email_text)

email_lower = email_text.lower()

if "invoice" in email_lower and "payment" in email_lower:
    category = "Possible supplier payment query"
    action = "Check invoice and payment status"
else:
    category = "Needs manual review"
    action = "Read the email and decide what is needed"

print("CATEGORY:", category)
print("ACTION REQUIRED:", action)
invoice_match = re.search(r"\bINV-\d+\b", email_text, re.IGNORECASE)

if invoice_match:
    invoice_number = invoice_match.group()
else:
    invoice_number = "Not found"

print("INVOICE NUMBER:", invoice_number)

amount_match = re.search(r"£\s*\d[\d,]*(?:\.\d{2})?", email_text)

if amount_match:
    amount = amount_match.group()
else:
    amount = "Not found"

print("AMOUNT MENTIONED:", amount)

if category == "Possible supplier payment query" and invoice_number != "Not found":
    draft_reply = f"""
Hi,

Thank you for your query regarding invoice {invoice_number}.
We have received your request for a payment update.

Kind regards,
Accounts Payable
"""
else:
    draft_reply = "Please review the email and write a response manually."

print("\nDRAFT REPLY — REVIEW BEFORE SENDING:")
print(draft_reply)