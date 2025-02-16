from src import bot
import asyncio
import nest_asyncio

if __name__ == "__main__":
	nest_asyncio.apply()
	asyncio.run(bot.main())
