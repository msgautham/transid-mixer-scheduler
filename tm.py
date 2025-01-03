import io
import pandas as pd
import streamlit as st

# Function Definitions (Calculate Trip Times and Format Time)
def calculate_trip_times(start_time, batch_qty, pour_time, travel_time, pump_interval, buffer_time, qty_per_trip, num_vehicles):
    trips = []
    cumulative_qty = 0
    next_available_time = [start_time] * num_vehicles  # Track availability of each vehicle

    for i in range(batch_qty // qty_per_trip):
        trip_no = i + 1
        vehicle_no = (i % num_vehicles) + 1

        if vehicle_no == 1:
            work_start_time = next_available_time[vehicle_no - 1]
        else:
            previous_trip = trips[-1]
            work_start_time = previous_trip['Site Left Time After Pumping']

        plant_start_time = work_start_time + pour_time
        site_reach_time = plant_start_time + travel_time
        pump_start_time = site_reach_time + buffer_time
        site_left_time = pump_start_time + pump_interval
        plant_reach_time = site_left_time + travel_time

        next_available_time[vehicle_no - 1] = plant_reach_time

        cumulative_qty += qty_per_trip

        trip = {
            'Trip No.': trip_no,
            'Vehicle No.': vehicle_no,
            'Work Start Time': work_start_time,
            'Plant Start Time': plant_start_time,
            'Site Reach Time': site_reach_time,
            'Pump Start Time': pump_start_time,
            'Site Left Time After Pumping': site_left_time,
            'Buffer Time': buffer_time,
            'Plant Reach Time': plant_reach_time,
            'Round Trip Time': plant_reach_time - work_start_time,
            'Batch Qty per Trip': qty_per_trip,
            'Cumulative Qty': cumulative_qty
        }

        trips.append(trip)

    return trips

def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

# Function to generate Excel in memory using openpyxl
def generate_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer

# Streamlit App
st.title("Transit Mixer Trip Scheduler")

start_time = st.number_input("Start time of the first trip (in minutes, e.g., 300 for 5:00 AM)", min_value=0)
batch_qty = st.number_input("Total required batch quantity (in units)", min_value=1)
pour_time = st.number_input("Pour time into the TM (in minutes)", min_value=0)
travel_time = st.number_input("Travel time to the site (in minutes)", min_value=0)
pump_interval = st.number_input("Pumping interval (in minutes)", min_value=0)
buffer_time = st.number_input("Buffer time after pumping (in minutes)", min_value=0)
qty_per_trip = st.number_input("Batch quantity per trip", min_value=1)
num_vehicles = st.number_input("Number of vehicles (TM's)", min_value=1)

if st.button("Generate Trip Schedule"):
    trips = calculate_trip_times(start_time, batch_qty, pour_time, travel_time, pump_interval, buffer_time, qty_per_trip, num_vehicles)
    for trip in trips:
        trip['Work Start Time'] = format_time(trip['Work Start Time'])
        trip['Plant Start Time'] = format_time(trip['Plant Start Time'])
        trip['Site Reach Time'] = format_time(trip['Site Reach Time'])
        trip['Pump Start Time'] = format_time(trip['Pump Start Time'])
        trip['Site Left Time After Pumping'] = format_time(trip['Site Left Time After Pumping'])
        trip['Plant Reach Time'] = format_time(trip['Plant Reach Time'])

    df = pd.DataFrame(trips)
    st.write(df)
    
    excel_buffer = generate_excel(df)
    
    st.download_button(
        label="Download as Excel",
        data=excel_buffer,
        file_name='tm_scheduler.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
