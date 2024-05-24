import os
import tkinter as tk
from tkinter import messagebox, ttk, Text, Button
from tkcalendar import DateEntry
import pandas as pd
from pymongo import MongoClient
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import base64
import webbrowser
from plotly import graph_objs as go
from plotly.subplots import make_subplots


# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
form_data_collection = db['formdatas']
users_collection = db['users']

# Initialize Tkinter window
window = tk.Tk()
window.title('Hazardous Waste Management Form')
window.geometry("600x400")

def center_window(window, width=300, height=200):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def signup_page():
    signup_window = tk.Toplevel(window)
    signup_window.title('Signup')
    signup_window.geometry("400x200")

    def register_user():
        username = username_entry.get()
        password = password_entry.get()
        users_collection.insert_one({'username': username, 'password': password})
        messagebox.showinfo('Success', 'Signup successful! Please login.')
        signup_window.destroy()
        login_page()

    username_label = ttk.Label(signup_window, text='Username:')
    username_label.pack()
    username_entry = ttk.Entry(signup_window)
    username_entry.pack()

    password_label = ttk.Label(signup_window, text='Password:')
    password_label.pack()
    password_entry = ttk.Entry(signup_window, show='*')
    password_entry.pack()

    signup_button = ttk.Button(signup_window, text='Signup', command=register_user)
    signup_button.pack()

def login_page():
    login_window = tk.Toplevel(window)
    login_window.title('Login')
    login_window.geometry("400x200")

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            messagebox.showinfo('Success', 'Login successful!')
            login_window.destroy()
            show_main_menu()
        else:
            messagebox.showerror('Error', 'Invalid username or password.')

    username_label = ttk.Label(login_window, text='Username:')
    username_label.pack()
    username_entry = ttk.Entry(login_window)
    username_entry.pack()

    password_label = ttk.Label(login_window, text='Password:')
    password_label.pack()
    password_entry = ttk.Entry(login_window, show='*')
    password_entry.pack()

    login_button = ttk.Button(login_window, text='Login', command=validate_login)
    login_button.pack()

def show_main_menu():
    main_menu_window = tk.Toplevel(window)
    main_menu_window.title('Main Menu')
    main_menu_window.geometry("400x300")

    data_entry_button = ttk.Button(main_menu_window, text='Data Entry', command=main_app)
    data_entry_button.pack()

    view_data_button = ttk.Button(main_menu_window, text='View Data', command=view_data_page)
    view_data_button.pack()

    logout_button = ttk.Button(main_menu_window, text='Logout', command=window.destroy)
    logout_button.pack()

def main_app():
    main_window = tk.Toplevel(window)
    main_window.title('Hazardous Waste Management Form')
    main_window.geometry("800x600") 

    date_label = ttk.Label(main_window, text='Date:')
    date_label.grid(row=0, column=0, padx=10, pady=10)
    selected_date = DateEntry(main_window, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    selected_date.grid(row=0, column=1, padx=10, pady=10)

    # Function to format date before storing
    def get_formatted_date():
        return selected_date.get_date().strftime('%Y-%m-%d')

    # Select Division Dropdown
    division_label = ttk.Label(main_window, text='Select Division:')
    division_label.grid(row=1, column=0, padx=10, pady=10)
    division_options = ['GD ENGINE', 'TNGA ENGINE', 'Auto Parts', 'Utilities']
    selected_division = ttk.Combobox(main_window, values=division_options)
    selected_division.grid(row=1, column=1, padx=10, pady=10)

    # Input Fields - Organized in 2 Columns
    input_labels = [
        ("Used oil from shopfloor", "1"),
        ("Used glove and cloth", "2"),
        ("Compressor filters", "3"),
        ("Band/oiled filter papers", "4"),
        ("Paint waste", "5"),
        ("Adhesive (FIPG)", "6"),
        ("DG Chimney", "7"),
        ("Softner resin", "8"),
        ("Carbuoys", "9"),
        ("Metal barrels", "10"),
        ("Chemical sludge", "11"),
        ("Skimmed oil", "12"),
        ("Grinding Muck", "13"),
        ("Fuel Filters", "14"),
        ("Lapping Tape", "15"),
        ("Epoxy Waste", "16"),
        ("Test Bench Chimney", "17"),
        ("Plastic Barrels", "18"),
        ("Paint Containers", "19"),
        ("Oil Emulsion", "20"),
        ("DG Filers", "21"),
        ("Prowipe Paper", "22"),
        ("Canteen Chimney", "23"),
        ("Metal Buckets", "24"),
        ("Spray Containers", "25"),
        ("Saw Dust", "26"),
        ("Residue with Oil", "27"),
        ("Plastic Buckets", "28"),
    ]

    row_counter = 2
    column_counter = 0
    input_entries = {}  # Dictionary to store input entry widgets

    for label, id in input_labels:
        label_widget = ttk.Label(main_window, text=label)
        label_widget.grid(row=row_counter, column=column_counter, padx=10, pady=5)
        input_entry = ttk.Entry(main_window)
        input_entry.grid(row=row_counter, column=column_counter + 1, padx=10, pady=5)
        input_entries[id] = input_entry  # Add entry widget to the dictionary
        column_counter += 2
        if column_counter >= 4:  # Adjust column count for every 2 fields
            column_counter = 0
            row_counter += 1

    # Submit Button
    def submit_form():
        # Get the entered date and selected division
        form_data = {
            "Date": selected_date.get(),
            "Division": selected_division.get(),
        }

        # Convert input values to floats and handle empty strings as 0
        for label, id in input_labels:
            input_value = input_entries[id].get()
            input_value = float(input_value) if input_value else 0
            form_data[label] = input_value

        # Insert form data into the MongoDB collection
        form_data_collection.insert_one(form_data)

        # Show success message and optionally clear the input fields
        messagebox.showinfo("Success", "Form data submitted and stored in MongoDB!")
        selected_date.delete(0, tk.END)
        selected_division.set('')
        for entry in input_entries.values():
            entry.delete(0, tk.END)

    submit_button = ttk.Button(main_window, text='Submit', command=submit_form)
    submit_button.grid(row=row_counter, column=0, columnspan=2, pady=10)
    logout_button = ttk.Button(main_window, text='Logout', command=window.destroy)
    logout_button.grid(row=row_counter, column=3, columnspan=2, pady=10)

def view_data_page():
    view_data_window = tk.Toplevel(window)
    view_data_window.title('View Data')
    view_data_window.geometry("800x600")
    # Retrieve data from MongoDB
    form_data_cursor = form_data_collection.find()
    form_data_list = list(form_data_cursor)
    data = pd.DataFrame(form_data_list)

    # Convert 'Date' column to datetime format
    data['Date'] = pd.to_datetime(data['Date'])

    # Display data in a structured table format using DataFrameViewer
    data_viewer = ttk.Treeview(view_data_window)
    data_viewer['columns'] = list(data.columns)
    data_viewer['show'] = 'headings'  # Show only the column headers

    # Add column headings
    for col in data_viewer['columns']:
        data_viewer.heading(col, text=col)

    # Add data rows
    for index, row in data.iterrows():
        data_viewer.insert('', 'end', values=list(row))

    data_viewer.pack(padx=10, pady=10)

    # Button to download data as CSV
    def download_data():
        data.to_csv('mongodb_data.csv', index=False)
        messagebox.showinfo('Download', 'Data downloaded successfully as CSV.')

    download_button = Button(view_data_window, text='Download Data', command=download_data)
    download_button.pack(pady=10)

    # Dropdown menu to select specific category
    categories = [
        "Used oil (5.1) - Used oil from shopfloor, Skimmed oil",
        "Wastes containing oil (5.2) - Used Gloves & Cloth, Grinding muck, Oil emulsion, Saw dust, Compressor filters, Fuel filters, DG filters, Residue with oil, Band/oiled filter paper, Lapping tape, Prowipe paper",
        "Process waste (21.1) - Paint waste, Epoxy waste",
        "Wastes or residues (23.1) - Adhesive (FIPG)",
        "Exhaust Air or Gas cleaning residue (35.1) - DG chimney, Test bench chimney, Canteen chimney",
        "Spent resin (35.2) - Softener resin",
        "ETP wastes (35.3) - Chemical sludge",
        "Discarded containers (33.1) - Metal barrels, Plastic barrels, Metal buckets, Plastic buckets, Carbuoys, Paint containers, Spray containers"
    ]
    selected_category = tk.StringVar()
    selected_category.set(categories[0])  # Set default category

    selected_category_combo = ttk.Combobox(view_data_window, values=categories, textvariable=selected_category)
    selected_category_combo.pack(padx=10, pady=10)

    # Generate graphs for the selected category
    def generate_category_graph():
        category = selected_category.get()
        generate_graph_for_category(data, category)

    plotly_button = Button(view_data_window, text='Category Wise Analysis (Inflow)', command=generate_category_graph)
    plotly_button.pack(pady=10)

    logout_button = ttk.Button(view_data_window, text='Logout', command=window.destroy)
    logout_button.pack(pady=10)

def generate_graph_for_category(data, category):
    # Define category mappings and get fields for the selected category
    category_map = {
        'Used oil (5.1) - Used oil from shopfloor, Skimmed oil': {
            'fields': ['Used oil from shopfloor', 'Skimmed oil'],
            'kspcb_target': 12.05,
            'internal_target': 10.85,
        },
        'Wastes containing oil (5.2) - Used Gloves & Cloth, Grinding muck, Oil emulsion, Saw dust, Compressor filters, Fuel filters, DG filters, Residue with oil, Band/oiled filter paper, Lapping tape, Prowipe paper': {
            'fields': ['Used glove and cloth', 'Grinding Muck', 'Oil Emulsion', 'Saw Dust', 'Compressor filters', 'Fuel Filters', 'DG Filers', 'Residue with Oil', 'Band/oiled filter papers', 'Lapping Tape', 'Prowipe Paper'],
            'kspcb_target': 28.33,
            'internal_target': 25.50,
        },
        'Process waste (21.1) - Paint waste, Epoxy waste': {
            'fields': ['Paint waste', 'Epoxy Waste'],
            'kspcb_target': 0.33,
            'internal_target': 0.30,
        },
        'Wastes or residues (23.1) - Adhesive (FIPG)': {
            'fields': ['Adhesive (FIPG)'],
            'kspcb_target': 0.25,
            'internal_target': 0.23,
        },
        'Exhaust Air or Gas cleaning residue (35.1) - DG Chimney, Test Bench Chimney, Canteen Chimney': {
            'fields': ['DG chimney', 'Test Bench Chimney', 'Canteen Chimney'],
            'kspcb_target': 0.17,
            'internal_target': 0.15,
        },
        'Spent resin (35.2) - Softener resin': {
            'fields': ['Softener resin'],
            'kspcb_target': 0.38,
            'internal_target': 0.34,
        },
        'ETP wastes (35.3) - Chemical sludge': {
            'fields': ['Chemical sludge'],
            'kspcb_target': 125.0,
            'internal_target': 112.5,
        },
        'Discarded containers (33.1) - Metal barrels, Plastic barrels, Metal buckets, Plastic buckets, Carbuoys, Paint containers, Spray containers': {
            'fields': ['Metal barrels', 'Plastic barrels', 'Metal buckets', 'Plastic buckets', 'Carbuoys', 'Paint Containers', 'Spray Containers'],
            'kspcb_target': 3.0,
            'internal_target': 2.7,
        }
    }

    # Get category-specific details
    category_details = category_map[category]
    selected_fields = category_details['fields']
    kspcb_target = category_details['kspcb_target']
    internal_target = category_details['internal_target']

    # Filter data for the selected fields
    category_data = data[['Date'] + selected_fields].copy()  # Ensure to make a copy here

    # Convert 'Date' column to YearMonth format using .loc
    category_data.loc[:, 'YearMonth'] = pd.to_datetime(category_data['Date']).dt.to_period('M')

    # Combine data from all related sub-categories using .loc
    category_data.loc[:, 'Combined'] = category_data[selected_fields].sum(axis=1)

    # Group by 'YearMonth' and calculate the sum of combined data for each month
    monthly_aggregates = category_data.groupby('YearMonth')['Combined'].sum().reset_index()

    # Calculate cumulative values for each target based on category data
    kspcb_cumulative = [kspcb_target * (i + 1) for i in range(len(monthly_aggregates))]
    cumulative_internal = [internal_target * (i + 1) for i in range(len(monthly_aggregates))]

    # Plot bar chart
    fig = go.Figure()

    # Add current month's data as a bar graph
    fig.add_trace(go.Bar(x=monthly_aggregates['YearMonth'].astype(str), y=monthly_aggregates['Combined'],
                         name='Actual Data'))

    # Add cumulative sum as a second bar graph
    fig.add_trace(go.Bar(x=monthly_aggregates['YearMonth'].astype(str), y=monthly_aggregates['Combined'].cumsum(),
                         name='Cumulative Data'))

    # Add Cumulative KSPCB target line graph
    fig.add_trace(go.Scatter(x=monthly_aggregates['YearMonth'].astype(str), y=kspcb_cumulative,
                             mode='lines', name='Cumulative KSPCB target'))

    # Add Cumulative internal target line graph
    fig.add_trace(go.Scatter(x=monthly_aggregates['YearMonth'].astype(str), y=cumulative_internal,
                             mode='lines', name='Cumulative internal target'))

    # Set y-axis range dynamically based on data
    max_y = max(monthly_aggregates['Combined'].max(), max(kspcb_cumulative), max(cumulative_internal))
    fig.update_yaxes(range=[0, max_y + 5])  # Add some buffer to the max value for better visualization

    # Display month names on the x-axis
    month_names = [calendar.month_name[int(month.split('-')[1])] for month in monthly_aggregates['YearMonth'].astype(str)]
    fig.update_xaxes(tickvals=monthly_aggregates['YearMonth'].astype(str), ticktext=month_names)

    # Set graph title including the category
    fig.update_layout(
        title='Graph for {}'.format(category),
        xaxis_title='Month',
        yaxis_title='Data',
        barmode='group',  # Group bars together
        height=400  # Reduce the height of the graph
    )

    # Save Plotly graph as HTML file
    plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    with open('plotly_graph.html', 'w') as f:
        f.write(plotly_html)

    # Prepare the table data
    table_data = pd.DataFrame({
        'Month': monthly_aggregates['YearMonth'].dt.strftime('%B %Y'),
        'Monthly KSPCB Target (MT)': [kspcb_target] * len(monthly_aggregates),
        'Cumulative KSPCB Target (MT)': kspcb_cumulative,
        'Monthly Target (MT)': [internal_target] * len(monthly_aggregates),
        'Cumulative Target (MT)': cumulative_internal,
        'Monthly Actual (MT)': monthly_aggregates['Combined'],
        'Cumulative Actual (MT)': monthly_aggregates['Combined'].cumsum()
    })

    # Sort data by YearMonth in ascending order
    table_data['Month'] = pd.to_datetime(table_data['Month'], format='%B %Y')
    table_data = table_data.sort_values('Month')
    table_data['Month'] = table_data['Month'].dt.strftime('%B %Y')

    # Transpose the table
    table_data = table_data.set_index('Month').T
    # Round data to 2 decimal places
    table_data = table_data.round(2)

    # Prepare the table HTML
    table_html = table_data.to_html()

    # Save table as HTML file
    with open('table.html', 'w') as f:
        f.write(table_html)

    # Combine graph and table in a single HTML file
    combined_html = f"""<html>
    <head><title>Graph and Table</title></head>
    <body>
    <h1>Graph for {category}:</h1>
    {plotly_html}
    <h1>Table:</h1>
    {table_html}
    </body>
    </html>
    """
    with open('combined_graph_table.html', 'w') as f:
        f.write(combined_html)

    # Get the absolute path to the combined HTML file
    combined_html_path = os.path.abspath('combined_graph_table.html')

    # Open the combined HTML file in the default web browser using the file protocol
    webbrowser.open(f'file://{combined_html_path}')


if __name__ == '__main__':
    signup_button = ttk.Button(window, text='Signup', command=signup_page)
    signup_button.pack()

    login_button = ttk.Button(window, text='Login', command=login_page)
    login_button.pack()

    window.mainloop()
