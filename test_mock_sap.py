from mock_sap import find_invoice

invoice = find_invoice("SUP-2048")
assert invoice is not None
assert invoice["payment_status"] == "Scheduled"
print("PASS: Known invoice found with Scheduled status.")

assert find_invoice(" sup-2048 ") == invoice
print("PASS: Extra spaces and lowercase handled.")

assert find_invoice("UNKNOWN-999") is None
print("PASS: Unknown invoice returns no match.")

assert find_invoice("") is None
assert find_invoice(None) is None
print("PASS: Missing invoice references handled.")

print("\nAll lookup tests passed.")
from mock_sap import format_invoice_lookup

print()
print(format_invoice_lookup("SUP-2048"))