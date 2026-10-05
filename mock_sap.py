INVOICES = {
    "SUP-2048": {
        "supplier": "Example Supplies",
        "amount": "£860.25",
        "approval_status": "Approved",
        "payment_status": "Scheduled",
        "payment_date": "8 September 2026",
    },
    "XY-908": {
        "supplier": "Example Trading",
        "amount": "£1,240.00",
        "approval_status": "Awaiting approval",
        "payment_status": "Not scheduled",
        "payment_date": None,
    },
    "INV-10291": {
        "supplier": "ABC Supplies",
        "amount": "£4,250.00",
        "approval_status": "Approved",
        "payment_status": "Paid",
        "payment_date": "28 August 2026",
    },
}


def find_invoice(invoice_number):
    if not invoice_number:
        return None

    cleaned_number = invoice_number.strip().upper()
    return INVOICES.get(cleaned_number)

def format_invoice_lookup(invoice_number):
    heading = "DEMO INVOICE RECORD — FICTIONAL DATA"

    if not invoice_number:
        return heading + "\nNo invoice reference was provided."

    invoice = find_invoice(invoice_number)

    if invoice is None:
        return (
            heading
            + "\nNo exact match in the demo records. Review manually."
        )

    date_label = (
        "Scheduled payment date"
        if invoice["payment_status"] == "Scheduled"
        else "Recorded payment date"
    )

    return "\n".join([
        heading,
        "Reference match only — verify supplier and office before use.",
        f"Invoice: {invoice_number.strip().upper()}",
        f"Supplier: {invoice['supplier']}",
        f"Record amount: {invoice['amount']}",
        f"Invoice approval status: {invoice['approval_status']}",
        f"Payment status: {invoice['payment_status']}",
        f"{date_label}: {invoice['payment_date'] or 'Not recorded'}",
    ])