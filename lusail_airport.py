import customtkinter as ctk
from tkinter import messagebox
import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FlightBookingSystem:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Flight Booking - Lusail International Airport")
        self.root.geometry("1200x750")
        
        # Flight data
        self.cities = ["Mattupolis", "Metropolis", "Aqualis", "Aureapolis"]
        self.airlines = ["Etihad", "Royal Jordanian", "United Airlines", "Air Finland", 
                        "Air South Korea", "Air Arabia", "Qatar Airways"]
        
        self.flights = self.generate_flights()
        self.filtered_flights = self.flights.copy()
        self.current_booking = None
        
        self.setup_ui()
        
    def generate_flights(self):
        """Generate flight schedules"""
        flights = []
        flight_id = 1000
        
        for city in self.cities:
            # Flights FROM Atlantes (Lusail) TO city
            for _ in range(3):  # 3 flights per route
                airline = random.choice(self.airlines)
                airline_code = self.get_airline_code(airline)
                flight_num = f"{airline_code}{random.randint(100, 999)}"
                
                dep_hour = random.randint(6, 22)
                dep_min = random.choice([0, 15, 30, 45])
                flight_duration = random.randint(2, 6)
                arr_hour = (dep_hour + flight_duration) % 24
                arr_min = dep_min
                
                flights.append({
                    'id': flight_id,
                    'flight_number': flight_num,
                    'airline': airline,
                    'origin': 'Atlantes (Lusail Intl)',
                    'destination': city,
                    'departure': f"{dep_hour:02d}:{dep_min:02d}",
                    'arrival': f"{arr_hour:02d}:{arr_min:02d}",
                    'duration': f"{flight_duration}h"
                })
                flight_id += 1
            
            # Flights FROM city TO Atlantes (Lusail)
            for _ in range(3):
                airline = random.choice(self.airlines)
                airline_code = self.get_airline_code(airline)
                flight_num = f"{airline_code}{random.randint(100, 999)}"
                
                dep_hour = random.randint(6, 22)
                dep_min = random.choice([0, 15, 30, 45])
                flight_duration = random.randint(2, 6)
                arr_hour = (dep_hour + flight_duration) % 24
                arr_min = dep_min
                
                flights.append({
                    'id': flight_id,
                    'flight_number': flight_num,
                    'airline': airline,
                    'origin': city,
                    'destination': 'Atlantes (Lusail Intl)',
                    'departure': f"{dep_hour:02d}:{dep_min:02d}",
                    'arrival': f"{arr_hour:02d}:{arr_min:02d}",
                    'duration': f"{flight_duration}h"
                })
                flight_id += 1
        
        return sorted(flights, key=lambda x: x['departure'])
    
    def get_airline_code(self, airline):
        """Get airline IATA-style codes"""
        codes = {
            "Etihad": "EY",
            "Royal Jordanian": "RJ",
            "United Airlines": "UA",
            "Air Finland": "AF",
            "Air South Korea": "KE",
            "Air Arabia": "G9",
            "Qatar Airways": "QR"
        }
        return codes.get(airline, "XX")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title = ctk.CTkLabel(self.root, text="✈️ Lusail International Airport", 
                            font=("Arial", 26, "bold"))
        title.pack(pady=10)
        
        subtitle = ctk.CTkLabel(self.root, text="Atlantes, Minecraft • Flight Booking System", 
                               font=("Arial", 14))
        subtitle.pack(pady=(0, 10))
        
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Left side - Filters
        filter_frame = ctk.CTkFrame(main_frame, width=230)
        filter_frame.pack(side="left", fill="y", padx=(8, 5), pady=8)
        filter_frame.pack_propagate(False)
        
        filter_title = ctk.CTkLabel(filter_frame, text="Filters", 
                                    font=("Arial", 18, "bold"))
        filter_title.pack(pady=10)
        
        # Origin filter
        ctk.CTkLabel(filter_frame, text="Origin:", font=("Arial", 12, "bold")).pack(pady=(8, 3))
        self.origin_var = ctk.StringVar(value="All")
        origin_options = ["All", "Atlantes (Lusail Intl)"] + self.cities
        self.origin_menu = ctk.CTkOptionMenu(filter_frame, variable=self.origin_var,
                                            values=origin_options, 
                                            command=self.apply_filters,
                                            width=210)
        self.origin_menu.pack(pady=3)
        
        # Destination filter
        ctk.CTkLabel(filter_frame, text="Destination:", font=("Arial", 12, "bold")).pack(pady=(12, 3))
        self.dest_var = ctk.StringVar(value="All")
        dest_options = ["All", "Atlantes (Lusail Intl)"] + self.cities
        self.dest_menu = ctk.CTkOptionMenu(filter_frame, variable=self.dest_var,
                                          values=dest_options,
                                          command=self.apply_filters,
                                          width=210)
        self.dest_menu.pack(pady=3)
        
        # Departure time filter
        ctk.CTkLabel(filter_frame, text="Departure Time:", font=("Arial", 12, "bold")).pack(pady=(12, 3))
        self.dep_time_var = ctk.StringVar(value="All")
        time_options = ["All", "Morning (06-12)", "Afternoon (12-18)", "Evening (18-24)"]
        self.dep_time_menu = ctk.CTkOptionMenu(filter_frame, variable=self.dep_time_var,
                                              values=time_options,
                                              command=self.apply_filters,
                                              width=210)
        self.dep_time_menu.pack(pady=3)
        
        # Reset filters button
        reset_btn = ctk.CTkButton(filter_frame, text="Reset Filters", 
                                 command=self.reset_filters,
                                 width=210,
                                 height=32,
                                 font=("Arial", 12))
        reset_btn.pack(pady=20)
        
        # Right side - Flight list and booking
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(5, 8), pady=8)
        
        # Flight list
        list_title = ctk.CTkLabel(right_frame, text="Available Flights", 
                                 font=("Arial", 18, "bold"))
        list_title.pack(pady=8)
        
        # Scrollable frame for flights
        self.flight_scroll = ctk.CTkScrollableFrame(right_frame, height=340)
        self.flight_scroll.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Booking section
        booking_frame = ctk.CTkFrame(right_frame)
        booking_frame.pack(fill="x", padx=8, pady=8)
        
        booking_title = ctk.CTkLabel(booking_frame, text="Book Your Flight", 
                                     font=("Arial", 16, "bold"))
        booking_title.pack(pady=8)
        
        # Input fields
        input_frame = ctk.CTkFrame(booking_frame)
        input_frame.pack(pady=5)
        
        ctk.CTkLabel(input_frame, text="Minecraft Username:", font=("Arial", 12)).grid(row=0, column=0, padx=8, pady=5, sticky="e")
        self.username_entry = ctk.CTkEntry(input_frame, width=220, height=32, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, padx=8, pady=5)
        
        ctk.CTkLabel(input_frame, text="Email Address:", font=("Arial", 12)).grid(row=1, column=0, padx=8, pady=5, sticky="e")
        self.email_entry = ctk.CTkEntry(input_frame, width=220, height=32, font=("Arial", 12))
        self.email_entry.grid(row=1, column=1, padx=8, pady=5)
        
        ctk.CTkLabel(input_frame, text="Selected Flight:", font=("Arial", 12)).grid(row=2, column=0, padx=8, pady=5, sticky="e")
        self.selected_flight_label = ctk.CTkLabel(input_frame, text="None", 
                                                 font=("Arial", 12, "bold"),
                                                 text_color="#3b8ed0")
        self.selected_flight_label.grid(row=2, column=1, padx=8, pady=5, sticky="w")
        
        # Buttons frame
        button_frame = ctk.CTkFrame(booking_frame)
        button_frame.pack(pady=8)
        
        # Book button
        self.book_btn = ctk.CTkButton(button_frame, text="✈️ Confirm Booking", 
                                     command=self.book_flight,
                                     font=("Arial", 13, "bold"),
                                     height=38,
                                     width=180)
        self.book_btn.grid(row=0, column=0, padx=8, pady=5)
        
        # Send Email button
        self.email_btn = ctk.CTkButton(button_frame, text="📧 Send Email Confirmation", 
                                      command=self.send_email_confirmation,
                                      font=("Arial", 13, "bold"),
                                      height=38,
                                      width=180,
                                      state="disabled",
                                      fg_color="gray")
        self.email_btn.grid(row=0, column=1, padx=8, pady=5)
        
        self.selected_flight = None
        self.display_flights()
    
    def display_flights(self):
        """Display flights in the scrollable frame"""
        # Clear existing widgets
        for widget in self.flight_scroll.winfo_children():
            widget.destroy()
        
        if not self.filtered_flights:
            no_flights = ctk.CTkLabel(self.flight_scroll, 
                                     text="No flights match your filters",
                                     font=("Arial", 15))
            no_flights.pack(pady=20)
            return
        
        for flight in self.filtered_flights:
            flight_frame = ctk.CTkFrame(self.flight_scroll)
            flight_frame.pack(fill="x", pady=5, padx=5)
            
            # Flight info
            info_text = f"{flight['flight_number']} | {flight['airline']}\n"
            info_text += f"{flight['origin']} → {flight['destination']}\n"
            info_text += f"Departure: {flight['departure']} | Arrival: {flight['arrival']} | Duration: {flight['duration']}"
            
            info_label = ctk.CTkLabel(flight_frame, text=info_text, 
                                     font=("Arial", 12), justify="left")
            info_label.pack(side="left", padx=12, pady=10)
            
            select_btn = ctk.CTkButton(flight_frame, text="Select", 
                                      command=lambda f=flight: self.select_flight(f),
                                      width=90,
                                      height=32,
                                      font=("Arial", 12))
            select_btn.pack(side="right", padx=12, pady=8)
    
    def select_flight(self, flight):
        """Select a flight for booking"""
        self.selected_flight = flight
        flight_text = f"{flight['flight_number']} - {flight['origin']} to {flight['destination']}"
        self.selected_flight_label.configure(text=flight_text)
    
    def apply_filters(self, *args):
        """Apply filters to flight list"""
        self.filtered_flights = self.flights.copy()
        
        # Origin filter
        if self.origin_var.get() != "All":
            self.filtered_flights = [f for f in self.filtered_flights 
                                    if f['origin'] == self.origin_var.get()]
        
        # Destination filter
        if self.dest_var.get() != "All":
            self.filtered_flights = [f for f in self.filtered_flights 
                                    if f['destination'] == self.dest_var.get()]
        
        # Departure time filter
        dep_time = self.dep_time_var.get()
        if dep_time != "All":
            if "Morning" in dep_time:
                self.filtered_flights = [f for f in self.filtered_flights 
                                        if 6 <= int(f['departure'].split(':')[0]) < 12]
            elif "Afternoon" in dep_time:
                self.filtered_flights = [f for f in self.filtered_flights 
                                        if 12 <= int(f['departure'].split(':')[0]) < 18]
            elif "Evening" in dep_time:
                self.filtered_flights = [f for f in self.filtered_flights 
                                        if 18 <= int(f['departure'].split(':')[0]) < 24]
        
        self.display_flights()
    
    def reset_filters(self):
        """Reset all filters"""
        self.origin_var.set("All")
        self.dest_var.set("All")
        self.dep_time_var.set("All")
        self.filtered_flights = self.flights.copy()
        self.display_flights()
    
    def book_flight(self):
        """Book the selected flight"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter your Minecraft username!")
            return
        
        if not email or "@" not in email:
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        
        if not self.selected_flight:
            messagebox.showerror("Error", "Please select a flight!")
            return
        
        # Generate booking confirmation
        booking_ref = f"LUS{random.randint(100000, 999999)}"
        
        # Store current booking
        self.current_booking = {
            'reference': booking_ref,
            'username': username,
            'email': email,
            'flight': self.selected_flight
        }
        
        # Create confirmation message
        confirmation = f"""
✈️ FLIGHT BOOKING CONFIRMED ✈️

Booking Reference: {booking_ref}
Passenger: {username}

Flight Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flight Number: {self.selected_flight['flight_number']}
Airline: {self.selected_flight['airline']}
Route: {self.selected_flight['origin']} → {self.selected_flight['destination']}
Departure: {self.selected_flight['departure']}
Arrival: {self.selected_flight['arrival']}
Duration: {self.selected_flight['duration']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing Lusail International Airport!
Safe travels! 🌍
"""
        
        messagebox.showinfo("Booking Confirmed!", confirmation)
        
        # Enable email button
        self.email_btn.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])
    
    def send_email_confirmation(self):
        """Send confirmation email for current booking"""
        if not self.current_booking:
            messagebox.showerror("Error", "No booking to send! Please book a flight first.")
            return
        
        booking = self.current_booking
        
        confirmation_text = f"""
✈️ FLIGHT BOOKING CONFIRMATION ✈️

Booking Reference: {booking['reference']}
Passenger: {booking['username']}

Flight Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flight Number: {booking['flight']['flight_number']}
Airline: {booking['flight']['airline']}
Route: {booking['flight']['origin']} → {booking['flight']['destination']}
Departure: {booking['flight']['departure']}
Arrival: {booking['flight']['arrival']}
Duration: {booking['flight']['duration']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing Lusail International Airport!
Safe travels! 🌍

---
This is an automated confirmation from Lusail International Airport
Atlantes, Minecraft Server
"""
        
        # Try to send email
        email_sent = self.send_email(booking['email'], booking['username'], confirmation_text, booking['reference'])
        
        if email_sent:
            messagebox.showinfo("Email Sent!", 
                              f"Confirmation email has been sent to:\n{booking['email']}")
            # Clear current booking
            self.current_booking = None
            self.email_btn.configure(state="disabled", fg_color="gray")
            # Clear fields
            self.username_entry.delete(0, 'end')
            self.email_entry.delete(0, 'end')
            self.selected_flight = None
            self.selected_flight_label.configure(text="None")
        else:
            messagebox.showerror("Email Failed", 
                              "Could not send email. Please check your SMTP settings in the code.\n\n"
                              "Make sure you've updated:\n"
                              "- sender_email\n"
                              "- sender_password (Gmail App Password)")
    
    def send_email(self, to_email, username, confirmation, booking_ref):
        """Send confirmation email (requires SMTP configuration)"""
        try:
            # SMTP Configuration - UPDATE THESE VALUES
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "mqasem784@gmail.com"  # ← CHANGE THIS
            sender_password = "rdpoabfzdvbfanhh"  # ← CHANGE THIS (16-char app password)
            
            msg = MIMEMultipart()
            msg['From'] = f"Lusail Airport <{sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = f"Flight Booking Confirmation - {booking_ref}"
            
            msg.attach(MIMEText(confirmation, 'plain'))
            
            print(f"Connecting to {smtp_server}...")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            print("Logging in...")
            server.login(sender_email, sender_password)
            print("Sending email...")
            server.send_message(msg)
            server.quit()
            print("Email sent successfully!")
            
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = FlightBookingSystem()
    app.run()