import pandas as pd
import re

def parse_duration(duration):
    """
    Converts a duration string (e.g., '1h 30m', '45m', '15m 20s') to total hours as a float.
    Returns a tuple of (hours, minutes, seconds).
    """
    if not isinstance(duration, str):
        return 0, 0, 0  # Return 0 for invalid or missing values

    hours = 0
    minutes = 0
    seconds = 0

    # Extract hours, minutes, seconds using regex
    hours_match = re.search(r'(\d+)h', duration)
    minutes_match = re.search(r'(\d+)m', duration)
    seconds_match = re.search(r'(\d+)s', duration)

    if hours_match:
        hours = int(hours_match.group(1))
    if minutes_match:
        minutes = int(minutes_match.group(1))
    if seconds_match:
        seconds = int(seconds_match.group(1))

    return hours, minutes, seconds

def normalize_time(row):
    """
    Normalize hours, minutes, and seconds so minutes and seconds don't exceed their limits.
    """
    total_seconds = row['hours'] * 3600 + row['minutes'] * 60 + row['seconds']
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    return int(hours), int(minutes), int(seconds)

# Load the file
data = pd.read_csv('[INSERT FILE LOCATION HERE]')

# Parse the duration column into hours, minutes, and seconds
data[['hours', 'minutes', 'seconds']] = data['duration'].apply(
    lambda x: pd.Series(parse_duration(x))
)

# Convert the payout column to numeric values
data['payout'] = data['payout'].replace('[\$,]', '', regex=True).astype(float)

# Aggregate total hours, minutes, seconds, and payout worked per day
total_time_per_day = data.groupby('workDate')[['hours', 'minutes', 'seconds', 'payout']].sum().reset_index()

# Normalize the aggregated time
total_time_per_day[['hours', 'minutes', 'seconds']] = total_time_per_day.apply(normalize_time, axis=1, result_type='expand')

# Sort by date in ascending order
total_time_per_day['workDate'] = pd.to_datetime(total_time_per_day['workDate'])
total_time_per_day = total_time_per_day.sort_values(by='workDate', ascending=True)

# Print total hours, minutes, seconds, and pay per day
for _, row in total_time_per_day.iterrows():
    print(f"Date: {row['workDate'].strftime('%Y-%m-%d')}, Hours: {row['hours']}, Minutes: {row['minutes']}, Seconds: {row['seconds']}, Total Earned: ${row['payout']:.2f}")

# Calculate total time and earnings
total_seconds_all_days = total_time_per_day['hours'] * 3600 + total_time_per_day['minutes'] * 60 + total_time_per_day['seconds']
total_seconds = total_seconds_all_days.sum()
total_hours = total_seconds // 3600
remaining_seconds = total_seconds % 3600
total_minutes = remaining_seconds // 60
total_seconds = remaining_seconds % 60

# Calculate total earnings
total_earnings = total_time_per_day['payout'].sum()

# Calculate total earnings for missions and referrals
rewards_data = data[data['payType'].isin(['missionReward', 'referralReward'])]
rewards_earnings = rewards_data['payout'].sum()

# Print the total overall time and earnings
print(f"\nTotal Overall Time: {total_hours} hours, {total_minutes} minutes, {total_seconds} seconds")
print(f"Total Overall Earnings: ${total_earnings:.2f}")

# Print the total earnings from missions and referrals
print(f"Total Earnings from missionReward and referralReward: ${rewards_earnings:.2f}")
