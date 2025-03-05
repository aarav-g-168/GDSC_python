Discord Bot README

📌 Introduction

This is a Discord bot built using Python and the discord.py library. It includes several features such as AI-powered chat, reminders, polling, and user management. The bot integrates with the Gemini API for AI-powered responses and supports user interaction through various commands.

⚙️ Features

🤖 AI Chat
Command: !useai <message>
Description: Uses Gemini AI to generate responses for user messages.
Example:
!useai What is quantum computing?

📝 Text Summarization
Command: !summarize <text>
Description: Uses Gemini AI to generate a simple summary of the given text.
Example:
!summarize The history of computers dates back to the 19th century...

⏰ Reminder System
Set a Reminder: !remind <DD-MM-YYYY HH:MM> > <message>
View Reminders: !reminders
Modify Reminder: !modifyreminder <reminder_id> > <new_time> > <new_message>
Delete Reminder: !deletereminder <reminder_id>
Example:
!remind 05-03-2025 14:30 > Buy groceries

📊 Poll System
Command: !poll <question> > <option1> <option2> ...
Description: Creates a poll where users can vote using reactions.
Example:
!poll What is your favorite color? > Red Blue Green Yellow

🎉 Welcome Messages
The bot automatically sends a welcome message when a new member joins the server.

🛠️ Installation & Setup

1️⃣ Prerequisites
Ensure you have Python installed along with the required dependencies:
pip install discord.py python-dotenv requests google-generativeai

2️⃣ Setup Environment Variables
Create a .env file in the project directory and add:
DISCORD_TOKEN=your-discord-bot-token
GEMINI_API_KEY=your-gemini-api-key

3️⃣ Run the Bot
Execute the script with:
python bot.py

🔧 Error Handling

API Errors: If the bot fails to connect to the Gemini API, ensure your API key is valid.
Invalid Commands: If commands are not responding, check the bot's permissions and message content intent settings.
Reminder Issues: Ensure the format is correct (DD-MM-YYYY HH:MM) and the time is in the future.

📜 License

This project is open-source. Feel free to modify and use it according to your needs.
✨ Future Enhancements
🎵 Add music playback feature.
📅 Implement a scheduling system for recurring reminders.
🔎 Improve AI capabilities with additional features.

🤝 Contributing
If you have suggestions or improvements, feel free to submit a pull request or open an issue.
🚀 Happy coding!
