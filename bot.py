import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import requests
import asyncio
from datetime import datetime, timedelta
from google import genai
import yt_dlp as youtube_dl

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Reminders storage
reminders = []
music_queue = []

# Gemini API integration
def get_gemini_response(prompt):

    try:
        response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt])
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Gemini API Error: {e}")
        return "Sorry, there was an error processing your request."

# Welcome new members
@bot.event
async def on_member_join(member):
    try:
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f"Welcome {member.mention} to the server! �")
    except Exception as e:
        print(f"Error in on_member_join: {e}")

@bot.command(name="summarize")
async def summarize(ctx, *, message: str):

    prompt = f"simple summarize: {message}"

    try:
        response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt])
        await ctx.send(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Gemini API Error: {e}")
        return "Sorry, there was an error processing your request."

# Chat with Gemini API
@bot.command(name="useai")
async def chat(ctx, *, message: str):
    try: 
        response = get_gemini_response(message)
        await ctx.send(response)
    except Exception as e:
        print(f"Error in chat command: {e}")
        await ctx.send("Sorry, there was an error processing your message.")


# Reminder system
from itertools import count

# Counter for generating unique reminder IDs
reminder_id_counter = count(start=1)

@bot.command(name="remind")
async def remind(ctx, *, input_str: str):
    try:
        parts = input_str.split('>', 1)
        if len(parts) != 2:
            await ctx.send("Invalid format. Use **!remind DD-MM-YYYY HH:MM > Your message**.")
            return

        time_str, message = parts[0].strip(), parts[1].strip()
        reminder_time = datetime.strptime(time_str, "%d-%m-%Y %H:%M")

        if reminder_time < datetime.now():
            await ctx.send("The time you entered has already passed. Please enter a valid future time.")
            return

        # Assign a unique ID to the reminder
        reminder_id = next(reminder_id_counter)
        reminders.append([ctx.author.id, reminder_time, message, reminder_id])  # Use a list instead of a tuple
        await ctx.send(f"Reminder set for **{reminder_time.strftime('%d-%m-%Y %H:%M')}** (ID: {reminder_id}): {message}")
    except ValueError:
        await ctx.send("Invalid time format. Use **DD-MM-YYYY HH:MM**.")
    except Exception as e:
        print(f"Error in remind command: {e}")
        await ctx.send("Sorry, there was an error setting your reminder.")

@bot.command(name="reminders")
async def show_reminders(ctx):
    try:
        user_id = ctx.author.id
        user_reminders = [reminder for reminder in reminders if reminder[0] == user_id]

        if not user_reminders:
            await ctx.send("You have no upcoming reminders.")
            return

        reminder_list = []
        for reminder in user_reminders:
            reminder_time, message, reminder_id = reminder[1], reminder[2], reminder[3]
            formatted_time = reminder_time.strftime("%d-%m-%Y %H:%M")
            reminder_list.append(f"**ID: {reminder_id}** - **{formatted_time}**: {message}")

        await ctx.send(f"**Your upcoming reminders:**\n" + "\n".join(reminder_list))
    except Exception as e:
        print(f"Error in show_reminders command: {e}")
        await ctx.send("Sorry, there was an error fetching your reminders.")

@bot.command(name="modifyreminder")
async def modify_reminder(ctx, *, input_str: str):
    try:
        user_id = ctx.author.id
        # Split the input string using '>' as the delimiter
        parts = input_str.split('>', maxsplit=2)
        if len(parts) < 2:
            await ctx.send("Invalid format. Use **!modifyreminder <reminder_id> > <new_time> > <new_message>**.")
            return

        reminder_id = int(parts[0].strip())  # First part is the reminder ID
        new_time = parts[1].strip() if len(parts) > 1 else None  # Second part is the new time
        new_message = parts[2].strip() if len(parts) > 2 else None  # Third part is the new message

        # Find the reminder by ID and user ID
        reminder_found = None
        for reminder in reminders:
            if reminder[0] == user_id and reminder[3] == reminder_id:  # Check user ID and reminder ID
                reminder_found = reminder
                break

        if not reminder_found:
            await ctx.send("Reminder not found. Make sure you entered the correct reminder ID.")
            return

        # Update the reminder time if provided
        if new_time:
            try:
                new_reminder_time = datetime.strptime(new_time, "%d-%m-%Y %H:%M")
                if new_reminder_time < datetime.now():
                    await ctx.send("The new time you entered has already passed. Please enter a valid future time.")
                    return
                reminder_found[1] = new_reminder_time  # Update the time (lists are mutable)
            except ValueError:
                await ctx.send("Invalid time format. Use **DD-MM-YYYY HH:MM**.")
                return

        # Update the reminder message if provided
        if new_message:
            reminder_found[2] = new_message  # Update the message (lists are mutable)

        # Confirm the update
        await ctx.send(f"Reminder updated successfully!\n"
                       f"New time: **{reminder_found[1].strftime('%d-%m-%Y %H:%M')}**\n"
                       f"New message: **{reminder_found[2]}**")
    except Exception as e:
        print(f"Error in modify_reminder command: {e}")
        await ctx.send("Sorry, there was an error modifying your reminder.")

@bot.command(name="deletereminder")
async def delete_reminder(ctx, reminder_id: int):
    try:
        user_id = ctx.author.id
        # Find the reminder by ID and user ID
        reminder_found = None
        for reminder in reminders:
            if reminder[0] == user_id and reminder[3] == reminder_id:  # Check user ID and reminder ID
                reminder_found = reminder
                break

        if not reminder_found:
            await ctx.send("Reminder not found. Make sure you entered the correct reminder ID.")
            return

        # Remove the reminder from the list
        reminders.remove(reminder_found)
        await ctx.send(f"Reminder with ID **{reminder_id}** has been deleted.")
    except Exception as e:
        print(f"Error in delete_reminder command: {e}")
        await ctx.send("Sorry, there was an error deleting your reminder.")


@tasks.loop(minutes=1)
async def check_reminders():
    try:
        now = datetime.now()
        for reminder in reminders[:]:
            user_id, reminder_time, message, reminder_id = reminder
            if now >= reminder_time:
                try:
                    user = await bot.fetch_user(user_id)
                    await user.send(f"Reminder: {message}")
                    reminders.remove(reminder)
                except discord.NotFound:
                    print(f"User with ID {user_id} not found. Removing reminder.")
                    reminders.remove(reminder)
                except discord.Forbidden:
                    print(f"Could not send a DM to user with ID {user_id}. They may have blocked the bot or disabled DMs.")
                    reminders.remove(reminder)
                except Exception as e:
                    print(f"Error sending reminder to user {user_id}: {e}")
    except Exception as e:
        print(f"Error in check_reminders task: {e}")

@tasks.loop(minutes=1)
async def auto_delete_expired_reminders():
    try:
        now = datetime.now()
        reminders[:] = [reminder for reminder in reminders if reminder[1] > now]
    except Exception as e:
        print(f"Error in auto_delete_expired_reminders task: {e}")



# Poll system
@bot.command(name="poll")
async def poll(ctx, *, input: str = None):  # Make input optional
    try:
        # Check if input is missing
        if input is None:
            await ctx.send("Please use the poll command like this: `!poll <question> > <option1> <option2> ...`")
            return

        # Split the input into question and options using the '>' delimiter
        if '>' not in input:
            await ctx.send("Invalid format. Use `!poll <question> > <option1> <option2> ...`")
            return

        # Split into question and options
        question, options_str = input.split('>', 1)
        question = question.strip()  # Remove leading/trailing spaces
        options = options_str.split()  # Split options into a list

        # Validate the number of options
        if len(options) > 10:
            await ctx.send("You can only have up to 10 options.")
            return

        # Format the options
        formatted_options = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])

        # Send the poll message
        poll_message = await ctx.send(f"**Poll: {question}**\n{formatted_options}")

        # Add reactions for each option
        for i in range(len(options)):
            await poll_message.add_reaction(f"{i+1}\N{COMBINING ENCLOSING KEYCAP}")
    except Exception as e:
        print(f"Error in poll command: {e}")
        await ctx.send("Sorry, there was an error creating the poll.")


# Start the bot
@bot.event
async def on_ready():
    try:
        print(f"Logged in as {bot.user}")
        check_reminders.start()
        auto_delete_expired_reminders.start()
    except Exception as e:
        print(f"Error in on_ready: {e}")

# Run the bot
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"Error starting the bot: {e}")
