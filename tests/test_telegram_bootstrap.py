from aiogram import Dispatcher

from apps.telegram.main import build_dispatcher


def test_build_dispatcher_without_runtime_token() -> None:
    dispatcher = build_dispatcher()

    assert isinstance(dispatcher, Dispatcher)
