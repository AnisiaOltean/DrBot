import json
# import os
#
# current_path = os.getcwd()
# root_folder = os.path.dirname(current_path)

docker_path1 = '/rasa-be/symcat_small_data'
docker_path2 = '/rasa-actions/symcat_small_data'
local_path = 'C:/Cursuri (incomplet)/Anul III/Licenta/RasaNew/symcat_small_data'

current_dir = local_path

with open(f'{current_dir}/diseases_treatments.json', 'r', encoding='utf-8') as f:
    disease_treatments = json.load(f)


def get_explanation_new(disease, current_diagnosis):
    if disease not in disease_treatments.keys():
        return disease_treatments[current_diagnosis]['description']
    else:
        return disease_treatments[disease]['description']


def get_treatments(disease, current_diagnosis):
    d = disease
    if disease not in disease_treatments.keys():
        d = current_diagnosis

    treatments = disease_treatments[d]['treatments']
    extra_advice = disease_treatments[d]['treatments_list']
    see_doctor = disease_treatments[d]['see_doctor']
    return treatments, extra_advice, see_doctor


if __name__ == "__main__":
    for k, v in disease_treatments.items():
        print(k, v['description'])
    print(disease_treatments['conjuctivitis']['description'])

    get_explanation_new('conjuctivitis', 'conjuctivitis')