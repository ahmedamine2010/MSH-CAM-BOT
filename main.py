import discord
from discord.ext import commands, tasks
import asyncio
from keep_alive import keep_alive

keep_alive()
intents = discord.Intents.default()
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace these with your channel IDs
camera_channel_ids = [1200493375867064450, 1200493451293229087]  # List of camera room channel IDs
afk_channel_id = 1172473342461214762
warning_channel_id = 1200769349674356836

# Configuration parameters
camera_check_interval = 15  # in seconds (adjust as needed)
warning_threshold = 1  # number of warnings before moving to AFK
time_between_notifications = 12  # seconds between the first and second notification

# Dictionary to track warnings for each user in each camera room
user_warnings = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    camera_check.start()

@tasks.loop(seconds=camera_check_interval)
async def camera_check():
    afk_channel = bot.get_channel(afk_channel_id)
    warning_channel = bot.get_channel(warning_channel_id)

    if afk_channel and warning_channel:
        for camera_channel_id in camera_channel_ids:
            camera_channel = bot.get_channel(camera_channel_id)

            if camera_channel:
                for member in camera_channel.members:
                    if not member.voice.self_video:
                        user_id = member.id
                        if user_id not in user_warnings:
                            user_warnings[user_id] = {camera_channel_id: 1}
                            await warning_channel.send(f"{member.mention}, Please Turn on your Camera within 30 seconds or you will be kicked from one of the camera rooms.")
                        elif user_warnings[user_id].get(camera_channel_id, 0) >= warning_threshold:
                            await member.move_to(afk_channel)
                            await warning_channel.send(f"{member.mention} You were moved to the AFK room for not turning on your camera within the time limit in one of the camera rooms.")
                            del user_warnings[user_id]  # remove user from warnings after moving
                        else:
                            user_warnings[user_id][camera_channel_id] = user_warnings[user_id].get(camera_channel_id, 0) + 1

        # Sleep outside of the loop
        await asyncio.sleep(time_between_notifications)

        # Add a counter to limit the number of iterations (for example, stop after 10 iterations)
        iterations_counter = getattr(camera_check, 'iterations_counter', 0)
        iterations_counter += 1
        camera_check.iterations_counter = iterations_counter

        if iterations_counter >= 10:  # Adjust the limit as needed
            camera_check.stop()  # Stop the loop after reaching the specified number of iterations

# Command to greet users
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello, I am your camera-monitoring bot!')

# Replace 'YOUR_TOKEN' with the actual token you copied
bot.run('MTIwMDU3OTk2NzI1NjM3NTI5Ng.G02u6h.01EBtTNiV2rEIMFPxVoLWDTb-rJ0aWK_GhvKgU')
