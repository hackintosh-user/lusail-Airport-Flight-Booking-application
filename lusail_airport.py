
import customtkinter as ctk
from tkinter import messagebox
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import json
import os
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CURRENT_VERSION = "3.0.0"
GITHUB_RELEASES_URL = "https://api.github.com/repos/hackintosh-user/lusail-Airport-Flight-Booking-application/releases/latest"

LUGGAGE_PRICES = {
    "No Luggage": 0,
    "1 Checked Bag (23kg)": 25,
    "2 Checked Bags (23kg each)": 45,
    "1 Checked Bag + Carry-on": 30,
    "2 Checked Bags + Carry-on": 50
}

class FlightBookingSystem:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"Flight Booking v{CURRENT_VERSION}")
        self.root.geometry("1100x700")
        self.check_for_updates()
        
        self.cities = ["Mattupolis", "Metropolis", "Aqualis", "Aureapolis"]
        self.airline_aircraft = {
            "Ryanair": "Boeing 737-300", "Southwest": "Boeing 737-300",
            "Delta Airways": "Boeing 737-300", "British Airways": "Boeing 737-300",
            "United Airways": "Boeing 737-300", "Etihad": "Airbus A320-200",
            "Wizz Air": "Airbus A320-200", "Qatar Airways": "Airbus A320-200",
            "Royal Jordanian": "Airbus A320-200", "Swiss": "Airbus A220-300",
            "Air Canada": "Airbus A220-300", "Air France": "Airbus A220-300",
            "Breeze": "Airbus A220-300", "JetBlue A320": "Airbus A320-200",
            "JetBlue A220": "Airbus A220-300"
        }
        self.budget_airlines = ["Ryanair", "Southwest", "Breeze", "Wizz Air", "JetBlue A320", "JetBlue A220"]
        self.premium_airlines = ["Etihad", "Delta Airways", "British Airways", "United Airways", 
                                "Qatar Airways", "Royal Jordanian", "Swiss", "Air Canada", "Air France"]
        self.aircraft_types = {
            "Airbus A320-200": {"rows": 18, "config": ["A", "B", "D", "E"], "total": 72, "base_price": 150},
            "Boeing 737-300": {"rows": 18, "config": ["A", "B", "D", "E"], "total": 72, "base_price": 140},
            "Airbus A220-300": {"rows": 19, "config_left": ["A", "B"], "config_right": ["D"], "total": 57, "base_price": 180}
        }
        self.flights = self.generate_flights()
        self.filtered_flights = self.flights.copy()
        self.current_booking = None
        self.passengers = []
        self.selected_flight = None
        self.current_mode = "dark"
        self.setup_ui()
        
    def generate_flights(self):
        random.seed(12345)
        flights = []
        flight_id = 1000
        airlines = list(self.airline_aircraft.keys())
        for city in self.cities:
            for _ in range(3):
                airline = random.choice(airlines)
                airline_code = self.get_airline_code(airline)
                flight_num = f"{airline_code}{random.randint(100, 999)}"
                aircraft = self.airline_aircraft[airline]
                base_price = self.aircraft_types[aircraft]["base_price"]
                if airline in self.budget_airlines:
                    price = int(base_price * 0.7)
                elif airline in self.premium_airlines:
                    price = int(base_price * 1.3)
                else:
                    price = base_price
                dep_hour = random.randint(6, 22)
                dep_min = random.choice([0, 15, 30, 45])
                flight_duration = random.randint(2, 6)
                arr_hour = (dep_hour + flight_duration) % 24
                arr_min = dep_min
                flights.append({
                    'id': flight_id, 'flight_number': flight_num, 'airline': airline,
                    'origin': 'Atlantes (Lusail Intl)', 'destination': city,
                    'departure': f"{dep_hour:02d}:{dep_min:02d}",
                    'arrival': f"{arr_hour:02d}:{arr_min:02d}",
                    'duration': f"{flight_duration}h", 'aircraft': aircraft,
                    'price': price, 'booked_seats': [], 'gate': random.choice([1, 2, 3])
                })
                flight_id += 1
            for _ in range(3):
                airline = random.choice(airlines)
                airline_code = self.get_airline_code(airline)
                flight_num = f"{airline_code}{random.randint(100, 999)}"
                aircraft = self.airline_aircraft[airline]
                base_price = self.aircraft_types[aircraft]["base_price"]
                if airline in self.budget_airlines:
                    price = int(base_price * 0.7)
                elif airline in self.premium_airlines:
                    price = int(base_price * 1.3)
                else:
                    price = base_price
                dep_hour = random.randint(6, 22)
                dep_min = random.choice([0, 15, 30, 45])
                flight_duration = random.randint(2, 6)
                arr_hour = (dep_hour + flight_duration) % 24
                arr_min = dep_min
                flights.append({
                    'id': flight_id, 'flight_number': flight_num, 'airline': airline,
                    'origin': city, 'destination': 'Atlantes (Lusail Intl)',
                    'departure': f"{dep_hour:02d}:{dep_min:02d}",
                    'arrival': f"{arr_hour:02d}:{arr_min:02d}",
                    'duration': f"{flight_duration}h", 'aircraft': aircraft,
                    'price': price, 'booked_seats': [], 'gate': random.choice([1, 2, 3])
                })
                flight_id += 1
        random.seed()
        return sorted(flights, key=lambda x: x['departure'])
    
    def get_airline_code(self, airline):
        codes = {"Ryanair": "FR", "Southwest": "WN", "Delta Airways": "DL", "British Airways": "BA",
                "United Airways": "UA", "Etihad": "EY", "JetBlue A320": "B6", "JetBlue A220": "B6",
                "Wizz Air": "W6", "Qatar Airways": "QR", "Royal Jordanian": "RJ", "Swiss": "LX",
                "Air Canada": "AC", "Air France": "AF", "Breeze": "MX"}
        return codes.get(airline, "XX")
    
    def setup_ui(self):
        top_bar = ctk.CTkFrame(self.root, height=45, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=(8, 0))
        map_btn = ctk.CTkButton(top_bar, text="🗺️ View Airport Map", command=self.show_airport_map,
                               width=140, height=32, font=("Arial", 11))
        map_btn.pack(side="right", padx=5, pady=5)
        theme_btn = ctk.CTkButton(top_bar, text="🌙 Dark Mode", command=self.toggle_theme,
                                 width=110, height=32, font=("Arial", 11))
        theme_btn.pack(side="right", padx=5, pady=5)
        self.theme_btn = theme_btn
        
        title = ctk.CTkLabel(self.root, text="✈️ Lusail International Airport", font=("Arial", 24, "bold"))
        title.pack(pady=8)
        subtitle = ctk.CTkLabel(self.root, text="Atlantes, Minecraft • Flight Booking System", font=("Arial", 13))
        subtitle.pack(pady=(0, 8))
        
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        
        filter_frame = ctk.CTkFrame(main_frame, width=210)
        filter_frame.pack(side="left", fill="y", padx=(6, 4), pady=6)
        filter_frame.pack_propagate(False)
        filter_title = ctk.CTkLabel(filter_frame, text="Filters", font=("Arial", 16, "bold"))
        filter_title.pack(pady=8)
        
        ctk.CTkLabel(filter_frame, text="Origin:", font=("Arial", 11, "bold")).pack(pady=(6, 2))
        self.origin_var = ctk.StringVar(value="All")
        self.origin_menu = ctk.CTkOptionMenu(filter_frame, variable=self.origin_var,
                                            values=["All", "Atlantes (Lusail Intl)"] + self.cities,
                                            command=self.apply_filters, width=190)
        self.origin_menu.pack(pady=2)
        
        ctk.CTkLabel(filter_frame, text="Destination:", font=("Arial", 11, "bold")).pack(pady=(10, 2))
        self.dest_var = ctk.StringVar(value="All")
        self.dest_menu = ctk.CTkOptionMenu(filter_frame, variable=self.dest_var,
                                          values=["All", "Atlantes (Lusail Intl)"] + self.cities,
                                          command=self.apply_filters, width=190)
        self.dest_menu.pack(pady=2)
        
        ctk.CTkLabel(filter_frame, text="Departure Time:", font=("Arial", 11, "bold")).pack(pady=(10, 2))
        self.dep_time_var = ctk.StringVar(value="All")
        self.dep_time_menu = ctk.CTkOptionMenu(filter_frame, variable=self.dep_time_var,
                                              values=["All", "Morning (06-12)", "Afternoon (12-18)", "Evening (18-24)"],
                                              command=self.apply_filters, width=190)
        self.dep_time_menu.pack(pady=2)
        
        reset_btn = ctk.CTkButton(filter_frame, text="Reset Filters", command=self.reset_filters,
                                 width=190, height=30, font=("Arial", 11))
        reset_btn.pack(pady=15)
        
        ctk.CTkLabel(filter_frame, text="Search:", font=("Arial", 11, "bold")).pack(pady=(4, 2))
        self.search_entry = ctk.CTkEntry(filter_frame, width=190, height=30, placeholder_text="Flight # or Airline")
        self.search_entry.pack(pady=2)
        self.search_entry.bind("<KeyRelease>", self.search_flights)
        search_btn = ctk.CTkButton(filter_frame, text="🔍 Search", command=self.search_flights,
                                  width=190, height=30, font=("Arial", 11))
        search_btn.pack(pady=4)
        
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(4, 6), pady=6)
        list_title = ctk.CTkLabel(right_frame, text="Available Flights", font=("Arial", 16, "bold"))
        list_title.pack(pady=6)
        self.flight_scroll = ctk.CTkScrollableFrame(right_frame, height=240)
        self.flight_scroll.pack(fill="both", expand=True, padx=6, pady=6)
        
        booking_frame = ctk.CTkFrame(right_frame)
        booking_frame.pack(fill="x", padx=6, pady=6)
        booking_title = ctk.CTkLabel(booking_frame, text="Book Your Flight", font=("Arial", 14, "bold"))
        booking_title.pack(pady=6)
        
        passenger_frame = ctk.CTkFrame(booking_frame)
        passenger_frame.pack(pady=4, fill="x", padx=10)
        self.passenger_list_label = ctk.CTkLabel(passenger_frame, text="Passengers: None", font=("Arial", 11))
        self.passenger_list_label.pack(side="left", padx=8)
        add_passenger_btn = ctk.CTkButton(passenger_frame, text="➕ Add Passenger", 
                                         command=self.add_passenger_dialog, width=130, height=30, font=("Arial", 11))
        add_passenger_btn.pack(side="left", padx=4)
        clear_passengers_btn = ctk.CTkButton(passenger_frame, text="🗑️ Clear All", 
                                            command=self.clear_passengers, width=90, height=30, font=("Arial", 11))
        clear_passengers_btn.pack(side="left", padx=4)
        
        info_frame = ctk.CTkFrame(booking_frame)
        info_frame.pack(pady=4)
        
        ctk.CTkLabel(info_frame, text="Selected Flight:", font=("Arial", 11)).grid(row=0, column=0, padx=6, pady=4, sticky="e")
        self.selected_flight_label = ctk.CTkLabel(info_frame, text="None", font=("Arial", 11, "bold"), text_color="#3b8ed0")
        self.selected_flight_label.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        
        ctk.CTkLabel(info_frame, text="Total Price:", font=("Arial", 11)).grid(row=1, column=0, padx=6, pady=4, sticky="e")
        self.total_price_label = ctk.CTkLabel(info_frame, text="$0", font=("Arial", 11, "bold"), text_color="#4CAF50")
        self.total_price_label.grid(row=1, column=1, padx=6, pady=4, sticky="w")
        
        ctk.CTkLabel(info_frame, text="Payment:", font=("Arial", 11)).grid(row=0, column=2, padx=6, pady=4, sticky="e")
        self.payment_var = ctk.StringVar(value="Pay at LIA")
        payment_menu = ctk.CTkOptionMenu(info_frame, variable=self.payment_var,
                                        values=["Pay at LIA", "Pay Now"], width=140)
        payment_menu.grid(row=0, column=3, padx=6, pady=4, sticky="w")
        
        ctk.CTkLabel(info_frame, text="Luggage:", font=("Arial", 11)).grid(row=1, column=2, padx=6, pady=4, sticky="e")
        self.luggage_var = ctk.StringVar(value="No Luggage")
        luggage_menu = ctk.CTkOptionMenu(info_frame, variable=self.luggage_var,
                                        values=list(LUGGAGE_PRICES.keys()), width=140, command=self.update_total_price)
        luggage_menu.grid(row=1, column=3, padx=6, pady=4, sticky="w")
        
        ctk.CTkLabel(info_frame, text="Email:", font=("Arial", 11)).grid(row=2, column=0, padx=6, pady=4, sticky="e")
        self.email_entry = ctk.CTkEntry(info_frame, width=300, height=30, font=("Arial", 11))
        self.email_entry.grid(row=2, column=1, columnspan=3, padx=6, pady=4, sticky="w")
        
        button_frame = ctk.CTkFrame(booking_frame)
        button_frame.pack(pady=6)
        self.book_btn = ctk.CTkButton(button_frame, text="✈️ Confirm Booking", 
                                     command=self.book_flight, font=("Arial", 12, "bold"), height=36, width=160)
        self.book_btn.grid(row=0, column=0, padx=6, pady=4)
        self.email_btn = ctk.CTkButton(button_frame, text="📧 Send Email", 
                                      command=self.send_email_confirmation, font=("Arial", 12, "bold"),
                                      height=36, width=160, state="disabled", fg_color="gray")
        self.email_btn.grid(row=0, column=1, padx=6, pady=4)
        
        self.display_flights()
    
    def display_flights(self):
        for widget in self.flight_scroll.winfo_children():
            widget.destroy()
        if not self.filtered_flights:
            no_flights = ctk.CTkLabel(self.flight_scroll, text="No flights match your filters", font=("Arial", 13))
            no_flights.pack(pady=15)
            return
        for flight in self.filtered_flights:
            flight_frame = ctk.CTkFrame(self.flight_scroll)
            flight_frame.pack(fill="x", pady=4, padx=4)
            info_text = f"{flight['flight_number']} | {flight['airline']} | {flight['aircraft']}\n"
            info_text += f"{flight['origin']} → {flight['destination']} | Gate {flight['gate']}\n"
            info_text += f"Dep: {flight['departure']} | Arr: {flight['arrival']} | {flight['duration']} | ${flight['price']}"
            info_label = ctk.CTkLabel(flight_frame, text=info_text, font=("Arial", 11), justify="left")
            info_label.pack(side="left", padx=10, pady=8)
            select_btn = ctk.CTkButton(flight_frame, text="Select", command=lambda f=flight: self.select_flight_action(f),
                                      width=80, height=30, font=("Arial", 11))
            select_btn.pack(side="right", padx=10, pady=6)
    
    def select_flight_action(self, flight):
        self.selected_flight = flight
        flight_text = f"{flight['flight_number']} - {flight['origin']} to {flight['destination']}"
        self.selected_flight_label.configure(text=flight_text)
        self.update_total_price()
    
    def add_passenger_dialog(self):
        if not self.selected_flight:
            messagebox.showerror("Error", "Please select a flight first!")
            return
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Passenger")
        dialog.geometry("750x550")
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="Enter Passenger Details", font=("Arial", 16, "bold")).pack(pady=8)
        ctk.CTkLabel(dialog, text="Minecraft Username:", font=("Arial", 11)).pack(pady=4)
        username_entry = ctk.CTkEntry(dialog, width=220, height=32, font=("Arial", 12))
        username_entry.pack(pady=4)
        ctk.CTkLabel(dialog, text="Select Seat:", font=("Arial", 13, "bold")).pack(pady=8)
        seat_frame = ctk.CTkScrollableFrame(dialog, width=680, height=320)
        seat_frame.pack(pady=8, padx=15)
        aircraft = self.selected_flight['aircraft']
        aircraft_config = self.aircraft_types[aircraft]
        selected_seat = {"seat": None}
        if aircraft == "Airbus A220-300":
            for row in range(1, aircraft_config["rows"] + 1):
                row_frame = ctk.CTkFrame(seat_frame)
                row_frame.pack(pady=2)
                ctk.CTkLabel(row_frame, text=f"Row {row}:", font=("Arial", 10), width=55).pack(side="left", padx=4)
                for seat_letter in aircraft_config["config_left"]:
                    seat_num = f"{row}{seat_letter}"
                    is_taken = seat_num in self.selected_flight['booked_seats']
                    color = "#D32F2F" if is_taken else "#4CAF50"
                    btn = ctk.CTkButton(row_frame, text=seat_num, width=45, height=28, fg_color=color, font=("Arial", 10),
                                       command=lambda s=seat_num: self.select_seat(s, selected_seat, dialog) if not is_taken else None)
                    btn.pack(side="left", padx=2)
                ctk.CTkLabel(row_frame, text="  ", width=18).pack(side="left")
                for seat_letter in aircraft_config["config_right"]:
                    seat_num = f"{row}{seat_letter}"
                    is_taken = seat_num in self.selected_flight['booked_seats']
                    color = "#D32F2F" if is_taken else "#4CAF50"
                    btn = ctk.CTkButton(row_frame, text=seat_num, width=45, height=28, fg_color=color, font=("Arial", 10),
                                       command=lambda s=seat_num: self.select_seat(s, selected_seat, dialog) if not is_taken else None)
                    btn.pack(side="left", padx=2)
        else:
            for row in range(1, aircraft_config["rows"] + 1):
                row_frame = ctk.CTkFrame(seat_frame)
                row_frame.pack(pady=2)
                ctk.CTkLabel(row_frame, text=f"Row {row}:", font=("Arial", 10), width=55).pack(side="left", padx=4)
                for seat_letter in aircraft_config["config"][:2]:
                    seat_num = f"{row}{seat_letter}"
                    is_taken = seat_num in self.selected_flight['booked_seats']
                    color = "#D32F2F" if is_taken else "#4CAF50"
                    btn = ctk.CTkButton(row_frame, text=seat_num, width=45, height=28, fg_color=color, font=("Arial", 10),
                                       command=lambda s=seat_num: self.select_seat(s, selected_seat, dialog) if not is_taken else None)
                    btn.pack(side="left", padx=2)
                ctk.CTkLabel(row_frame, text="  ", width=18).pack(side="left")
                for seat_letter in aircraft_config["config"][2:]:
                    seat_num = f"{row}{seat_letter}"
                    is_taken = seat_num in self.selected_flight['booked_seats']
                    color = "#D32F2F" if is_taken else "#4CAF50"
                    btn = ctk.CTkButton(row_frame, text=seat_num, width=45, height=28, fg_color=color, font=("Arial", 10),
                                       command=lambda s=seat_num: self.select_seat(s, selected_seat, dialog) if not is_taken else None)
                    btn.pack(side="left", padx=2)
        def confirm_passenger():
            username = username_entry.get().strip()
            if not username:
                messagebox.showerror("Error", "Please enter a username!")
                return
            if not selected_seat["seat"]:
                messagebox.showerror("Error", "Please select a seat!")
                return
            self.passengers.append({"username": username, "seat": selected_seat["seat"]})
            self.selected_flight['booked_seats'].append(selected_seat["seat"])
            self.update_passenger_list()
            self.update_total_price()
            dialog.destroy()
        ctk.CTkButton(dialog, text="✅ Confirm Passenger", command=confirm_passenger,
                     width=180, height=36, font=("Arial", 13, "bold")).pack(pady=8)
    
    def select_seat(self, seat, selected_seat_dict, dialog):
        selected_seat_dict["seat"] = seat
        messagebox.showinfo("Seat Selected", f"Seat {seat} selected!")
    
    def clear_passengers(self):
        if self.selected_flight:
            for passenger in self.passengers:
                if passenger["seat"] in self.selected_flight['booked_seats']:
                    self.selected_flight['booked_seats'].remove(passenger["seat"])
        self.passengers = []
        self.update_passenger_list()
        self.update_total_price()
    
    def update_passenger_list(self):
        if not self.passengers:
            self.passenger_list_label.configure(text="Passengers: None")
        else:
            passenger_text = ", ".join([f"{p['username']} ({p['seat']})" for p in self.passengers])
            self.passenger_list_label.configure(text=f"Passengers: {passenger_text}")
    
    def update_total_price(self, *args):
        if self.selected_flight and self.passengers:
            flight_cost = self.selected_flight['price'] * len(self.passengers)
            luggage_cost = LUGGAGE_PRICES[self.luggage_var.get()] * len(self.passengers)
            total = flight_cost + luggage_cost
            self.total_price_label.configure(text=f"${total} (Tickets: ${flight_cost} + Luggage: ${luggage_cost})")
        else:
            self.total_price_label.configure(text="$0")
    
    def search_flights(self, *args):
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            self.apply_filters()
            return
        self.apply_filters()
        self.filtered_flights = [f for f in self.filtered_flights 
                                if search_term in f['flight_number'].lower() or 
                                   search_term in f['airline'].lower()]
        self.display_flights()
    
    def apply_filters(self, *args):
        self.filtered_flights = self.flights.copy()
        if self.origin_var.get() != "All":
            self.filtered_flights = [f for f in self.filtered_flights if f['origin'] == self.origin_var.get()]
        if self.dest_var.get() != "All":
            self.filtered_flights = [f for f in self.filtered_flights if f['destination'] == self.dest_var.get()]
        dep_time = self.dep_time_var.get()
        if dep_time != "All":
            if "Morning" in dep_time:
                self.filtered_flights = [f for f in self.filtered_flights if 6 <= int(f['departure'].split(':')[0]) < 12]
            elif "Afternoon" in dep_time:
                self.filtered_flights = [f for f in self.filtered_flights if 12 <= int(f['departure'].split(':')[0]) < 18]
            elif "Evening" in dep_time:
                self.filtered_flights = [f for f in self.filtered_flights if 18 <= int(f['departure'].split(':')[0]) < 24]
        self.display_flights()
    
    def reset_filters(self):
        self.origin_var.set("All")
        self.dest_var.set("All")
        self.dep_time_var.set("All")
        self.search_entry.delete(0, 'end')
        self.filtered_flights = self.flights.copy()
        self.display_flights()
    
    def book_flight(self):
        email = self.email_entry.get().strip()
        if not email or "@" not in email:
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        if not self.selected_flight:
            messagebox.showerror("Error", "Please select a flight!")
            return
        if not self.passengers:
            messagebox.showerror("Error", "Please add at least one passenger!")
            return
        booking_ref = f"LUS{random.randint(100000, 999999)}"
        flight_cost = self.selected_flight['price'] * len(self.passengers)
        luggage_cost = LUGGAGE_PRICES[self.luggage_var.get()] * len(self.passengers)
        total_cost = flight_cost + luggage_cost
        self.current_booking = {
            'reference': booking_ref, 'email': email, 'flight': self.selected_flight,
            'passengers': self.passengers.copy(), 'payment': self.payment_var.get(),
            'luggage': self.luggage_var.get(), 'flight_cost': flight_cost,
            'luggage_cost': luggage_cost, 'total': total_cost
        }
        passenger_list = "\n".join([f"  - {p['username']} (Seat {p['seat']})" for p in self.passengers])
        confirmation = f"""
✈️ FLIGHT BOOKING CONFIRMED ✈️

Booking Reference: {booking_ref}

Passengers:
{passenger_list}

Flight Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flight: {self.selected_flight['flight_number']}
Airline: {self.selected_flight['airline']}
Aircraft: {self.selected_flight['aircraft']}
Gate: {self.selected_flight['gate']}
Route: {self.selected_flight['origin']} → {self.selected_flight['destination']}
Departure: {self.selected_flight['departure']}
Arrival: {self.selected_flight['arrival']}
Duration: {self.selected_flight['duration']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ticket cost: ${self.current_booking['flight_cost']}
Luggage: {self.luggage_var.get()} (+${self.current_booking['luggage_cost']})
Total passengers: {len(self.passengers)}
Total cost: ${self.current_booking['total']}
Payment: {self.payment_var.get()}

Thank you for choosing Lusail International Airport!
"""
        messagebox.showinfo("Booking Confirmed!", confirmation)
        self.email_btn.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])
    
    def send_email_confirmation(self):
        if not self.current_booking:
            messagebox.showerror("Error", "No booking to send!")
            return
        
        booking = self.current_booking
        passenger_list = "\n".join([f"  - {p['username']} (Seat {p['seat']})" for p in booking['passengers']])
        
        email_text = f"""
✈️ Flight Details | Lusail International Airport ✈️
Hello Dear Lusail International Airport Customer!
Please Carefully Look at the Flight details and Gate Number!
We Hope Safe travels!

Booking Reference: {booking['reference']}

Passengers:
{passenger_list}

Flight Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Flight Number: {booking['flight']['flight_number']}
Airline: {booking['flight']['airline']}
Aircraft: {booking['flight']['aircraft']}
Gate: {booking['flight']['gate']}
Route: {booking['flight']['origin']} → {booking['flight']['destination']}
Departure: {booking['flight']['departure']}
Arrival: {booking['flight']['arrival']}
Duration: {booking['flight']['duration']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ticket cost: ${booking['flight_cost']}
Luggage: {booking['luggage']} (+${booking['luggage_cost']})
Total passengers: {len(booking['passengers'])}
Total cost: ${booking['total']}
Payment Method: {booking['payment']}

Thank you for choosing Lusail International Airport!
Safe travels! 🌍

---
Lusail International Airport (LIA)
Atlantes City district of international Flying
"""
        
        email_sent = self.send_email(booking['email'], booking['reference'], email_text)
        
        if email_sent:
            messagebox.showinfo("Email Sent!", f"Confirmation sent to: {booking['email']}")
            self.current_booking = None
            self.passengers = []
            self.selected_flight = None
            self.email_btn.configure(state="disabled", fg_color="gray")
            self.email_entry.delete(0, 'end')
            self.selected_flight_label.configure(text="None")
            self.update_passenger_list()
            self.update_total_price()
            self.luggage_var.set("No Luggage")
        else:
            messagebox.showerror("Email Failed", "Could not send email. Check SMTP settings.")
    
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        if self.current_mode == "dark":
            ctk.set_appearance_mode("light")
            self.current_mode = "light"
            self.theme_btn.configure(text="☀️ Light Mode")
        else:
            ctk.set_appearance_mode("dark")
            self.current_mode = "dark"
            self.theme_btn.configure(text="🌙 Dark Mode")
    
    def show_airport_map(self):
        """Display the airport map with gate information"""
        map_window = ctk.CTkToplevel(self.root)
        map_window.title("Lusail International Airport - Terminal Map")
        map_window.geometry("900x700")
        map_window.grab_set()
        
        ctk.CTkLabel(map_window, text="🗺️ LIA Departures Terminal", 
                    font=("Arial", 20, "bold")).pack(pady=10)
        
        # Info about gates
        info_frame = ctk.CTkFrame(map_window)
        info_frame.pack(pady=10)
        
        gate_info = """
        Gate Layout:
        • Gate 3 - Left side (longest jet bridge)
        • Gate 1 - Middle position  
        • Gate 2 - Right position
        
        Your selected flight departs from:
        """
        
        ctk.CTkLabel(info_frame, text=gate_info, font=("Arial", 13), justify="left").pack(padx=20, pady=10)
        
        if self.selected_flight:
            gate_label = ctk.CTkLabel(info_frame, 
                                     text=f"✈️ {self.selected_flight['flight_number']} - Gate {self.selected_flight['gate']}", 
                                     font=("Arial", 16, "bold"), 
                                     text_color="#4CAF50")
            gate_label.pack(pady=5)
        else:
            ctk.CTkLabel(info_frame, text="No flight selected", 
                        font=("Arial", 14), text_color="gray").pack(pady=5)
        
        # Note about the map
        note_frame = ctk.CTkFrame(map_window)
        note_frame.pack(pady=10, fill="x", padx=20)
        
        note_text = """
        📍 Terminal Information:
        • 3 Jet Bridges (Gates 1, 2, 3)
        • Departures Terminal (Left building in Minecraft)
        • Random gate assignment for all flights
        • Check your boarding pass for gate number
        """
        
        ctk.CTkLabel(note_frame, text=note_text, font=("Arial", 12), 
                    justify="left").pack(padx=15, pady=10)
        
        close_btn = ctk.CTkButton(map_window, text="Close", command=map_window.destroy,
                                 width=150, height=40, font=("Arial", 14))
        close_btn.pack(pady=20)
    
    def send_email(self, to_email, booking_ref, confirmation):
        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "mqasem784@gmail.com"  # ← CHANGE THIS
            sender_password = "rdpoabfzdvbfanhh"  # ← CHANGE THIS
            
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
    
    def check_for_updates(self):
        """Check GitHub for latest version"""
        try:
            # Don't check if URL not configured
            if "YOUR_USERNAME" in GITHUB_RELEASES_URL:
                return
            
            import ssl
            context = ssl._create_unverified_context()
            
            req = urllib.request.Request(GITHUB_RELEASES_URL)
            req.add_header('User-Agent', 'Flight-Booking-App')
            
            with urllib.request.urlopen(req, timeout=5, context=context) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get('tag_name', '').replace('v', '')
                
                if latest_version and latest_version != CURRENT_VERSION:
                    download_url = data.get('html_url', '')
                    
                    result = messagebox.askyesno(
                        "Update Available!",
                        f"A new version is available!\n\n"
                        f"Current: v{CURRENT_VERSION}\n"
                        f"Latest: v{latest_version}\n\n"
                        f"Would you like to download it?"
                    )
                    
                    if result and download_url:
                        import webbrowser
                        webbrowser.open(download_url)
        except Exception as e:
            # Silently fail if update check doesn't work
            print(f"Update check failed: {e}")
            pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FlightBookingSystem()
    app.run()