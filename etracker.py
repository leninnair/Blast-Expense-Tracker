import os
from datetime import datetime

import customtkinter as ctk
from ctkdateentry import CTkDateEntry
from CTkMessagebox import CTkMessagebox
from PIL import Image

from expenseDB import Expenses


class Trans_Form(ctk.CTkFrame): # Transaction form class. 
    def __init__(self, parent:ctk.widget):
        super().__init__(master=parent)
        self.master = parent
        self.columnconfigure((0,1,2), weight=1)
        self.rowconfigure((0,1,2,3,4,5), weight=1)
        self.current_trans_id = None
        self.build_form_ui()

    def build_form_ui(self): # Builds the transaction form.
        ctk.CTkLabel(self, text="DATE *", font=("Bahnschrift Semicondensed", 20)).grid(row=0, column=0, sticky="e", padx=20, pady=(20,0))
        self.date_val = ctk.StringVar()
        self.date = CTkDateEntry(self, bg_color="transparent", text_color="#ffffff",
                                font=("Helvetica", 18), width=600, variable=self.date_val)
        self.date.grid(row=0, column=1, columnspan=2, sticky="w", padx=20, pady=(20,0))
        self.traceids = {"date": 0}
        self.traceids["date"] = self.date_val.trace_add("write", lambda *args: self.master.format_date(self.date_val, self.date, self.traceids, "date"))

        ctk.CTkLabel(self, text="TYPE *", font=("Bahnschrift Semicondensed", 20)).grid(row=1, column=0, sticky="e", padx=20)
        self.type_var = ctk.StringVar()
        self.income_radio = ctk.CTkRadioButton(
            self,
            text="INCOME", font=("Helvetica", 18),
            value="Income",
            variable=self.type_var,
            fg_color="#ce2cff"
        )
        self.expense_radio = ctk.CTkRadioButton(
            self,
            text="EXPENSE",
            value="Expense",
            variable=self.type_var, font=("Helvetica", 18),
            fg_color="#ce2cff"
        )
        self.income_radio.grid(row=1, column=1, sticky="w", padx=50)
        self.expense_radio.grid(row=1, column=2, sticky="w", padx=50)
        
        ctk.CTkLabel(self, text="CATEGORY *", font=("Bahnschrift Semicondensed", 20)).grid(row=2, column=0, sticky="e", padx=20, pady=10)
        self.category = ctk.CTkEntry(self, width=600, font=("Helvetica", 18))
        self.category.grid(row=2, column=1, columnspan=2, sticky="w", padx=20)
        
        ctk.CTkLabel(self, text="AMOUNT *", 
            font=("Bahnschrift Semicondensed", 18)).grid(row=3, column=0, sticky="e", padx=20)
        self.amount = ctk.CTkEntry(self, width=600, placeholder_text="0.00", font=("Helvetica", 18))
        self.amount.grid(row=3, column=1, columnspan=2, sticky="w", padx=20)
        
        ctk.CTkLabel(self, text="DESCRIPTION", 
            font=("Bahnschrift Semicondensed", 18)).grid(row=4, column=0, sticky="e", padx=20)
        self.description = ctk.CTkTextbox(self, height=60, width=600, font=("Helvetica", 18))
        self.description.grid(row=4, column=1, columnspan=2, sticky="w", padx=20)

        ctk.CTkButton(self, text="SAVE", command=self.save_trans, 
            font=("Bahnschrift Semicondensed", 20)).grid(row=5, column=1, sticky="ew", padx=50, pady=(0,20))
        ctk.CTkButton(self, text="CANCEL", command=self.cancel_trans, 
            font=("Bahnschrift Semicondensed", 20)).grid(row=5, column=2, sticky="ew", padx=50, pady=(0,20))

    def validate_form(self):
        try:
            amount = float(self.amount.get())
        except ValueError:
            warning = CTkMessagebox(title="Invalid amount", message="Please input amount correctly.", icon="warning"
                            , option_1="Retry", option_2="Cancel")
            if warning.get() == "Retry":
                return
            else:
                self.cancel_trans()
                return
        type = self.type_var.get()
        if type != "Expense" and type != "Income":
            warning = CTkMessagebox(title="Invalid type", message="Please select the transaction type.", icon="warning"
                                        , option_1="Retry", option_2="Cancel")
            if warning.get() == "Retry":
                return
            else:
                self.cancel_trans()
                return
        category = self.category.get()

        date = self.date_val.get()
        if not date:
            warning = CTkMessagebox(title="Invalid date", message="Please input date correctly.", icon="warning"
                            , option_1="Retry", option_2="Cancel")
            if warning.get() == "Retry":
                return
            else:
                self.cancel_trans()
                return 
        if not category:
            warning = CTkMessagebox(title="Invalid category", message="Please input category correctly.", icon="warning"
                            , option_1="Retry", option_2="Cancel")
            if warning.get() == "Retry":
                return
            else:
                self.cancel_trans()
                return
        description = self.description.get("1.0", "end-1c")
        return (date, type, category, amount, description)
                    
    def save_trans(self):
        transaction = self.validate_form()
        if not self.current_trans_id:
            self.master.expenses.save_transaction(transaction)
        else:
            transaction += (self.current_trans_id,)
            self.master.expenses.update_transaction(transaction)
            self.current_trans_id = None
        self.master.build_summary()
        self.master.build_expense_table()
            
        self.reset_form()
     
    def cancel_trans(self): # Resets form and shows summary.
        self.reset_form()
        self.master.raise_frame(self.master.s_frame)

# Resets the form to default values.
    def reset_form(self):
        self.amount.set("")
        self.amount.configure(placeholder_text="0.00")
        self.date.variable.set("")
        self.income_radio.deselect()
        self.expense_radio.deselect()
        self.category.set("")
        self.description.delete("1.0", "end")

# Sets the form so that transaction can be edited.
    def edit_trans(self, expense):
        # Populate the form fields with the data of the selected transaction.
        date = datetime.strptime(expense[1], "%Y-%m-%d")
        date = date.strftime("%d/%m/%Y")
        self.date_val.set(date)
        self.category.set(expense[3])
        if expense[2] == "Income":
            self.income_radio.select()
        else:
            self.expense_radio.select()
        self.amount.set(expense[4])
        self.description.insert("1.0", text=expense[5])
        self.current_trans_id = expense[0]


class ExpenseTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.expenses = Expenses()
        self.logo_path = os.path.join(os.path.dirname(__file__), "static", "logo.png")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        self.title("Blast! Expense Tracker")
        self.geometry("1500x800")
        self.currency = self.csymbol(self.expenses.currency)
        self.build_topbar()
        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
    
    def build_ui(self): # Creates various UI elements via functions.
        # Configuring columns and rows
        self.columnconfigure(0, weight=0, minsize=300)
        self.columnconfigure(1, weight=10)
        self.rowconfigure(0, weight=1, uniform="theapp")
        self.rowconfigure(1, weight=5, uniform="theapp")
                
        self.build_sidebar()
        self.build_expense_table()
        self.build_form()
        self.build_summary()
        self.raise_frame(self.s_frame)
    
    def build_sidebar(self): # Creates the sidebar with buttons.
        if hasattr(self, "sidebar") and self.sidebar.winfo_exists():
            self.sidebar.destroy()
        self.sidebar = ctk.CTkFrame(self,
                                    corner_radius=0,
                                    fg_color="#6c2c77",
                                    border_width=0                                   
                                    )
        # Sidebar column and row configuration
        self.sidebar.columnconfigure(0, weight=1)
        self.sidebar.rowconfigure((0,1,2), weight=1)
        self.sidebar.rowconfigure(3, weight=1, minsize=150) # Sets minimum height for date pickers.
        self.sidebar.rowconfigure((4,5), weight=8)

        self.sidebar.grid(row=1, column=0, sticky="nesw")
        self.build_sidebar_buttons()
        self.build_currency_picker()  
    def build_sidebar_buttons(self): # Creates the buttons and date filter on the sidebar.
        ctk.CTkButton(self.sidebar, 
                      corner_radius=0,
                      font=("Segoe UI Bold", 20),
                      fg_color="#793286",
                      hover_color="#873795",
                      cursor="hand2",
                      text="Summary",
                      command=lambda: self.raise_frame(self.s_frame)
                      ).grid(row=0, column=0, sticky="nsew")
        ctk.CTkButton(self.sidebar,   
                      corner_radius=0,
                      font=("Segoe UI Bold", 20),
                      fg_color="#793286",
                      hover_color="#873795",
                      cursor="hand2",
                      text="Transactions",command=lambda: self.raise_frame(self.main),
                      ).grid(row=1, column=0, sticky="nsew")
        ctk.CTkButton(self.sidebar,  
                      corner_radius=0,
                      font=("Segoe UI Bold", 20),
                      fg_color="#793286",
                      hover_color="#873795",
                      cursor="hand2",
                      text="Add Transaction", command=lambda: self.raise_frame(self.trans_form)
                      ).grid(row=2, column=0, sticky="nsew")

        # Filter frame shows the date filters.
        self.filter_frame = ctk.CTkFrame(self.sidebar, bg_color="transparent", fg_color="transparent")
        self.filter_frame.grid(row=3, column=0, sticky = "nsew")
        self.filter_frame.rowconfigure((0,1,2), weight=1)
        self.filter_frame.columnconfigure(0, weight=1)
        ctk.CTkLabel(self.filter_frame, 
                             text="FROM",
                             font=("Segoe UI Bold", 14),
                             ).grid(row=0, column=0, sticky="sw", padx=10, pady=(10,0))
        
        self.from_date = ctk.StringVar(value=datetime.today().replace(day=1).strftime("%Y-%m-%d")) # Sets month start as the default.

        # Helps format the date on the field in yyyy-mm-dd format for ease of use. every time, date is picked, 
        # it's reformatted via format_date. Trace ID stores the autogenerated ID that traces changes to this field.
        self.traceids = {"from": 0, "to": 0}
        self.traceids["from"] = self.from_date.trace_add("write", lambda *args: self.format_date(self.from_date, self.from_fld, self.traceids, "from"))
        self.from_fld = CTkDateEntry(self.filter_frame, corner_radius=0, bg_color="#6c2c77", 
                                    fg_color="#873795", text_color="#ffffff", state="readonly",
                                    font=("Helvetica", 14, "bold"), width=120, variable=self.from_date)
        self.from_fld.grid(row=1, column=0, sticky="nw", padx=10)

        ctk.CTkLabel(self.filter_frame, 
                        text="TO",
                        font=("Segoe UI Bold", 14),
                        ).grid(row=0, column=0, sticky="se", padx=10, pady=(10,0))
        
        self.to_date = ctk.StringVar(value=datetime.today().strftime("%Y-%m-%d")) # sets month end as default.
        self.traceids["to"] = self.to_date.trace_add("write", lambda *args: self.format_date(self.to_date, self.to_fld, self.traceids, "to"))
        self.to_fld = CTkDateEntry(self.filter_frame, corner_radius=0, bg_color="#6c2c77", 
                                  fg_color="#873795", text_color="#ffffff", state="readonly",
                                    font=("Helvetica", 14, "bold"), width=120, variable=self.to_date
                                    )
        self.to_fld.grid(row=1, column=0, sticky="ne", padx=10)

        ctk.CTkButton(self.filter_frame,  
                      corner_radius=10,
                      font=("Segoe UI Bold", 20),
                      fg_color="#793286",
                      hover_color="#873795",
                      border_color="#792A87",
                      cursor="hand2",
                      text="Update", command=self.build_expense_table
                      ).grid(row=2, column=0)
        self.filter_frame.grid_remove()

# Formats the date so that it shows in ISO format.
    def format_date(self, date:ctk.StringVar, picker:CTkDateEntry, traceids: dict, key: str, *args):
        # The trace IDs are used to track changes on the field associated with the variable.
        trace_id = traceids[key]
        # Remove the trace when starting the process. Add back the trace after variable is updated to ISO format.
        date.trace_remove("write", trace_id)
        picker.entry.configure(state="normal")
        # Set the variable in ISO formatted date. Useful to do SELECT query in the database.
        if date.get() == "":
            picker.entry.set("")
        else:
            picker.entry.set(datetime.strptime(date.get(), r"%d/%m/%Y").date().isoformat())
        picker.entry.configure(state="readonly")

        trace_id = date.trace_add("write", lambda *args: self.format_date(date, picker, traceids, key))
        traceids[key] = trace_id

# Helps pick a currency or change it.
    def build_currency_picker(self):
        currency = self.expenses.get_currency()
        currency = ctk.StringVar(value=currency) # Default value INR
        ctk.CTkLabel(self.sidebar, 
                     text="Select Currency",
                     font=("Segoe UI Bold", 20),
                     ).grid(row=4, column=0, sticky="esw", pady=(50, 20))
        self.cur_option = ctk.CTkOptionMenu( # The option menu that displays currency selection.
            self.sidebar,
            values=["INR", "USD", "EUR", "GBP", "JPY", "CAD", "AUD"],
            variable=currency,
            width=220,
            height=40,
            corner_radius=10,
            font=("Segoe UI", 18),
            fg_color="#8e44ad",
            button_color="#6c3483",
            button_hover_color="#9b59b6",
            dropdown_fg_color="#873795",
            dropdown_hover_color="#ba6ac8",
            dropdown_text_color="white",
            dropdown_font=("Segoe UI", 16),
            text_color="white",
            command=self.change_currency
        )
        self.cur_option.grid(row=5, column=0, sticky="new", padx=(10,10))

# Shows the list of expenses taken from the database, for the month by default, on clicking the "Transactions" button.
    def build_expense_table(self):
        if hasattr(self, "main") and self.main.winfo_exists():
            self.main.destroy()
        self.main = ctk.CTkScrollableFrame(self, 
                        corner_radius=0)
        self.main.columnconfigure(0, weight=1)

        self.set_table_labels() # Creates the labels at the top of the expense table.

        from_date = self.from_date.get()
        to_date = self.to_date.get()
        expense_frames = {}

# from_date and to_date by default contains month start and end. 
        for idx, expense in enumerate(self.expenses.data_generator(start=from_date, end=to_date)):
            if idx % 2 == 0: # The background is alternated between two colors.
                background = "#ffffff"
            else:
                background = "#ebebeb"

            e_id = expense[0]
            # Expense_frame contains the data from each expense, along with the action buttons.
            expense_frames[e_id] = ctk.CTkFrame(self.main,bg_color="transparent",
                                         fg_color=background,
                                         corner_radius=0)

            # Setting columns relative weight as needed.
            expense_frames[e_id].columnconfigure(0, weight=2, uniform="contentgrid") # Date
            expense_frames[e_id].columnconfigure(1, weight=2, uniform="contentgrid") # Category
            expense_frames[e_id].columnconfigure(2, weight=3, uniform="contentgrid") # Amount
            expense_frames[e_id].columnconfigure(3, weight=5, uniform="contentgrid") # Description
            expense_frames[e_id].columnconfigure(4, weight=4, uniform="contentgrid") # Delete & edit buttons

            expense_frames[e_id].grid(row=idx+1, column=0, sticky="nsew")
                   
            ctk.CTkLabel(expense_frames[e_id], corner_radius=0, bg_color="transparent", # date value
                         text=expense[1], text_color="#1f1f1f",
                         font=("Segoe UI", 18)).grid(row=0, column=0, sticky="w", ipadx=10)

            # cat_box shows each category
            cat_box = ctk.CTkEntry(expense_frames[e_id], bg_color="transparent", fg_color="transparent",
                                border_width=0, font=("Segoe UI", 18), text_color="#1f1f1f")
            cat_box.insert(0, expense[3])
            cat_box.configure(state="readonly")
            cat_box.grid(row=0, column=1, sticky="ew")

            f_amount = f"{self.currency} {float(expense[4]):,.2f}" # Formats the amount (expense[3]) to have 2 decimalpts

            # amt_box displays the amount.
            amt_box = ctk.CTkEntry(expense_frames[e_id], bg_color="transparent", fg_color="transparent",
                                    font=("Impact", 24), border_width=0, 
                                    text_color="#cc0003" if expense[2] == "Expense" else "#09b000")
            amt_box.insert(0, f_amount)
            amt_box.configure(state="readonly")
            amt_box.grid(row=0, column=2, sticky="ew")

            # Description box
            desc_box = ctk.CTkTextbox(expense_frames[e_id], bg_color="transparent", height=60,
                                      fg_color="transparent", corner_radius=0, text_color="#333333",                                    
                                      font=("Segoe UI", 20, "italic"))
            desc_box.insert("1.0", text=expense[5])
            desc_box.configure(state="disabled")
            desc_box.grid(row=0, column=3, sticky="ew")

            # The edit button for each transaction. Populates the transaction form with the details of the
            # transaction and lets user change values.
            edit_btn = ctk.CTkButton(expense_frames[e_id], fg_color="#1d7989", hover_color="#3e909f",
                                                 text_color="white", 
                                                 text="Edit", width=80, 
                                                 command=lambda exp_id=expense[0]: (self.raise_frame(self.trans_form),
                                                     self.trans_form.edit_trans(self.expenses.get_transaction(exp_id))                                                     
                                                     )) 
            edit_btn.grid(row=0, column=4, sticky="w", padx=10)

            # Button to delete each transaction. Passes the transaction ID to delete the transaction.
            # Then grid-removes the frame that holds the transaction.
            del_btn = ctk.CTkButton(expense_frames[e_id], fg_color="#912E2E", hover_color="#9A4040",
                                     text_color="white", width=80,
                                     text="Delete", 
                                     command=lambda exp_id=expense[0]: (self.expenses.del_transaction(exp_id),
                                                                      expense_frames[exp_id].grid_remove(),
                                                                      self.build_summary(),
                                                                      self.raise_frame(self.main)
                                                                      )) 
            del_btn.grid(row=0, column=4, sticky="w", padx=100)

        self.main.grid(row=1, column=1, sticky="nsew") # Displays the main content/table.
        self.main.focus_set()
        self.filter_frame.grid() # Shows date filters (filter_frame) only when transaction page is shown.


# Creates the table labels at the top of the transaction table.        
    def set_table_labels(self):
        expense_top_frame = ctk.CTkFrame(self.main,bg_color="#333333", # The frame that displays the labels.
                                                 fg_color="#333333",
                                                 corner_radius=0)
        expense_top_frame.columnconfigure(0, weight=2, uniform="contentgrid") # Date
        expense_top_frame.columnconfigure(1, weight=2, uniform="contentgrid") # Category
        expense_top_frame.columnconfigure(2, weight=3, uniform="contentgrid") # Amount
        expense_top_frame.columnconfigure(3, weight=5, uniform="contentgrid") # Description
        expense_top_frame.columnconfigure(4, weight=4, uniform="contentgrid") # Actions (edit/delete)
        expense_top_frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(expense_top_frame, corner_radius=0, bg_color="transparent", # Date label
                        text="DATE", text_color="#ffffff",
                        font=("Impact", 18)).grid(row=0, column=0, sticky="w", ipady=20, ipadx=10)
        ctk.CTkLabel(expense_top_frame, corner_radius=0, bg_color="transparent", # Category label
                    text="CATEGORY", text_color="#ffffff",
                    font=("Impact", 18)).grid(row=0, 
                            column=1, rowspan=2,
                            sticky="w", ipady=20)
        ctk.CTkLabel(expense_top_frame, corner_radius=0, bg_color="transparent", # Amount label
                    text="AMOUNT", text_color="#ffffff",
                    font=("Impact", 18)).grid(row=0, 
                            column=2, rowspan=2,
                            sticky="w", ipady=20)
        ctk.CTkLabel(expense_top_frame, corner_radius=0, bg_color="transparent", # Description label
                    text="DESCRIPTION", text_color="#ffffff",
                    font=("Impact", 18)).grid(row=0, 
                            column=3, rowspan=2,
                            sticky="w", ipady=20)
        ctk.CTkLabel(expense_top_frame, corner_radius=0, bg_color="transparent", # Description label
                            text="ACTIONS", text_color="#ffffff",
                            font=("Impact", 18)).grid(row=0, 
                                    column=4, rowspan=2,
                                    sticky="w", ipady=20)

# Shows the summary of transactions. Displayed by default while opening app.
    def build_summary(self):
        if hasattr(self, "s_frame") and self.s_frame.winfo_exists():
            self.s_frame.destroy()
        self.s_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent", bg_color="transparent")
        self.s_frame.rowconfigure(0, weight=1)
        self.s_frame.columnconfigure(0, weight=1)
        self.s_frame.grid(row=1, column=1, sticky="nsew", ipadx=100, ipady=100)

        self.summary = self.expenses.summary_generator() # Refreshes summary every time new data is added.
        bal = self.summary["Balance"] # Naming variable for ease of use in label below.

# Styled summary box displays contents in green or red based on balance amount.
        self.summary_box = ctk.CTkFrame(self.s_frame, bg_color="transparent", 
            fg_color="#007a2b" if bal >= 0 else "#871f1f", corner_radius=20)
        self.summary_box.columnconfigure((0), weight=1)
        self.summary_box.rowconfigure((0,1,2), weight=1)
        self.summary_box.grid(row=0, column=0, pady=(20, 50))

        inc_summary = f"INCOME : {self.currency} {self.summary["Income"]:,.2f}"
        exp_summary = f"EXPENDITURE : {self.currency} {self.summary["Expense"]:,.2f}"
        bal_summary = f"BALANCE  :  {self.currency} {bal:,.2f}"

        ctk.CTkLabel(self.summary_box, text=inc_summary,  
                     font=("Impact", 36)).grid(row=0, column=0, pady=(30,0), padx=40, sticky="w")
    
        ctk.CTkLabel(self.summary_box, text=exp_summary,  
                     font=("Impact", 36)).grid(row=1, column=0, pady=20, padx=40, sticky="w")

        ctk.CTkLabel(self.summary_box, text=bal_summary,  
                             font=("Impact", 36)).grid(row=2, column=0, pady=(0,30), padx=40, sticky="w")

    def build_form(self): # Adds the "add transaction" form.
        if hasattr(self, "trans_frame") and self.trans_frame.winfo_exists():
            self.trans_frame.destroy()

        self.trans_form = Trans_Form(self)
        self.trans_form.grid(row=1, column=1, sticky="nsew", padx=(150,200), pady=80)

# Creates the top part of the tracker, where logo is displayed.
    def build_topbar(self):
        self.topbar = ctk.CTkFrame(self, corner_radius=0,
                                   fg_color="#560063")
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.topbar.columnconfigure(0, weight=1)
        self.topbar.rowconfigure(0, weight=1)

        self.logo = ctk.CTkImage(Image.open(self.logo_path), size=(307, 204))
        self.logo_base = ctk.CTkLabel(self.topbar, image=self.logo, text="", fg_color="#610067")
        self.logo_base.grid(row=0, column=0, sticky="nsew", ipady=50)

    @staticmethod
    def csymbol(option:str): # Returns the symbol associated with currency string.
        symbols = {
            "INR": "₹", "USD": "$", "GBP": "£", "EUR": "€", 
            "JPY": "¥", "CNY": "¥", "AUD": "$", "CAD": "$",
        }
        return symbols[option] # Returns the symbol associated with the currency string.
    
    def change_currency(self, option: str): #Changes the currency and alerts the user.
        self.currency = self.csymbol(option) #Gets the new currency symbol
        CTkMessagebox(self, message="Currency updated.", title="Currency")
        self.build_ui() # Rebuilds UI immediately with the new currency symbol.
        self.expenses.set_currency(option) # Changes the currency in the database.

# This raise function simply raises the corresponding frame to the top for quick display.
# Real update happens only when user adds or edits a transaction.
    def raise_frame(self, theframe):
        frames = [self.s_frame, self.trans_form, self.main, self.filter_frame]
        
        for frame in frames:
            if frame != theframe:
                frame.grid_remove()
        if theframe == self.main:
            self.filter_frame.grid()
        theframe.grid()
           
    def close_app(self): # Custom function called to close the app. Helps close the database.
        self.expenses.db.close()
        self.destroy()
        
if __name__ == "__main__": 
    etracker = ExpenseTracker()
    etracker.mainloop()