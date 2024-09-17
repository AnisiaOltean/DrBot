from joblib import load
from typing import List, Tuple
import numpy as np

docker_path1 = '/rasa-be/symcat_small_data'
docker_path2 = '/rasa-actions/symcat_small_data'
local_path = 'C:/Cursuri (incomplet)/Anul III/Licenta/RasaNew/symcat_small_data'

current_dir = local_path

with open(f'{current_dir}/logRegSimpleBun.joblib', 'rb') as f:
    logReg = load(f)

with open(f'{current_dir}/new_symptom_index.joblib', 'rb') as f:
    symptom_index = load(f)

with open(f'{current_dir}/disease_symptoms.joblib', 'rb') as f:
    disease_symptoms = load(f)


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


def get_top2(symptoms_list):
    encoded = get_one_hot(symptoms_list)
    print(encoded.shape)
    encoded = encoded.reshape(1, -1)
    res = logReg.predict_proba(encoded)
    top2_indices = np.argsort(res, axis=-1)[:, -2:]
    predicted_labels = logReg.classes_[top2_indices[0][0]], logReg.classes_[top2_indices[0][1]]  # second_max and max!!!
    probs = res[0, top2_indices[0][0]], res[0, top2_indices[0][1]]
    return predicted_labels[0], predicted_labels[1], probs[0], probs[1]


def get_related_for_current_symptoms(current_symptoms):
    related = {}
    for k, v in disease_symptoms.items():
        # verific daca am toate simptomele din current_symptoms
        check = all(item in v for item in current_symptoms)
        if check:
            # le filtrez sa nu le iau pe astea din current symptoms
            other_sympts = [a for a in v if a not in current_symptoms]
            for o in other_sympts:
                if o in related.keys():
                    related[o] = related[o] + 1
                else:
                    related[o] = 1
    return sorted(related.items(), key=lambda x: x[1], reverse=True)


def get_predictions(symptoms_list):
    embedded_sample = get_one_hot(symptoms_list)
    embedded_sample = embedded_sample.reshape(1, -1)
    print(embedded_sample.shape)
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


if __name__ == "__main__":
    symptoms_list = ['fever', 'cough', 'sore throat']
    related = get_related_for_current_symptoms(symptoms_list)
    max_l = min(3, len(related))
    next_s = related[:max_l]
    next_s = [el[0] for el in next_s]
    print(next_s)
    final = ', '.join(next_s[:-1])
    final += ' or '+ next_s[-1]
    print(final)
    print(related)
    probs = get_predictions(symptoms_list)
    first2 = get_first_two(probs)
    print(first2)

    d = get_diagnosis(["cough", "headache", "sore throat", "fever", "nasal congestion", "coryza", "vomiting", "ear pain", "wheezing", "flu-like syndrome"])
    print(d)
