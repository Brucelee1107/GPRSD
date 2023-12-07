import tkinter as tk
import subprocess
import os
import time
import psutil

update_enabled = False  # Enable/disable state
enable_button_clicked = False  # Track if the Enable button has been clicked


# Function to execute the command and update values
def execute_and_update():
    global update_enabled
    if update_enabled:
        execute_command()
        display_values_in_text_boxes()


# Command execution function
def execute_command():
    # Check if daemon is already running
    for process in psutil.process_iter(['pid', 'name']):
        if 'gprsd' in process.info['name']:
            print("Already Running")
            return

    # If not running , start gprsd
    try:
        command = "/usr/sbin/gprsd"
        output = subprocess.check_output(command, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print("gprsd not enabled")


# Function to display the values in the text boxes
def display_values_in_text_boxes():
    tower_value = get_tower_value()
    sim_operator = get_sim_operator()
    imei_number = get_imei_number()
    sim_serial = get_sim_serial()

    # Display values in text boxes
    text_boxes[1].config(state=tk.NORMAL)
    text_boxes[1].delete(0, tk.END)
    text_boxes[1].insert(0, tower_value)

    text_boxes[2].config(state=tk.NORMAL)
    text_boxes[2].delete(0, tk.END)
    text_boxes[2].insert(0, sim_operator)

    text_boxes[3].config(state=tk.NORMAL)
    text_boxes[3].delete(0, tk.END)
    text_boxes[3].insert(0, imei_number)

    text_boxes[4].config(state=tk.NORMAL)
    text_boxes[4].delete(0, tk.END)
    text_boxes[4].insert(0, sim_serial)

    # Update the canvas with connectivity status
    update_connectivity_canvas()


# Function to get the tower value from the given path
def get_tower_value():
    try:
        with open("/usr/share/status/gprs/csq_value", "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""


# Function to get the sim operator from the given path
def get_sim_operator():
    try:
        with open("/usr/share/status/gprs/sim_operator", "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""


# Function to get the IMEI number from the given path
def get_imei_number():
    try:
        with open("/usr/share/status/gprs/sim_imei", "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""


# Function to get the Sim Serial number from the given path
def get_sim_serial():
    try:
        with open("/usr/share/status/gprs/sim_serial", "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""


# Function to save APN name
def save_apn():
    apn_name = text_boxes[0].get()
    if apn_name:
        file_path = "/usr/share/status/gprs/apn"
        with open(file_path, "w") as file:
            file.write(apn_name)
        print("APN name saved")
        disable_updates()
        time.sleep(1)
        enable_updates()
    else:
        print("APN name not saved")


# Function to execute the function after clicking the enable button
def enable_updates():
    global update_enabled, enable_button_clicked
    if not enable_button_clicked:
        enable_button_clicked = True
        update_enabled = True
        execute_and_update()  # Execute the command and update values periodically
        display_values_in_text_boxes()


# Function to execute the function after clicking the disable button
def disable_updates():
    global update_enabled, enable_button_clicked
    update_enabled = False
    enable_button_clicked = False
    os.system("killall gprsd")
    reset_values()


# Function to reset values to the initial state and disable text boxes
def reset_values():
    text_boxes[1].config(state=tk.NORMAL)
    text_boxes[1].delete(0, tk.END)
    text_boxes[1].insert(0, "")
    text_boxes[1].config(state=tk.DISABLED)

    text_boxes[2].config(state=tk.NORMAL)
    text_boxes[2].delete(0, tk.END)
    text_boxes[2].insert(0, "")
    text_boxes[2].config(state=tk.DISABLED)

    text_boxes[3].config(state=tk.NORMAL)
    text_boxes[3].delete(0, tk.END)
    text_boxes[3].insert(0, "")
    text_boxes[3].config(state=tk.DISABLED)

    text_boxes[4].config(state=tk.NORMAL)
    text_boxes[4].delete(0, tk.END)
    text_boxes[4].insert(0, "")
    text_boxes[4].config(state=tk.DISABLED)

    # Reset canvas
    canvas.delete("all")


# Function to handle file system events
class FileChangeHandler():
    def on_modified(self, event):
        display_values_in_text_boxes()


# Function to check for file changes and update the GUI
def check_file_changes():
    if update_enabled:
        display_values_in_text_boxes()
    app.after(1000, check_file_changes)  # Check for updates every (1 second)


# Function to update the connectivity canvas
def update_connectivity_canvas():
    try:
        with open("/usr/share/status/gprs/nw_status", "r") as file:
            status = int(file.read().strip())
            canvas.delete("all")
            if status == 1:
                canvas.create_rectangle(0,0,10,10, fill="green")
            else:
                canvas.create_rectangle(0,0,10,10, fill="red")
    except FileNotFoundError:
        # Handle file not found error
        canvas.delete("all")
        canvas.create_rectangle(0,0,30, 30, fill="gray")

# Start the GUI
app = tk.Tk()
app.title("GPRS Settings")
app.config(bg="#ddd")
app.geometry("600x300")

# Enable/Disable buttons
enable_button = tk.Button(app, text="Enable", command=enable_updates)
enable_button.grid(row=0, column=0, padx=5, pady=5)

disable_button = tk.Button(app, text="Disable", command=disable_updates)
disable_button.grid(row=0, column=1, padx=5, pady=5)

# Labels and text boxes
labels = ["APN name", "Tower value", "Sim Operator", "IMEI No", "Sim Serial No"]
text_boxes = [tk.Entry(app, width=40) if i == 0 else tk.Entry(app, width=40, state=tk.DISABLED) for i in range(6)]

for i, label_text in enumerate(labels):
    label = tk.Label(app, text="{} :".format(label_text), anchor="center")
    label.grid(row=i + 1, column=0, padx=5, pady=5)
    text_box = text_boxes[i]
    text_box.grid(row=i + 1, column=1, padx=5, pady=5)

label = tk.Label(app, text="Connectivity :")
label.grid(row=7, column=0, padx=5, pady=5)

# Canvas for connectivity status
canvas = tk.Canvas(app,width=15,height=15, bg="white")
canvas.grid(row=7, column=1, padx=5, pady=5, sticky="w")

# Save button for APN name
save_button = tk.Button(app, text="Save APN", command=save_apn)
save_button.grid(row=1, column=2, padx=5, pady=5)

# Run the function to check for file changes periodically
app.after(1000, check_file_changes)

# Run the app main loop
app.mainloop()

