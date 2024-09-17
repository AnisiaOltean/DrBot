from joblib import load
from typing import List, Tuple
import numpy as np

with open('/RasaNew/symcat_small_data/logRegSimpleBun.joblib', 'rb') as f:
    logReg = load(f)

with open('/RasaNew/symcat_small_data/sympoms_em.joblib', 'rb') as f:
    symptoms_embeddings = load(f)

with open('/RasaNew/symcat_small_data/disease_symptoms.joblib', 'rb') as f:
    d_sym = load(f)

with open('/RasaNew/symcat_small_data/new_symptom_index.joblib', 'rb') as f:
    symptom_index = load(f)

def get_one_hot(symptoms_list):
    symptoms = [s.strip() for s in symptoms_list]
    #print(symptoms)
    # creating input data for the models
    embedding = [0] * len(symptom_index)
    for symptom in symptoms:
        index = symptom_index[symptom]
        embedding[index] = 1
    return np.array(embedding)


def predict_disease(symptoms_list):
    encoded = get_one_hot(symptoms_list)
    print(encoded)
    encoded = encoded.reshape(1, -1)
    prediction = logReg.predict(encoded)
    return prediction


# def get_top2(symptoms_list):
#     encoded = get_one_hot(symptoms_list)
#     print(encoded.shape)
#     encoded = encoded.reshape(1, -1)
#     res = logReg.predict_proba(encoded)
#     top2_indices = np.argsort(res, axis=-1)[:, -2:]
#     predicted_labels = logReg.classes_[top2_indices[0][0]], logReg.classes_[top2_indices[0][1]]  # second_max and max!!!
#     probs = res[0, top2_indices[0][0]], res[0, top2_indices[0][1]]
#     return predicted_labels[0], predicted_labels[1], probs[0], probs[1]


def get_predictions(symptoms_list):
    embedded_sample = get_one_hot(symptoms_list)
    embedded_sample = embedded_sample.reshape(1, -1)
    prediction = logReg.predict_proba(embedded_sample)
    return prediction


def get_first_two(probs):
    sorted_indices = np.argsort(probs[0])
    i1 = sorted_indices[-2:][0]
    i2 = sorted_indices[-2:][1]
    return probs[0][i1], probs[0][i2], logReg.classes_[i1], logReg.classes_[i2]


def get_diagnosis(symptoms_list) -> List[Tuple[float, str]]:
    probs = get_predictions(symptoms_list)
    prob_1, prob_2, disease1, disease2 = get_first_two(probs)

    return [(prob_1, disease1), (prob_2, disease2)]


def get_related_symptoms(current_symptoms, prob_1, prob_2, disease1, disease2):
    list_1 = d_sym[disease1]
    list_1 = [e for e in list_1 if e.lower() not in current_symptoms]
    list_2 = d_sym[disease2]
    list_2 = [e for e in list_2 if e.lower() not in current_symptoms]
    if prob_2 - prob_1 < 0.1:
        just_1 = set(list_1) - set(list_2)
        just_2 = set(list_2) - set(list_1)
    else:
        just_1 = set()
        just_2 = set(list_2) - set(list_1)

    total = set(just_1 | just_2)
    return total
