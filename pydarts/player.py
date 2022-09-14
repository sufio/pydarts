from random import randint


class Player:

    NUMBER_OF_DARTS = 3

    def __init__(self, name: str = None) -> None:
        self.name: str = (
            name if name is not None else "Player{}".format(randint(0, 10))
        )
        self._score: list[int] = []

    @property
    def score(self) -> list[int]:
        return self._score

    @property
    def final_score(self) -> int:
        return sum(self._score)

    @property
    def finished(self) -> bool:
        return True if len(self._score) >= self.NUMBER_OF_DARTS else False

    @score.setter
    def score(self, value) -> None:
        if self.finished:
            return

        self._score.append(value)

    def __str__(self) -> str:
        return """name: {}
        dart_score: {}
        final_score: {}
        done: {}
        """.format(
            self.name, self._score, sum(self._score), self.finished
        )
