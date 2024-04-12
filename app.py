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

    # Live view of the inputs
    dice_1 = st.number_input("Dice 1", min_value=1, max_value=6, step=1, key="dice_1")
    dice_2 = st.number_input("Dice 2", min_value=1, max_value=6, step=1, key="dice_2")
    dice_3 = st.number_input("Dice 3", min_value=1, max_value=6, step=1, key="dice_3")

    st.write("## Live view of the inputs")
    st.write(f"Dice 1: {dice_1}  |  Dice 2: {dice_2}  |  Dice 3: {dice_3}")

    # Subtract and add buttons
    subtract_dice_1 = st.button("-", key="subtract_dice_1")
    subtract_dice_2 = st.button("-", key="subtract_dice_2")
    subtract_dice_3 = st.button("-", key="subtract_dice_3")

    add_dice_1 = st.button("+", key="add_dice_1")
    add_dice_2 = st.button("+", key="add_dice_2")
    add_dice_3 = st.button("+", key="add_dice_3")

    # Update dice values based on button clicks
    if subtract_dice_1:
        dice_1 = max(1, dice_1 - 1)
    if subtract_dice_2:
        dice_2 = max(1, dice_2 - 1)
    if subtract_dice_3:
        dice_3 = max(1, dice_3 - 1)
    if add_dice_1:
        dice_1 = min(6, dice_1 + 1)
    if add_dice_2:
        dice_2 = min(6, dice_2 + 1)
    if add_dice_3:
        dice_3 = min(6, dice_3 + 1)

    # Commit button
    if st.button("Commit"):
        timestamp = generate_timestamp()
        data = {
            'Dice_1': dice_1,
            'Dice_2': dice_2,
            'Dice_3': dice_3,
            'Timestamp': timestamp
        }

        try:
            with pymongo.MongoClient(os.environ.get('MONGO_URI')) as mongo_client:
                db_name = os.environ.get('MONGO_DB_NAME', 'dice_app')
                db = mongo_client[db_name]

                collection_name = os.environ.get('MONGO_COLLECTION_NAME', 'dice_values')
                collection = db.create_collection(collection_name, capped=True, size=1024 * 1024, max=50)

                collection.insert_one(data)
                st.success("Data saved to MongoDB successfully.")

                # Append the new data to the data_df
                new_data = pd.DataFrame({'Dice_1': [dice_1], 'Dice_2': [dice_2], 'Dice_3': [dice_3], 'Timestamp': [timestamp]})
                data_df = pd.concat([data_df, new_data], ignore_index=True)

        except pymongo.errors.ConnectionFailure as e:
            st.error(f"Error connecting to MongoDB: {e}")

    # Display the recorded data with newest entries at the top
    st.subheader("Past records")
    recorded_data = data_df.sort_index(ascending=False)
    st.table(recorded_data)

if __name__ == '__main__':
    main()
