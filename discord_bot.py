import discord
from discord.ext import commands
from discord import app_commands
import os
import shutil
from dotenv import load_dotenv
from game import Game
import asyncio


dir_path = os.path.dirname(os.path.realpath(__file__))

# Load token from environment variable
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True 
intents.voice_states = True 
bot = commands.Bot(command_prefix="!", intents=intents)

voice_client = None

# Initialize game
game = None

# Event: Bot is ready
@bot.event
async def on_ready():
    try:
        await bot.tree.sync() 
        print("Slash commands synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"We have logged in as {bot.user}")

# Slash Command: /start_game
@bot.tree.command(name="start_game", description="Start a History Bee game")
@app_commands.describe(channel="Voice Channel to join", file="PDF File of History Bee Packet")
async def join(interaction: discord.Interaction, channel: discord.VoiceChannel, file: discord.Attachment):
    global voice_client, game
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()  # Disconnect if already connected
    voice_client = await channel.connect()

    os.makedirs("bee_packets", exist_ok=True)

    # Download and save the file locally
    file_path = os.path.join("bee_packets", file.filename)
    await file.save(file_path)

    await interaction.response.send_message(f"Joined {channel.name}! and downloaded file")

    game = Game(file_path)
    print(game.qa)

# Slash Command: /next_question
@bot.tree.command(name="next_question", description="Play the next tossup")
@app_commands.describe(tossup_skip="If you want to skip to a specific tossup, enter its number here")
async def play(interaction: discord.Interaction, tossup_skip: int = None):
    global voice_client
    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("I am not connected to a voice channel!")
        return

    # Defer the response immediately
    await interaction.response.defer()

    # Use the game's current question number if no value is provided
    tossup_num = tossup_skip if tossup_skip is not None else game.qNum
    game.qNum = tossup_num

    file_name = game.get_tossup()
    file_path = os.path.join(dir_path, file_name)

    print(file_path)

    audio_path = os.path.join(os.getcwd(), file_path)
    if not os.path.isfile(audio_path):
        await interaction.followup.send(f"File '{file_name}' not found!")
        return

    async def question_end():
        await asyncio.sleep(5)
        # game.midQ = False
        await interaction.channel.send("Question has ended")
        game.next_question()

    def sync_after_wrapper(async_func):
        def wrapper(error):
            if error:
                print(f"Error during playback: {error}")
            asyncio.run_coroutine_threadsafe(async_func(), bot.loop)
        return wrapper

    # Play the audio file
    game.midQ = True
    if voice_client.is_playing():
        voice_client.stop()  # Stop any currently playing audio
    voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_path)), after=sync_after_wrapper(question_end))
    await interaction.followup.send(f"Now playing: {file_name}")


# Slash Command: /buzz
@bot.tree.command(name="buzz", description="Buzz on the current tossup")
async def buzz(interaction: discord.Interaction):
    global voice_client
    if not voice_client or not game.midQ:
        await interaction.response.send_message("Question has not begun.")
        return

    # Pause the audio playback
    voice_client.pause()

    user = interaction.user
    await interaction.response.send_message(f"{user.name}, you have 5 seconds to answer.")

    def check(message: discord.Message):
        return message.author == user and message.channel == interaction.channel

    try:
        answer_message = await bot.wait_for('message', timeout=5.0, check=check)
        answer = answer_message.content

        # Check if the answer is correct
        is_correct = game.buzz(user.name, answer)

        if is_correct:
            game.next_question()
            await interaction.followup.send("Correct! You may proceed to the next question.")
        else:
            voice_client.resume()
            await interaction.followup.send(f"Incorrect. Continuing the question.")

    except asyncio.TimeoutError:
        await interaction.followup.send(f"{user.name}, you ran out of time. Continuing the question.")
        voice_client.resume()


# Slash Command: /scoreboard
@bot.tree.command(name="scoreboard", description="Get the scores")
async def scoreboard(interaction: discord.Interaction):
    scores = game.scores

    if not scores:
        formatted_scores = "No scores available yet"
    else:
        formatted_scores = "Scoreboard:\n"
        formatted_scores += "```\n" 
        formatted_scores += "{:<20} {:>10}\n".format("Team", "Score") 
        formatted_scores += "-" * 30 + "\n" 
        for team, score in scores.items():
            formatted_scores += "{:<20} {:>10}\n".format(team, score) 
        formatted_scores += "```" 

    # Send the formatted scoreboard
    await interaction.response.send_message(formatted_scores)


# Slash Command: /end_game
@bot.tree.command(name="end_game", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    global voice_client
    if voice_client and voice_client.is_connected():
        if voice_client.is_playing():
            voice_client.stop()

        await voice_client.disconnect()
        voice_client = None
        for filename in os.listdir("audio_files"):
            file_path = os.path.join("audio_files", filename)
            try:
                os.remove(file_path)
            except PermissionError:
                print(f"File {file_path} is still in use. Retrying after ensuring playback has stopped.")
                await asyncio.sleep(1)  
                os.remove(file_path) 

        for filename in os.listdir("bee_packets"):
            file_path = os.path.join("bee_packets", filename)
            os.remove(file_path)

        await interaction.response.send_message("Ended game!")
    else:
        await interaction.response.send_message("No active game!")

# Run the bot
bot.run(TOKEN)
