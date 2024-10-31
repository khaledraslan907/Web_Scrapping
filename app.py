# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

# Set page title
st.title("Yallakora Match Center")

# Get today's date for default
today = datetime.today()

# Define the range of years (e.g., from 2020 to the current year)
current_year = today.year
years = list(range(2020, current_year + 1))

# Define months and days
months = list(range(1, 13))
days = list(range(1, 32))

# Select year, month, and day
selected_year = st.selectbox("Select a year:", years, index=len(years) - 1)  # Default to the current year
selected_month = st.selectbox("Select a month:", months, index=today.month - 1)  # Default to current month
selected_day = st.selectbox("Select a day:", days, index=today.day - 1)  # Default to current day

# Function to validate the selected date
def validate_date(year, month, day):
    try:
        valid_date = datetime(year, month, day).strftime('%m/%d/%Y')
        return valid_date
    except ValueError:
        st.warning("Invalid date selected. Please check the day for the selected month.")
        return None

# Validate and format the selected date
date = validate_date(selected_year, selected_month, selected_day)

# Fetch and parse the page content
@st.cache_data
def fetch_matches(date):
    page = requests.get(f"https://www.yallakora.com/match-center/?date={date}")
    src = page.content
    soup = BeautifulSoup(src, "lxml")
    matches_details = []
    
    championships = soup.find_all("div", {'class': 'matchCard'})
    
    if not championships:
        st.warning("No championships found for this date.")
        return []

    def get_match_info(championship):
        try:
            championship_title = championship.find('h2').text.strip()
            all_matches = championship.find_all("li", {'class': 'liItem'})
            
            for match in all_matches:
                # Get team names
                team_A = match.find("div", {'class': 'teamA'}).text.strip()
                team_B = match.find("div", {'class': 'teamB'}).text.strip()
                
                # Get score
                match_result = match.find("div", {'class': 'MResult'}).find_all('span', {'class': 'score'})
                score = f"{match_result[0].text.strip()} - {match_result[1].text.strip()}" if match_result else "- -"
                
                # Get match time
                match_time = match.find("div", {'class': 'MResult'}).find('span', {'class': 'time'}).text.strip()
                
                # Add match details to the list
                matches_details.append({
                    'اسم البطولة': championship_title,
                    'الفريق الأول': team_A,
                    'الفريق الثاني': team_B,
                    'موعد المباراة': match_time,
                    'النتيجة': score
                })
        except AttributeError as e:
            st.error(f"An error occurred while fetching match info: {e}")

    # Extract matches for each championship
    for championship in championships:
        get_match_info(championship)
    
    return matches_details

# Add a button to fetch matches only after confirming date
if date:
    if st.button("Get Matches"):
        matches = fetch_matches(date)

        # Check if matches data was retrieved
        if matches:
            # Convert match details to DataFrame for better display
            df = pd.DataFrame(matches)
            st.write("### Match Details")
            st.dataframe(df)  # Display the data in a table format
            
            # Option to download the match details as CSV
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="Download match details as CSV",
                data=csv,
                file_name=f'matches_{date.replace("/", "-")}.csv',
                mime='text/csv',
            )
        else:
            st.write("No match details available for this date.")
