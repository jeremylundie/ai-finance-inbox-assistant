import queue
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import openai
from mock_sap import format_invoice_lookup
from finance_ai import analyse_email_fields, format_analysis

results = queue.Queue()
completed_result = None


def show_result(text):
    result_box.config(state="normal")
    result_box.delete("1.0", tk.END)
    result_box.insert("1.0", text)
    result_box.config(state="disabled")


def reset_copy():
    global completed_result
    completed_result = None
    copy_button.config(state="disabled")
    acknowledgement_button.config(state="disabled")
    for value in detail_values.values():
        value.set("—")

    for value in detail_values.values():
        value.set("—")

def run_analysis(email_text):
    try:
        analysis = analyse_email_fields(email_text)
        results.put((True, analysis))
        return

    except openai.AuthenticationError:
        message = (
            "OpenAI could not accept the API key. "
            "Check the key in your .env file, then restart the app. "
            "Keep the key private."
        )

    except openai.PermissionDeniedError:
        message = (
            "Your API account does not have permission for this request. "
            "Check the project's API-key and model permissions."
        )

    except openai.RateLimitError as error:
        if getattr(error, "code", None) == "insufficient_quota":
            message = (
                "The API account has no available quota. "
                "Check its credit balance and billing limits."
            )
        else:
            message = (
                "An API usage limit was reached. "
                "Wait a minute before trying again. "
                "If it continues, check your account's usage and billing limits."
            )

    except openai.APITimeoutError:
        message = (
            "The AI request timed out. No complete result was received. "
            "Wait a moment before trying again."
        )

    except openai.APIConnectionError:
        message = (
            "Could not connect to OpenAI. "
            "Check your internet connection. "
            "If other websites work, the service may be temporarily unavailable."
        )

    except openai.InternalServerError:
        message = (
            "OpenAI encountered a server error. "
            "Please try again later."
        )

    except openai.APIStatusError:
        message = (
            "OpenAI could not process this request. "
            "Check the model and request settings before trying again."
        )

    except ValueError:
        message = (
            "The email or AI response could not be processed. "
            "Check that the email is not blank and is under 12,000 characters. "
            "If it is, the AI response may not match the expected format."
        )

    except RuntimeError:
        message = (
            "The AI did not return a complete, usable analysis. "
            "Review the email manually or try again later."
        )

    except Exception:
        message = (
            "An unexpected application error occurred. "
            "No usable analysis is available. "
            "Restart the app; if it happens again, we will investigate."
        )

    results.put((False, message))

def start_analysis():
    reset_copy()
    email_text = email_box.get("1.0", "end-1c").strip()

    if not email_text:
        show_result("Please enter an email first.")
        status.config(text="Email required")
        return

    if len(email_text) > 12000:
        show_result("Please keep the email under 12,000 characters.")
        status.config(text="Email too long")
        return

    analyse_button.config(state="disabled")
    clear_button.config(state="disabled")
    email_box.config(state="disabled")
    status.config(text="Analysing…")
    show_result("Waiting for the AI response…")

    threading.Thread(
        target=run_analysis,
        args=(email_text,),
        daemon=True,
    ).start()


def check_results():
    global completed_result

    try:
        success, result = results.get_nowait()
    except queue.Empty:
        pass
    else:
        if success:
            completed_result = format_analysis(result)
            demo_record = format_invoice_lookup(result.invoice_number)
            completed_result += "\n\n" + demo_record
            action_and_reply = completed_result.split(
                "ACTION REQUIRED\n", 1
            )[1]
            show_result("ACTION REQUIRED\n" + action_and_reply)

            detail_values["Category"].set(result.category)
            detail_values["Sender"].set(
                result.sender_name or "Not provided"
            )
            detail_values["Invoice number"].set(
                result.invoice_number or "Not provided"
            )
            detail_values["Amount mentioned"].set(
                result.amount_mentioned or "Not provided"
            )

            copy_button.config(state="normal")
            acknowledgement_button.config(
                state=(
                    "disabled"
                    if result.category == "Needs manual review"
                    else "normal"
                )
            )
            status.config(text="Done — review the result.")
        else:
            reset_copy()
            show_result(result)
            status.config(text="Error")

        analyse_button.config(state="normal")
        clear_button.config(state="normal")
        email_box.config(state="normal")

    window.after(100, check_results)


def copy_acknowledgement():
    if completed_result is None:
        return
    if detail_values["Category"].get() == "Needs manual review":
        return

    acknowledgement = (
        "Hello,\n\n"
        "Thank you for your email. "
        "We acknowledge receipt of your enquiry.\n\n"
        "Kind regards,\n"
        "Accounts Team"
    )
    window.clipboard_clear()
    window.clipboard_append(acknowledgement)
    status.config(
        text="Acknowledgement copied — review before sending."
    )
def copy_results():
    if completed_result is None:
        return

    window.clipboard_clear()
    window.clipboard_append(completed_result)
    status.config(text="Completed results copied to clipboard.")


def clear_fields():
    if str(analyse_button["state"]) == "disabled":
        return

    reset_copy()
    email_box.delete("1.0", tk.END)
    show_result("")
    status.config(text="Ready")
    email_box.focus_set()

def on_email_changed(event=None):
    if not email_box.edit_modified():
        return

    email_box.edit_modified(False)

    if completed_result is None:
        return

    reset_copy()
    show_result("")
    status.config(text="Email changed — analyse again.")

window = tk.Tk()
window.title("Finance Inbox Assistant")
window.geometry("850x700")

frame = ttk.Frame(window, padding=20)
frame.pack(fill="both", expand=True)

ttk.Label(
    frame,
    text="Finance Inbox Assistant",
    font=("Segoe UI", 20, "bold"),
).pack(anchor="w")

ttk.Label(
    frame,
    text=(
        "Use made-up emails. Each analysis sends the text "
        "to OpenAI and uses API credit."
    ),
    wraplength=760,
).pack(anchor="w", pady=(15, 5))

email_box = ScrolledText(frame, height=5, wrap="word")
email_box.pack(fill="x")

analyse_button = ttk.Button(
    frame,
    text="Analyse email",
    command=start_analysis,
)
analyse_button.pack(anchor="w", pady=(15, 5))

status = ttk.Label(frame, text="Ready")
status.pack(anchor="w", pady=(0, 10))

ttk.Label(
    frame,
    text="Results — review before use",
).pack(anchor="w")

result_box = ScrolledText(
    frame,
    height=8,
    wrap="word",
    state="disabled",
)
details_frame = ttk.Frame(frame)
details_frame.pack(fill="x", pady=(5, 10))

detail_values = {}

for row, heading in enumerate([
    "Category",
    "Sender",
    "Invoice number",
    "Amount mentioned",
]):
    ttk.Label(
        details_frame,
        text=heading + ":",
    ).grid(row=row, column=0, sticky="w", padx=(0, 15), pady=3)

    value = tk.StringVar(value="—")
    detail_values[heading] = value

    ttk.Label(
        details_frame,
        textvariable=value,
        wraplength=600,
    ).grid(row=row, column=1, sticky="w", pady=3)

result_box.pack(fill="both", expand=True, pady=(5, 0))

button_row = ttk.Frame(frame)
button_row.pack(fill="x", pady=(10, 0))

copy_button = ttk.Button(
    button_row,
    text="Copy results",
    command=copy_results,
    state="disabled",
)
copy_button.pack(side="left")
acknowledgement_button = ttk.Button(
    button_row,
    text="Copy acknowledgement",
    command=copy_acknowledgement,
    state="disabled",
)
acknowledgement_button.pack(side="left", padx=(10, 0))
clear_button = ttk.Button(
    button_row,
    text="Clear",
    command=clear_fields,
)
clear_button.pack(side="left", padx=(10, 0))

email_box.edit_modified(False)
email_box.bind("<<Modified>>", on_email_changed)

window.after(100, check_results)
window.mainloop()
from mock_sap import format_invoice_lookup