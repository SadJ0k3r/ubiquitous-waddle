import requests
from datetime import datetime
import smtplib
from tkinter import *
 
MY_LAT =  # Put your latitude here
MY_LONG =  # Put your longitude here
LOCAL_UTC_OFFSET = # Put your UTC offset here
EMAIL = "your.email@gmail.com"  # Don't forget to change the SMTP if not Gmail
PASSWORD = "yourpassword"
FONT = ("Open Sans", 16)
tracker = ""
 
 
def is_iss_overhead():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
 
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    if abs(iss_latitude - MY_LAT) <= 5 and abs(iss_longitude - MY_LONG) <= 5:
        return True
    else:
        return False
 
 
def utc_to_local(utc_hour):
    utc_hour += LOCAL_UTC_OFFSET
    if LOCAL_UTC_OFFSET > 0:
        if utc_hour > 23:
            utc_hour -= 24
    elif LOCAL_UTC_OFFSET < 0:
        if utc_hour < 0:
            utc_hour += 24
    return utc_hour
 
 
def is_dark():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }
 
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    utc_sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    utc_sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])
    local_sunrise = utc_to_local(utc_sunrise)
    local_sunset = utc_to_local(utc_sunset)
    time_now = datetime.now()
    if local_sunset <= time_now.hour or time_now.hour <= local_sunrise:
        return True
    else:
        return False
 
 
def check_on_iss():
    if is_iss_overhead() and is_dark():
        window.bell()
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=EMAIL, password=PASSWORD)
            connection.sendmail(
                from_addr=EMAIL,
                to_addrs=EMAIL,
                msg="Subject: Look up!\n\nThe ISS should be visible above you right now."
            )
 
 
def start_tracking():
    global tracker
    track_button.config(state="disabled")
    stop_button.config(state="normal")
    hour = datetime.now().hour
    if hour < 10:
        hour = f"0{hour}"
    minute = datetime.now().minute
    if minute < 10:
        minute = f"0{minute}"
    tracking_text.config(text=f"Last check: {hour}:{minute}")
    check_on_iss()
    tracker = window.after(60000, start_tracking)
 
 
def stop_tracking():
    global tracker
    track_button.config(state="normal")
    stop_button.config(state="disabled")
    tracking_text.config(text="Press 'Start Tracking' to check if the ISS is visible.")
    window.after_cancel(tracker)
 
 
window = Tk()
window.title("ISS Tracker")
window.config(width=250, height=100, padx=50, pady=50)
 
track_button = Button(text="Start Tracking", bg="#3399ff", fg="white", font=FONT, command=start_tracking)
track_button.grid(column=0, row=0)
 
stop_button = Button(text="Stop Tracking", bg="#800000", fg="white", font=FONT, command=stop_tracking)
stop_button.config(state="disabled")
stop_button.grid(column=1, row=0)
 
tracking_text = Label(text="Press 'Start Tracking' to check if the ISS is visible.", font=("Open Sans", 10), pady=25)
tracking_text.grid(column=0, row=1, columnspan=2)
 
window.mainloop()