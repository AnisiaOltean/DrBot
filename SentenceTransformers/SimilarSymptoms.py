import numpy as np
from joblib import load
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

docker_path1 = '/rasa-be'
docker_path2 = '/rasa-actions'
local_path = 'C:/Cursuri (incomplet)/Anul III/Licenta/RasaNew'

current_dir = local_path

with open(f'{current_dir}/SentenceTransformers/new_symptom_index.joblib', 'rb') as f:
    symptoms_index = load(f)

with open(f'{current_dir}/SentenceTransformers/symptoms_em_transformers.joblib', 'rb') as f:
    symptoms_em = load(f)

model = SentenceTransformer('FremyCompany/BioLORD-2023')


def get_most_similar(w):
    em1 = model.encode(w)

    similarities = []
    for k, v in symptoms_em.items():
        em2 = v
        if norm(em1) == 0 or norm(em2) == 0:
            print(f'{w} or {k} has norm 0')
        cosine = np.dot(em1, em2)/(norm(em1)*norm(em2))
        # Calculate cosine similarity
        similarities.append((k, cosine))
    return similarities


def get_most_similar_words(w):
    print(f'word: {w}')
    simi = get_most_similar(w)
    most_similar = sorted(simi, key= lambda x: x[1], reverse=True)
    return most_similar


def get_top(words_list):
    l = {}
    for w in words_list:
        ll = []
        mm = get_most_similar_words(w)

        found = 0
        found_in = 0
        for el, proba in mm:
            if w == el:
                ll.append(el)
                found = 1
                break

            if found == 0 and w in el:
                ll.append(el)
                found_in = 1

        if found == 0 and found_in == 0:
            ll.append(mm[0][0])

        l[w] = ll
    return l


if __name__ == "__main__":
    most_simi = get_most_similar_words('painful periods')
    top1 = get_top(['painful periods', 'headaches', 'discharge from vagina', 'abdominal pain'])
    top2 = get_top(['painful menstruation', 'headache', 'vaginal discharge', 'sharp abdominal pain'])
    print(top1)
    print(top2)

    top3 = get_top(['hair loss'])
    print(top3)

    top4 = get_top(['abdominal pain'])
    print(top4)