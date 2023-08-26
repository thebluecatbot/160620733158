from flask import Flask, request, jsonify
import requests
import asyncio

app = Flask(__name__)

# Function to fetch data from a given URL
def fetch_data_from_url(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            data = response.json()
            if "numbers" in data and isinstance(data["numbers"], list):
                return data["numbers"]
    except (requests.RequestException, asyncio.TimeoutError):
        pass
    return []

# Asynchronous function to fetch data from multiple URLs concurrently
async def fetch_all(urls):
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, fetch_data_from_url, url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

@app.route('/numbers', methods=['GET'])
def get_numbers():
    # Extract URLs from query parameters
    urls = request.args.getlist('url')
    
    # Create a new event loop for the asynchronous operations
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Fetch data from all URLs concurrently
    results = loop.run_until_complete(fetch_all(urls))
    loop.close()

    # Merge and sort the numbers
    merged_numbers = sorted(list(set(number for sublist in results for number in sublist)))
    
    # Return the merged numbers in a JSON response
    return jsonify({"numbers": merged_numbers})

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='localhost', port=8008, debug=True)
