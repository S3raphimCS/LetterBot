import enum


class Callback(enum.Enum):
    """Перечисление колбеков."""

    FAST_MAILING = "fast_mailing"
    ADMIN = "admin"
    BROADCAST = "broadcast"
    VOICE_MAILING = "voice_mailing"
    BROADCAST_VOICE = "broadcast_voice"
