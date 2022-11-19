class KiwiType:
    ...


class Score(KiwiType):
    pass


class Scoreboard(KiwiType):
    pass


built_in_dict = {
    "score": Score,
    "scoreboard": Scoreboard
}
