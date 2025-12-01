import os
import io
import math
import random
import asyncio

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def generate_wheel(names):
    """Génère une roue avec les pseudos et une flèche en haut."""
    size = 800
    img = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(img)

    center = size // 2
    radius = size // 2 - 60

    draw.ellipse(
        (center - radius, center - radius, center + radius, center + radius),
        fill="#dfecc2",
        outline="black",
        width=4,
    )

    if not names:
        return img

    n = len(names)
    angle_per = 360 / n
    colors = [
        "#f6e58d",
        "#ffbe76",
        "#ff7979",
        "#badc58",
        "#dff9fb",
        "#c7ecee",
        "#e056fd",
        "#7ed6df",
    ]

    start_angle = -90

    for i, name in enumerate(names):
        end_angle = start_angle + angle_per

        draw.pieslice(
            (center - radius, center - radius, center + radius, center + radius),
            start=start_angle,
            end=end_angle,
            fill=colors[i % len(colors)],
            outline="black",
        )

        mid_angle = math.radians((start_angle + end_angle) / 2)
        tx = center + (radius * 0.6) * math.cos(mid_angle)
        ty = center + (radius * 0.6) * math.sin(mid_angle)

        font = ImageFont.load_default()
        w, h = draw.textsize(name, font=font)
        draw.text((tx - w / 2, ty - h / 2), name, fill="black", font=font)

        start_angle = end_angle

    arrow_length = radius + 40
    top_y = center - arrow_length
    draw.polygon(
        [
            (center, top_y),
            (center - 30, top_y + 60),
            (center + 30, top_y + 60),
        ],
        fill="red",
    )

    return img


@bot.command(name="giveaway")
async def giveaway(ctx, seconds: int, *, prize: str):
    message = await ctx.send(
        f"🎉 **GIVEAWAY !** 🎉\n"
        f"Prix : **{prize}**\n"
        f"Réagissez avec 🎁 pour participer !\n"
        f"Fin dans {seconds} secondes."
    )

    await message.add_reaction("🎁")

    await asyncio.sleep(seconds)

    msg = await ctx.fetch_message(message.id)

    participants = []
    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎁":
            async for user in reaction.users():
                if not user.bot and user not in participants:
                    participants.append(user)

    if not participants:
        await ctx.send("❌ Aucun participant…")
        return

    winner = random.choice(participants)
    names = [u.name for u in participants]

    wheel = generate_wheel(names)
    buffer = io.BytesIO()
    wheel.save(buffer, format="PNG")
    buffer.seek(0)

    await ctx.send(
        f"🎉 **FÉLICITATIONS {winner.mention} !**\n"
        f"Tu remportes : **{prize}** 🎁",
        file=discord.File(buffer, filename="roulette.png"),
    )


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")


bot.run(TOKEN)
