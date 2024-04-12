import os
import streamlit as st
import pymongo
from datetime import datetime
import pytz
import pandas as pd

# Function to generate a unique timestamp in IST
def generate_timestamp():
    ist = pytz.timezone('Asia/Kolkata')  # IST timezone
    timestamp = datetime.now(ist)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

# Streamlit app
def main():
    st.title("Dice Value Recorder")

    # Initialize an empty DataFrame to store the data
    data_df = pd.DataFrame(columns=['Dice_1', 'Dice_2', 'Dice_3', 'Timestamp'])

    # Input fields for dice values
    dice_1 = st.number_input("Dice 1", min_value=1, max_value=6, step=1)
    dice_2 = st.number_input("Dice 2", min_value=1, max_value=6, step=1)
    dice_3 = st.number_input("Dice 3", min_value=1, max_value=6, step=1)

    # Create a DataFrame row with the input values
    input_data = pd.DataFrame({
        'Dice_1': [dice_1],
        'Dice_2': [dice_2],
        'Dice_3': [dice_3],
        'Timestamp': [generate_timestamp()]
    })

    # Display the input data in a tabular view
    st.subheader("Input Data")
    st.table(input_data)

    # Commit button
    if st.button("Commit"):
        # Append the input data to the data_df
        data_df = pd.concat([data_df, input_data], ignore_index=True)

        # Save the data to MongoDB
        try:
            with pymongo.MongoClient(os.environ.get('MONGO_URI')) as mongo_client:
                db_name = os.environ.get('MONGO_DB_NAME', 'dice_app')
                db = mongo_client[db_name]

                collection_name = os.environ.get('MONGO_COLLECTION_NAME', 'dice_values')
                collection = db[collection_name]

                data_dict = input_data.to_dict('records')[0]  # Convert DataFrame row to dictionary
                collection.insert_one(data_dict)
                st.success("Data saved to MongoDB successfully.")

        except pymongo.errors.ConnectionFailure as e:
            st.error(f"Error connecting to MongoDB: {e}")

    # Display the recorded data with newest entries at the top
    st.subheader("Recorded Data")
    recorded_data = data_df.sort_index(ascending=False)
    st.table(recorded_data)

if __name__ == '__main__':
    main()
