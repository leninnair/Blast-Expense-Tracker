import os
from datetime import datetime

import customtkinter as ctk
from ctkdateentry import CTkDateEntry
from CTkMessagebox import CTkMessagebox
from expenseDB import Expenses
from PIL import Image


class Trans_Form(ctk.CTkFrame):
    def __init__(self, parent:ctk.widget):
        super().__init__(master=parent)
        self.master = parent
        self.columnconfigure((0,1,2), weight=1)
        self.rowconfigure((0,1,2,3,4,5), weight=1)
        self.build_form_ui()

    def build_form_ui(self):
        ctk.CTkLabel(self, text="DATE *", font=("Bahnschrift Semicondensed", 20)).grid(row=0, column=0, sticky="e", padx=20, pady=(20,0))
        self.date_val = ctk.StringVar()
        self.date = CTkDateEntry(self, bg_color="transparent", text_color="#ffffff",
                                font=("Helvetica", 18), width=600, variable=self.date_val)
        self.date.grid(row=0, column=1, columnspan=2, sticky="w", padx=20, pady=(20,0))

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

    def save_trans(self):
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
        date = datetime.strptime(date, r"%d/%m/%Y").date().isoformat()
        if not category:
            warning = CTkMessagebox(title="Invalid category", message="Please input category correctly.", icon="warning"
                            , option_1="Retry", option_2="Cancel")
            if warning.get() == "Retry":
                return
            else:
                self.cancel_trans()
        description = self.description.get("1.0", "end-1c")
        transaction = (date, type, category, amount, description)
        self.master.expenses.save_transaction(transaction)
        self.master.build_expense_table()
        self.master.build_summary()
        self.reset_form()
     
    def cancel_trans(self):
        self.reset_form()
        self.master.raise_summary()

# Resets the form to default values.
    def reset_form(self):
        self.amount.set("")
        self.amount.configure(placeholder_text="0.00")
        self.date.variable.set("")
        self.income_radio.deselect()
        self.expense_radio.deselect()
        self.category.set("")
        self.description.delete("1.0", "end")

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
        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.close_app)
    
    def build_ui(self):
        # Configuring columns and rows
        self.columnconfigure(0, weight=0, minsize=300)
        self.columnconfigure(1, weight=10)
        self.rowconfigure(0, weight=1, uniform="theapp")
        self.rowconfigure(1, weight=5, uniform="theapp")
                
        self.build_sidebar()
        self.build_topbar()
        self.build_expense_table()
        self.build_form()
        self.build_summary()
    
    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self,
                                    corner_radius=0,
                                    fg_color="#6c2c77",
                                    border_width=0                                   
                                    )
        # Sidebar column and row configuration
        self.sidebar.columnconfigure(0, weight=1)
        self.sidebar.rowconfigure((0,1,2), weight=1)
        self.sidebar.rowconfigure((3,4), weight=8)

        self.sidebar.grid(row=1, column=0, sticky="nesw")
        self.build_sidebar_buttons()
        self.build_currency_picker()  
    def build_sidebar_buttons(self):
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
# Helps pick a currency or change it.
    def build_currency_picker(self):
        currency = self.expenses.get_currency()
        currency = ctk.StringVar(value=currency) # Default value INR
        ctk.CTkLabel(self.sidebar, 
                     text="Select Currency",
                     font=("Segoe UI Bold", 20),
                     ).grid(row=3, column=0, sticky="esw", pady=(50, 20))
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
        self.cur_option.grid(row=4, column=0, sticky="new", padx=(10,10))

# Shows the list of expenses taken from the database, for the month by default, on clicking the "Transactions" button.
    def build_expense_table(self):
        if hasattr(self, "main") and self.main.winfo_exists():
            self.main.destroy()
        self.main = ctk.CTkScrollableFrame(self, 
                        corner_radius=0)
        self.main.columnconfigure(0, weight=1)
        #self.main.rowconfigure(tuple(range(20)), weight=1)

        self.set_table_labels() # Creates the labels at the top of the expense table.

        for idx, expense in enumerate(self.expenses.data_generator()):
            if idx % 2 == 0:
                background = "#ffffff"
            else:
                background = "#ebebeb"
            expense_frame = ctk.CTkFrame(self.main,bg_color="transparent",
                                         fg_color=background,
                                         corner_radius=0)

            # Setting columns relative weight as needed.
            expense_frame.columnconfigure(0, weight=1, uniform="contentgrid")
            expense_frame.columnconfigure(1, weight=2, uniform="contentgrid")
            expense_frame.columnconfigure(2, weight=3, uniform="contentgrid")
            expense_frame.columnconfigure(3, weight=5, uniform="contentgrid")

            expense_frame.grid(row=idx+1, column=0, sticky="nsew")

            
            
            ctk.CTkLabel(expense_frame, corner_radius=0, bg_color="transparent", # date value
                         text=expense[0], text_color="#1f1f1f",
                         font=("Segoe UI", 18)).grid(row=0, column=0, sticky="w", ipadx=10)

            # cat_box shows each category
            cat_box = ctk.CTkEntry(expense_frame, bg_color="transparent", fg_color="transparent",
                                border_width=0, font=("Segoe UI", 18), text_color="#1f1f1f")
            cat_box.insert(0, expense[2])
            cat_box.configure(state="readonly")
            cat_box.grid(row=0, column=1, sticky="ew")


            f_amount = f"{self.currency} {float(expense[3]):,.2f}" # Formats the amount (expense[3]) to have 2 decimalpts

            # amt_box displays the amount.
            amt_box = ctk.CTkEntry(expense_frame, bg_color="transparent", fg_color="transparent",
                                    font=("Impact", 24), border_width=0, 
                                    text_color="#cc0003" if expense[1] == "Expense" else "#09b000")
            amt_box.insert(0, f_amount)
            amt_box.configure(state="readonly")
            amt_box.grid(row=0, column=2, sticky="ew")


            desc_box = ctk.CTkTextbox(expense_frame, bg_color="transparent", height=60,
                                      fg_color="transparent", corner_radius=0, text_color="#333333",                                    
                                      font=("Segoe UI", 20, "italic"))
            desc_box.insert("1.0", text=expense[4])
            desc_box.configure(state="disabled")
            desc_box.grid(row=0, column=3, sticky="ew")

        self.main.grid(row=1, column=1, sticky="nsew") # Displays the main content/table.
        self.main.focus_set()

# Creates the top table labels of the transaction list table.        
    def set_table_labels(self):
        expense_top_frame = ctk.CTkFrame(self.main,bg_color="#333333", # The frame that displays the labels.
                                                 fg_color="#333333",
                                                 corner_radius=0)
        expense_top_frame.columnconfigure(0, weight=1, uniform="contentgrid")
        expense_top_frame.columnconfigure(1, weight=2, uniform="contentgrid")
        expense_top_frame.columnconfigure(2, weight=3, uniform="contentgrid")
        expense_top_frame.columnconfigure(3, weight=5, uniform="contentgrid")
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

# Shows the summary on clicking the "Summary" button. Displayed by default while opening app.
    def build_summary(self):
        if hasattr(self, "s_frame") and self.s_frame.winfo_exists():
            self.s_frame.destroy()
        self.s_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent", bg_color="transparent")
        self.s_frame.rowconfigure(0, weight=1)
        self.s_frame.columnconfigure(0, weight=1)
        self.s_frame.grid(row=1, column=1, sticky="nsew", ipadx=100, ipady=100)

        self.summary = self.expenses.summary_generator() # Refreshes summary every time new data is added.
        bal = self.summary["Balance"] # Naming variable for ease of use in label below.

        self.summary_box = ctk.CTkFrame(self.s_frame, bg_color="transparent", 
            fg_color="#007a2b" if bal > 0 else "#871f1f", corner_radius=20)
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

    def build_form(self):
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
        frames = [self.s_frame, self.trans_form, self.main]
        for frame in frames:
            if frame != theframe:
                frame.grid_remove()
        theframe.grid()
           
    def close_app(self):
        self.expenses.db.close()
        self.destroy()
        
if __name__ == "__main__":
    tracker = ExpenseTracker()
    tracker.mainloop()