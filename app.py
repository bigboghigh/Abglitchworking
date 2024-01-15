from flask import Flask, request, jsonify
import requests
import time
import json
import threading

app = Flask(__name__)

@app.route('/add/coins.php', methods=['GET', 'POST', 'OPTIONS'])
def handle_request():
    if request.method == 'OPTIONS':  # Handling OPTIONS request
        headers = {
            'Access-Control-Allow-Origin': '*',  # Adjust as needed
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)

    if request.method == 'POST':
        key = request.json.get('key')
        token = request.json.get('token')
        number = request.json.get('number') 
        oldbal = request.json.get('oldbal') 
        userid = request.json.get('userid') 

        missing_parameters = []

        # Check for missing parameters
        if key is None:
            missing_parameters.append("key")
        if token is None:
            missing_parameters.append("token")
        if number is None:
            missing_parameters.append("number")
        if oldbal is None:
            missing_parameters.append("oldbal")
        if userid is None:
            missing_parameters.append("userid")

        if missing_parameters:
            error_message = "Missing parameters: {}".format(', '.join(missing_parameters))
            return jsonify({"error": error_message}), 400

        try:
            number = int(number)
            oldbal = int(oldbal)
        except ValueError:
            return jsonify({"error": "Invalid number parameter"}), 400

        def send_requests(key, token, number, oldbal, userid):
            url = 'https://abtalk-by-romeo.vercel.app/activate?key={}&deviceid={}'.format(key, token)

            headers = {
                'Host': 'abtalk-by-romeo.vercel.app'
            }

            

            while True:
                try:
                    response = requests.get(url=url, headers=headers)
                    print("API Response: {}".format(response.text))
                    print("API Status Code: {}".format(response.status_code))
                    response.raise_for_status()  # Raise an HTTPError for bad responses
                    response_json = response.json()
                    credit_amount = response_json.get('data', {}).get('creditsAmount')
                    if credit_amount is not None:
                        if credit_amount >= number:
                            send_put_request(userid)  # Send last PUT request when credit_amount >= number
                            break
                        elif credit_amount >= oldbal + 999:
                            send_put_request(userid)  # Send PUT request when credit_amount increases by 1000
                            oldbal = oldbal + 999  # Update oldbal when increased by 1000

                        # Log the response and status code
                        print("API Response: {}".format(response.text))
                        print("API Status Code: {}".format(response.status_code))

                except requests.exceptions.HTTPError as e:
                    # Log the error response status code
                    print("API Error Response Status Code: {}".format(response.status_code)) 
                    print("Api text: {}".format(response.text))  
                    break
                except Exception as e:
                    # Log the exception
                    print("Error in API request: {}".format(e))
                    break

                time.sleep(10)

        # Start the thread for continuous requests
        thread = threading.Thread(target=send_requests, args=(key, token, number, oldbal, userid))
        thread.start()

        # Return initial response 'done'
        return jsonify({"message": "done"}) 

    return app.send_static_file('index.html')

def send_put_request(userid):
    url = "https://sprout-tiny-penguin.glitch.me/deductUserbalance/" + str(userid)
    headers = {"content-type": "application/json"}
    payload = {"amountToDeduct": "1"}

    response = requests.put(url, json=payload, headers=headers)

    # Log the response and status code
    print("PUT Request Response: {}".format(response.text))
    print("PUT Request Status Code: {}".format(response.status_code))

    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
