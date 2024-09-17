import spacy

nlp_ner = spacy.load("en_CustomNer")


def get_labels(sentence):
    print(f'NER: {sentence}')
    diseases = nlp_ner(sentence)
    found = []
    for entity in diseases.ents:
        print(entity, entity.label_)
        found.append(entity.text)
    return found


if __name__ == "__main__":
    f = get_labels("i have also had flatulence this morning")
    print(f)