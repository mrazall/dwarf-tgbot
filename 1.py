import pymorphy2

def get_gender(word):
    morph = pymorphy2.MorphAnalyzer()
    parsed_word = morph.parse(word)[0]
    return parsed_word.tag.gender

word = "стол"
gender = get_gender(word)
print(gender)