# In a real application, this module would contain functions
# that interact with an AI model (e.g., OpenAI's GPT).
# For this prototype, we'll use dummy data.


def get_word_usages(word):
    """
    Returns a dictionary of usages for a given word.
    Keys are the usage types (e.g., "Basic Usage"), and values are the descriptions.
    """
    if word.lower() == "have":
        return {
            "Basic Usage": "To possess, own, or hold something.",
            "Expanded Usage": "Refers not just to objects, but also to emotions, thoughts, activities, and events. It's about 'possessing' an experience.",
            "Grammatical Usage": "Used as an auxiliary verb to form perfect tenses (e.g., have seen, have done).",
            "Idiomatic Expressions": "Used in various common phrases and idioms.",
        }
    else:
        return {"Error": "Word not found."}


def get_example_sentences(usage):
    """
    Returns a list of Korean sentences for the user to translate,
    based on the selected usage.
    """
    sentences = {
        "Basic Usage": [
            "나는 아름다운 집을 가지고 있다.",
            "그녀는 두 명의 자녀가 있다.",
            "우리에게는 시간이 거의 없다.",
        ],
        "Expanded Usage": [
            "좋은 생각 있어요.",
            "오늘 우리는 재미있는 시간을 보냈다.",
            "그는 어제 이상한 꿈을 꿨다.",
        ],
        "Grammatical Usage": [
            "나는 그 영화를 전에 본 적이 있다.",
            "그녀는 숙제를 이미 끝냈다.",
            "그들이 도착했을 때, 우리는 저녁을 다 먹은 상태였다.",
        ],
        "Idiomatic Expressions": [
            "그녀는 파티에서 즐거운 시간을 보냈다. (have a good time)",
            "잠깐 쉬자. (have a break)",
            "나는 그 문제에 대해 의심이 든다. (have doubts)",
        ],
    }
    return sentences.get(usage, [])


def get_feedback(user_sentence, original_korean_sentence):
    """
    Provides feedback on the user's English translation.
    In a real app, this would involve an AI call.
    For now, it returns a generic success message.
    """
    # This is a placeholder. A real implementation would compare the user's sentence
    # with a model translation or use an AI to evaluate the quality.
    return "Great job! Your translation is excellent."
