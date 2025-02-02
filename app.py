import schedule
import time
import requests

# Global variable to store the last execution time
last_execution_time = time.time()

# Set the interval for the task (in seconds)
TASK_INTERVAL = 10

def task():
    global last_execution_time
    global schedule
    
    # Define the API endpoint
    url = "http://localhost:3000/api/getMessage"

    # Make a GET request to the API
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(f"API Response: {data['message']}")    
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

    schedule.clear()
    schedule.every(TASK_INTERVAL).seconds.do(task)    
    print("Task completed.")

    # Update the last execution time
    last_execution_time = time.time()

schedule.every(TASK_INTERVAL).seconds.do(task)

ctr=0
while True:
    print(ctr)
    ctr+=1
    # Get the current time
    current_time = time.time()

    if current_time - last_execution_time >= TASK_INTERVAL:
        schedule.run_pending()
        ctr=0

    time.sleep(1)  # Sleep to avoid busy-waiting