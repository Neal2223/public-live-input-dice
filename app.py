import os
import streamlit as st
import pymongo
from datetime import datetime

# MongoDB configuration
try:
    mongo_client = pymongo.MongoClient(os.environ.get('MONGO_URI'))
    db_name = os.environ.get('MONGO_DB_NAME', 'dice_app')
    db = mongo_client[db_name]

    try:
        collection_name = os.environ.get('MONGO_COLLECTION_NAME', 'dice_values')
        collection = db[collection_name]
    except Exception as e:
        st.error(f"Error creating collection: {e}")
        exit(1)

except pymongo.errors.ConnectionFailure as e:
    st.error(f"Error connecting to MongoDB: {e}")
    exit(1)

# Function to generate a unique timestamp
def generate_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Streamlit app
def main():
    st.title("Dice Value Recorder")

    # Input fields for dice values
    dice_1 = st.number_input("Dice 1", min_value=1, max_value=6, step=1)
    dice_2 = st.number_input("Dice 2", min_value=1, max_value=6, step=1)
    dice_3 = st.number_input("Dice 3", min_value=1, max_value=6, step=1)

    # Commit button
    if st.button("Commit"):
        timestamp = generate_timestamp()
        data = {
            'Dice_1': dice_1,
            'Dice_2': dice_2,
            'Dice_3': dice_3,
            'Timestamp': timestamp
        }
        collection.insert_one(data)
        st.success("Data saved to MongoDB successfully.")

    # Display the recorded data
    st.subheader("Recorded Data")
    data = collection.find({}, {'_id': 0})  # Exclude the _id field from the result
    st.write(list(data))

if __name__ == '__main__':
    main()
