import subprocess
import json  # For parsing JSON

js_url =  '/Users/guyjasper/Documents/Guy/Projects/Python/youtube-po-token-generator/examples/one-shot.js'

result = subprocess.run(
            ["node", js_url],  # Ensure Node.js is installed and accessible
            capture_output=True,
            text=True
        )

if result.returncode != 0:
    raise Exception(f"Error running JavaScript: {result.stderr}")

data = result.stdout.strip()
print(f'data: {data}')

result_data = json.loads(data)  # Parse the JSON output

visitorData = result_data.get("visitorData")
if visitorData:
    print(f'visitorData: {visitorData}')
else:
    print('visitorData not found!')
    
po_token = result_data.get("poToken")  # Get the poToken value
if po_token:
    print(f'poToken: {po_token}')
else:
    print('poToken not found!')




