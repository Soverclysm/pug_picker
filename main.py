from src.bot.twitch_bot import PickBot  # Import our bot
import asyncio

async def main():
    bot = PickBot()
    try:
        await bot.connect_and_run()
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    print("Starting bot...")
    asyncio.run(main())