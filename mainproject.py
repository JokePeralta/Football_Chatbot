from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Function to properly format player name
def format_player_name(player_name):
    parts = player_name.split('_')
    formatted_name = '_'.join(part.capitalize() for part in parts)
    return formatted_name

# Function to fetch player details from Wikipedia
def get_player_details(player_name):
    formatted_name = format_player_name(player_name)
    logging.debug(f"Fetching details for player: {formatted_name}")
    url = f"https://en.wikipedia.org/wiki/{formatted_name}"
    
    try:
        player_source = requests.get(url).text
        player_page = BeautifulSoup(player_source, "lxml")
        
        # Extract player details
        name = player_page.find("h1", {"id": "firstHeading"})
        if name:
            name = name.text.strip()
        else:
            logging.debug("Player not found")
            return {"error": "Hmm, I couldn't find that player. Could you double-check the name?"}
        
        # Look for the infobox table with multiple possible class names
        infobox = player_page.find("table", {"class": ["infobox vcard", "infobox biography vcard", "infobox", "infobox football biography"]})
        if not infobox:
            logging.debug("Infobox not found")
            return {"error": "I couldn't find detailed information about this player. They might not have a detailed page."}
        
        player_info = {"Name": name, "Position": "N/A", "Current club": "N/A", "Nationality": "N/A", "Date of Birth": "N/A", "Height": "N/A"}
        
        rows = infobox.find_all("tr")
        for row in rows:
            header = row.find("th")
            data = row.find("td")
            if header and data:
                header_text = header.text.strip()
                data_text = data.text.strip()
                
                if "Position" in header_text:
                    player_info["Position"] = data_text
                elif "Current team" in header_text:
                    player_info["Current club"] = data_text
                elif "Place of birth" in header_text:
                    player_info["Nationality"] = data_text
                elif "Date of birth" in header_text:
                    player_info["Date of Birth"] = data_text
                elif "Height" in header_text:
                    player_info["Height"] = data_text
        
        logging.debug(f"Player info: {player_info}")
        return {"details": player_info}
    except Exception as e:
        logging.error(f"Error fetching player data: {e}")
        return {"error": f"Oops! Something went wrong while fetching the player data: {e}"}

# Function to generate a human-like response
def generate_response(user_message):
    user_message = user_message.lower()
    if user_message in ['hi', 'hello', 'hey', 'namaste', 'sup']:
        return "Hey there, football fanatic! Ready to kick off some epic queries?<br><br>Drop the name of your favorite football star, and I'll serve up their career highlights quicker than a Messi dribble—all neatly organized in a sleek table!.<br><br>Format for the input is {Firstname_Lastname}"
    elif user_message in ['bye', 'goodbye', 'see you', 'thank you']:
        return "Signing off like a top striker after a hat-trick! Have a winning day ahead!<br><br>Stamped with football passion by Pratham and Shreyas."
    else:
        player_details = get_player_details(user_message)
        if "error" in player_details:
            return player_details["error"]
        else:
            return generate_table(player_details["details"])

# Function to generate an HTML table from player details
def generate_table(details):
    table = '<table><tr><th>Attribute</th><th>Value</th></tr>'
    for key, value in details.items():
        table += f'<tr><td>{key}</td><td>{value}</td></tr>'
    table += '</table>'
    return table

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Football Player Info Chatbot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-image: url('static/stadium.jpg'); /* Replace 'your_image_path.jpg' with your actual image path */
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                height: 100vh;
            }

            .chat-container {
                max-width: 600px;
                margin: 20px auto;
                background-color: rgba(255, 255, 255, 0.8); /* Adjust the opacity as needed */
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }

            .chat-box {
                max-height: 400px;
                overflow-y: auto;
                padding: 20px;
            }

            .chat-message {
                margin-bottom: 10px;
                background-color: #f0f0f0;
                border-radius: 8px;
                padding: 10px;
            }

            .user-input {
                display: flex;
                padding: 10px;
                background-color: #f0f0f0;
            }

            .user-input input[type="text"] {
                flex: 1;
                padding: 8px;
                font-size: 16px;
                border: none;
                border-radius: 4px 0 0 4px;
            }

            .user-input button {
                padding: 8px 16px;
                font-size: 16px;
                background-color: #007bff;
                color: #fff;
                border: none;
                border-radius: 0 4px 4px 0;
                cursor: pointer;
            }

            .user-input button:hover {
                background-color: #0056b3;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 10px;
            }

            table, th, td {
                border: 1px solid #ddd;
            }

            th, td {
                padding: 8px;
                text-align: left;
            }

            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-box" id="chat-box">
                <div class="chat-message">
                    <p>Step into my arena<br><br>I'm the Football Player Info Chatbot, ready to tackle your queries with the finesse of a seasoned defender.</p>
                    
                </div>
            </div>
            <div class="user-input">
                <input type="text" id="user-input" placeholder="Type here...">
                <button id="send-btn">Shoot</button>
            </div>
        </div>

        <script>
            document.addEventListener("DOMContentLoaded", function() {
                const chatBox = document.getElementById("chat-box");
                const userInput = document.getElementById("user-input");
                const sendBtn = document.getElementById("send-btn");

                sendBtn.addEventListener("click", function() {
                    sendMessage(userInput.value);
                });

                userInput.addEventListener("keypress", function(e) {
                    if (e.key === "Enter") {
                        sendMessage(userInput.value);
                    }
                });

                function sendMessage(message) {
                    if (message.trim() === "") return;

                    appendUserMessage(message);
                    userInput.value = "";

                    // Send user input to Python backend using Ajax
                    fetchPlayerDetails(message);
                }

                function appendMessage(message) {
                    const messageElement = document.createElement("div");
                    messageElement.classList.add("chat-message");
                    messageElement.innerHTML = `<p>${message}</p>`;
                    chatBox.appendChild(messageElement);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                function appendUserMessage(message) {
                    const messageElement = document.createElement("div");
                    messageElement.classList.add("chat-message", "user");
                    messageElement.innerHTML = `<p>You: ${message}</p>`;
                    chatBox.appendChild(messageElement);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                function appendBotMessage(message) {
                    const messageElement = document.createElement("div");
                    messageElement.classList.add("chat-message", "bot");
                    messageElement.innerHTML = message;
                    chatBox.appendChild(messageElement);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }

                function fetchPlayerDetails(playerName) {
                    fetch(`/get_player_details?player_name=${encodeURIComponent(playerName)}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.error) {
                                appendBotMessage(`<p>${data.error}</p>`);
                            } else {
                                appendBotMessage(data.details);
                            }
                        })
                        .catch(error => {
                            console.error("Error fetching player details:", error);
                            appendBotMessage("<p>Oops! Something went wrong while fetching player details.</p>");
                        });
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/get_player_details')
def fetch_player_details():
    player_name = request.args.get('player_name', '')
    response = generate_response(player_name)
    return jsonify({"details": response})

if __name__ == '__main__':
    app.run(debug=True)
