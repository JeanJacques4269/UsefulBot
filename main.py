from lol_fonctions import *
# link : https://discord.com/api/oauth2/authorize?client_id=1094985990281629716&permissions=3072&scope=bot

import discord
from discord.ext import commands
from discord.ext.commands import Bot

import os
from dotenv import load_dotenv
import random

import openai

load_dotenv()
token = os.getenv("TOKEN")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)

cringe_emojis = [
    "(●'◡'●)",
    "(◕‿◕✿)",
    "(*/ω＼*)",
    "(´｡• ᵕ •｡`)",
    "(´｡• ᵕ •｡`)",
    "☆*: .｡. o(≧▽≦)o .｡.:*☆",
    "(^///^)",
    "༼ つ ◕_◕ ༽つ",
    "👈(⌒▽⌒)👉",
    "👉(⌒▽⌒)👈",
    "👉(◕‿◕)👈",
]


def extract_availability(message):
    # Authenticate with the OpenAI API using your API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Define the prompt to send to the OpenAI API
    template = """
    Lundi : 
    Mardi : 
    Mercredi : 
    Jeudi : 
    Vendredi : 
    Samedi : 
    Dimanche : """
    prompt = f"Modify this template : \n{template}\n according to the message of a user : \n'{message}' \n use ✅ and ❌"
    # Call the OpenAI API to generate a response to the prompt
    print(f"[INFO] Sending prompt to OpenAI API]")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=128,
        n=1,
        stop=None,
        temperature=0.2,
    )
    print(f"[INFO] OpenAI API responded")

    print(response.choices[0].text)
    # Return the response
    return response.choices[0].text.lstrip()


@bot.command(
    name="extract", help="Extract availability from a message", pass_context=True
)
async def extract(ctx):
    # Get the id of the message in reply
    message_id = ctx.message.reference.message_id

    message = await ctx.fetch_message(message_id)
    author_name = message.author.name

    extracted = extract_availability(message.content).strip()

    if extracted.startswith("[ERROR]"):
        await ctx.send("Pas assez d'info pour extraire les disponibilités")
        return
    else:
        pass
    dico = {}
    for line in extracted.splitlines():
        if line:
            day, availability = line.split(" : ")
            dico[day] = availability

    output_embed = discord.Embed(
        title=f"📅 Disponibilités de {author_name}",
        color=0x00FF00,
    )
    output_embed.set_footer(
        text=f"{random.choice(cringe_emojis)}",
        icon_url="https://cdn.discordapp.com/attachments/800044073158574093/1095057993961312316/pp.png",
    )

    for day, availability in dico.items():
        string = f"{day} : {availability}"
        output_embed.add_field(name="", value=string, inline=False)

    await ctx.send(embed=output_embed)


@bot.slash_command(name="test")
async def test(ctx):
    embed = discord.Embed(
        title="Disponibilités de Test",
        color=0x00FF00,
    )

    string = "Lundi : ✅"
    embed.add_field(name="", value=string, inline=False)

    string = "Mardi : ❌"
    embed.add_field(name="", value=string, inline=False)

    embed.set_footer(
        text=f"{random.choice(cringe_emojis)}",
        icon_url="https://cdn.discordapp.com/attachments/800044073158574093/1095057993961312316/pp.png",
    )

    await ctx.send(embed=embed)

    return


@bot.slash_command(
    name="extract", help="Extract availability from a message", pass_context=True
)
async def extract(ctx, message_id):
    message_id = message_id

    message = await ctx.fetch_message(message_id)
    author_name = message.author.name

    extracted = extract_availability(message.content).strip()

    if extracted.startswith("[ERROR]"):
        await ctx.send("Pas assez d'info pour extraire les disponibilités")
        return
    else:
        print("This is txt : ", extracted)
    dico = {}
    for line in extracted.splitlines():
        if line:
            day, availability = line.split(" : ")
            dico[day] = availability

    output_embed = discord.Embed(
        title=f"📅 Disponibilités de {author_name}",
        color=0x00FF00,
    )
    output_embed.set_footer(
        text=f"{random.choice(cringe_emojis)}",
        icon_url="https://cdn.discordapp.com/attachments/800044073158574093/1095057993961312316/pp.png",
    )

    for day, availability in dico.items():
        string = f"{day} : {availability}"
        output_embed.add_field(name="", value=string, inline=False)

    await ctx.respond(embed=output_embed)


@bot.slash_command(name="add_player", help="Add a player to the team")
async def add_player(ctx, player_name):
    add_player_to_team(player_name)
    await ctx.respond(f"Added {player_name} to the team")


@bot.slash_command(name="show", help="Show graph of team progress")
async def show(ctx):
    dl_graph_and_add_point("players.txt", "elo.txt")
    # send image
    await ctx.respond(file=discord.File("mychart.png"))


if __name__ == "__main__":
    bot.run(token)
