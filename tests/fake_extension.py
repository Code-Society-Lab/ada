def setup(bot: dict[str, list[str]]) -> None:
    bot.setdefault("loaded", []).append("tests.fake_extension")
