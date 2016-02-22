__author__ = 'jason'


class Clock:
    def __init__(self):
        pass

    _clock = 0

    @classmethod
    def tick(cls):
        cls._clock += 1

    @classmethod
    def get(cls):
        return Clock._clock

    @classmethod
    def reset(cls):
        cls._clock = 0



