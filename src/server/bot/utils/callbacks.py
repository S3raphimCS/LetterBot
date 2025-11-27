import enum


class Callback(enum.Enum):
    """Перечисление колбеков."""

    SOCIALS = 'socials'
    RETURN_MENU = 'menu'
    QUESTS = 'quests'

    QUEST_START = 'quest_start'
    QUEST_START_ID = 'quest_start {id}'
    POINT_DECLINE_1 = 'point_decline_1'
    POINT_DECLINE_1_ID = 'point_decline_1 {id}'
    POINT_DECLINE_2 = 'point_decline_2'
    POINT_DECLINE_2_ID = 'point_decline_2 {id}'
    POINT_DECLINE_3 = 'point_decline_3'
    POINT_DECLINE_3_ID = 'point_decline_3 {id}'
    POINT_GPT = 'point_gpt'
    POINT_GPT_ID = 'point_gpt {id}'
    POINT_GPT_ANSWER = 'point_gpt_answer'

    TASK_START = 'task_start'
    TASK_START_ID = 'task_start {id}'
    TASK_COMPLETE = 'task_complete'

    PAY_QUEST = 'pay_quest'
    PAY_QUEST_ID = 'pay_quest {id}'

    QUIZ = 'quiz'
    QUIZ_ITEM = 'quiz {id} {is_right}'

    PROMPT = 'prompt'
    PROMPT_ID = 'prompt {id}'
