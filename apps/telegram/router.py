from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="bootstrap")


@router.message(CommandStart())
async def start(message: Message) -> None:
    """Bootstrap UI only; business use cases are added through application modules later."""
    await message.answer("Bakunity Infra")
