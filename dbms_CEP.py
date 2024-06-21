import tkinter as tk
from tkinter import messagebox, Toplevel
from tkcalendar import Calendar
import cx_Oracle
from datetime import datetime
from PIL import Image, ImageTk

# Function to handle booking
def book_slot():
    name = entry_name.get()
    phone = entry_phone.get()
    
    # Get date from entry
    date_str = entry_date.get()

    try:
        # Convert to datetime object
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        # Format date to 'DD-MM-YYYY'
        formatted_date = date_obj.strftime('%d-%m-%Y')
        
        # Convert current date to datetime object
        current_datetime = datetime.now()
        current_date = current_datetime.date()

        # Check if the selected date is in the past
        if date_obj.date() < current_date:
            messagebox.showerror("Error", "Cannot book a slot for a past date. Please select a future date.")
            return
        
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid date format: {e}")
        return

    start_time = entry_start_time.get() + " " + start_time_period.get()
    end_time = entry_end_time.get() + " " + end_time_period.get()

    # Ensure end time is after start time
    start_datetime = datetime.strptime(f"{date_str} {start_time}", '%d-%m-%Y %I:%M %p')
    end_datetime = datetime.strptime(f"{date_str} {end_time}", '%d-%m-%Y %I:%M %p')

    if end_datetime <= start_datetime:
        messagebox.showerror("Error", "End time must be after start time.")
        return

    if name and phone and formatted_date and start_time and end_time:
        try:
            # Update connection string with your actual database connection details
            con = cx_Oracle.connect('system/krish@localhost:1521/xe')
            cur = con.cursor()

            # Insert user information if not exists
            cur.execute("SELECT user_id FROM users WHERE phone = :1", (phone,))
            user_id = cur.fetchone()
            if user_id is None:
                cur.execute("INSERT INTO users (user_id, name, phone) VALUES (users_seq.NEXTVAL, :1, :2)", (name, phone))
                con.commit()
                cur.execute("SELECT user_id FROM users WHERE phone = :1", (phone,))
                user_id = cur.fetchone()[0]
            else:
                user_id = user_id[0]

            # Insert time slot information
            cur.execute("""
                INSERT INTO time_slots (slot_id, start_time, end_time) 
                VALUES (time_slots_seq.NEXTVAL, TO_TIMESTAMP(:1, 'DD-MM-YYYY HH:MI AM'), TO_TIMESTAMP(:2, 'DD-MM-YYYY HH:MI AM'))
            """, (f"{formatted_date} {start_time}", f"{formatted_date} {end_time}"))
            con.commit()

            cur.execute("SELECT slot_id FROM time_slots WHERE start_time = TO_TIMESTAMP(:1, 'DD-MM-YYYY HH:MI AM')", (f"{formatted_date} {start_time}",))
            slot_id = cur.fetchone()[0]

            # Insert booking information
            query = """
            INSERT INTO bookings (booking_id, user_id, booking_date, slot_id) 
            VALUES (bookings_seq.NEXTVAL, :1, TO_DATE(:2, 'DD-MM-YYYY'), :3)
            """
            values = (user_id, formatted_date, slot_id)
            cur.execute(query, values)
            con.commit()

            # Close the connection
            cur.close()
            con.close()

            messagebox.showinfo("Booking Confirmed", f"Booking confirmed for {name} on {formatted_date} from {start_time} to {end_time}.")
        except cx_Oracle.DatabaseError as err:
            error, = err.args
            if error.code == 20001:
                messagebox.showerror("Error", "Time slot overlaps with an existing booking. Please choose a different time slot.")
            else:
                messagebox.showerror("Error", f"Database error: {err}")
            if cur:
                cur.close()
            if con:
                con.close()
    else:
        messagebox.showerror("Error", "Please fill in all fields.")

# Function to open a calendar window and select a date
def select_date():
    def on_date_select():
        date_str = cal.get_date()
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        formatted_date = date_obj.strftime('%d-%m-%Y')
        entry_date.delete(0, tk.END)
        entry_date.insert(0, formatted_date)
        top.destroy()

    top = Toplevel(root)
    top.title("Select Date")
    cal = Calendar(top, selectmode='day', year=2024, month=6, day=3)
    cal.pack(padx=10, pady=10)
    btn_select = tk.Button(top, text="Select", command=on_date_select)
    btn_select.pack(pady=10)

# Create main window
root = tk.Tk()
root.title("Box Cricket Booking System")

# Load background image using Pillow
image_path = r"C:\Users\admin\Downloads\cric(bg).jpg"
image = Image.open(image_path)
bg_image = ImageTk.PhotoImage(image)

# Create a label to display the background image
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)

# Create a frame to hold the widgets
frame = tk.Frame(root, bg='black', bd=5)
frame.place(relx=0.5, rely=0.5, anchor='center')

# Create and place widgets in the frame
tk.Label(frame, text="Name:", fg="blue").grid(row=0, column=0, padx=10, pady=10)
entry_name = tk.Entry(frame, fg="blue", bg='white')
entry_name.grid(row=0, column=1, padx=10, pady=10)

tk.Label(frame, text="Phone:", fg="blue").grid(row=1, column=0, padx=10, pady=10)
entry_phone = tk.Entry(frame, fg="blue", bg='white')
entry_phone.grid(row=1, column=1, padx=10, pady=10)

tk.Label(frame, text="Date:", fg="blue").grid(row=2, column=0, padx=10, pady=10)
entry_date = tk.Entry(frame, fg="blue", bg='white')
entry_date.grid(row=2, column=1, padx=10, pady=10)
btn_select_date = tk.Button(frame, text="Select Date", command=select_date)
btn_select_date.grid(row=2, column=2, padx=10, pady=10)

tk.Label(frame, text="Start Time:", fg="blue").grid(row=3, column=0, padx=10, pady=10)
entry_start_time = tk.Entry(frame, fg="blue", bg='white')
entry_start_time.grid(row=3, column=1, padx=10, pady=10)

start_time_period = tk.StringVar(value="AM")
start_time_options = ["AM", "PM"]
start_option_menu = tk.OptionMenu(frame, start_time_period, *start_time_options)
start_option_menu.grid(row=3, column=2, padx=10, pady=10)

tk.Label(frame, text="End Time:", fg="blue").grid(row=4, column=0, padx=10, pady=10)
entry_end_time = tk.Entry(frame, fg="blue", bg='white')
entry_end_time.grid(row=4, column=1, padx=10, pady=10)

end_time_period = tk.StringVar(value="AM")
end_time_options = ["AM", "PM"]
end_option_menu = tk.OptionMenu(frame, end_time_period, *end_time_options)
end_option_menu.grid(row=4, column=2, padx=10, pady=10)

btn_book = tk.Button(frame, text="Book Slot", command=book_slot)
btn_book.grid(row=5, columnspan=3, pady=20)

# Run the application
root.mainloop()
