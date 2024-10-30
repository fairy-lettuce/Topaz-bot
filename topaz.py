import dotenv
import json
import os
import discord
import discord.ext
from discord import app_commands
import discord.ext.commands
import gspread
import gspread.utils

dotenv.load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILD = os.getenv("DISCORD_GUILD")
if DISCORD_GUILD is not None:
    GUILD = discord.Object(DISCORD_GUILD)
SHEET_URL = os.getenv("SHEET_URL")

with open("users.json", encoding="UTF-8") as f:
    users_info = json.load(f)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

gc = gspread.service_account()
sh = gc.open_by_key(SHEET_URL)
ws = sh.worksheet('sandbox')

@client.event
async def on_ready():
    print(f"We have logged in as {client.user} !")

@tree.command(name="sync", guild=GUILD)
async def sync(interaction:discord.Interaction):
    if interaction.user.id == int(os.getenv("ADMIN_DISCORD_ID")):
        await tree.sync(guild=discord.Object(id=interaction.guild_id))
        print("Synced")
        await interaction.response.send_message("Successfully synced!")
    else:
        await interaction.response.send_message("not owner")

@tree.command()
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("Test command")

@tree.command(name="book", description="帳簿を記録するよ", guild=GUILD)
@discord.app_commands.describe(
    buy_date="買った日",
    title="買った場所",
    buyer="買った人",
    price="値段",
    rate_user0=f"{users_info["users"][0]["name"]}の折半割合",
    rate_user1=f"{users_info["users"][1]["name"]}の折半割合",
    rate_user2=f"{users_info["users"][2]["name"]}の折半割合"    
)
@discord.app_commands.rename(
    rate_user0=f"rate_{users_info["users"][0]["name"]}",
    rate_user1=f"rate_{users_info["users"][1]["name"]}",
    rate_user2=f"rate_{users_info["users"][2]["name"]}"
)
async def book(interaction: discord.Interaction,
               buy_date: str,
               title: str,
               buyer: discord.User,
               price: int,
               rate_user0: int,
               rate_user1: int,
               rate_user2: int):
    embed = discord.Embed(
        title=f"帳簿記録: {title}",
        description=f"",
        color=discord.Color.pink()
    )
    embed.add_field(name="タイトル", value=title)
    embed.add_field(name="購入者", value=buyer)
    embed.add_field(name="購入日", value=buy_date)
    embed.add_field(name="値段", value=price)
    embed.add_field(name="折半比率", value=f"{rate_user0} : {rate_user1} : {rate_user2}")
    await interaction.response.send_message(content="これで帳簿を記録したよ！", embed=embed, ephemeral=False)
    data = [
        buy_date,
        title,
        convert_name_to_emoji(buyer.name),
        price,
        rate_user0,
        rate_user1,
        rate_user2
    ]
    export_sheet(data)

def convert_name_to_emoji(name: str) -> str:
    for v in users_info["users"]:
        if name == v["name"]:
            return v["emoji"]
    return ""

def export_sheet(data: list):
    ws.append_row(data, insert_data_option=gspread.utils.InsertDataOption.overwrite, table_range="A1:G1")

if DISCORD_TOKEN is not None:
    client.run(DISCORD_TOKEN)
