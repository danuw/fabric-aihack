import os
import string
import random

import json
import time
from azure.eventhub import EventHubProducerClient, EventData
from datetime import timedelta, datetime

# Variables 
nb_events = 1000

# Fabric Custom App
# Get fabric_endpoint and fabric_entity from the environment variables
fabric_endpoint = os.environ["FABRIC_ENDPOINT"]
fabric_entity = os.environ["FABRIC_ENTITY"]

print('credentials loaded')

producer = EventHubProducerClient.from_connection_string(
    conn_str=fabric_endpoint, eventhub_name=fabric_entity
)

def generate_uk_number_plate():
    """Generate a random modern UK number plate."""
    # Letters I, Q not used in the first two positions
    letters = string.ascii_uppercase.replace('I', '').replace('Q', '')
    # Age identifier: two digits, where the first digit indicates the year (0-9) and the second digit is 0 for March (first half of the year) and 5 for September (second half of the year)
    age_identifier = str(random.randint(0, 9)) + random.choice(['0', '5'])
    # Three random letters at the end, I and Q can be included here
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    
    # Combine to form a number plate
    number_plate = ''.join(random.choices(letters, k=2)) + age_identifier + ' ' + random_letters
    return number_plate


# foreach number in the numberPlates list, display a number plate on the screen
# and send it to the event stream
for _ in range(nb_events):

    number = generate_uk_number_plate()
    meta_list = {}

    meta_list["datetime"] = datetime.now().isoformat()
    meta_list["device_id"] = "BC-L1-0" + str(random.randint(1,5))
    meta_list["event_type"] = random.randint(1,2) # 1 for arrival, 2 for exit
    meta_list["plate_number"] = number

    print(meta_list)

    # # Send the data to Fabric
    event_data_batch = producer.create_batch()
    event_data_batch.add(EventData(json.dumps(meta_list)))
    producer.send_batch(event_data_batch)

    time.sleep(30)

print(f'Sent {nb_events} events to the event stream')