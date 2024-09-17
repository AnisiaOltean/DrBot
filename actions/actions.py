# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset, Restarted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

# from Diagnose.Diagnose import get_diagnosis, get_related_symptoms
from Diagnose.DiagnoseNew import get_diagnosis, get_related_for_current_symptoms
from Info.Info import get_explanation_new, get_treatments
from googlemaps_api.location import find_nearest_hospitals, reverse_geocode, find_nearest_hospitals_current_location
# from BioEM.get_similar_symptoms import get_top
from SentenceTransformers.SimilarSymptoms import get_top


class ActionGiveDiagnosis(Action):
    def name(self) -> Text:
        return "action_give_diagnosis"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sender = tracker.sender_id
        print(f'Current sender: {sender}')
        entire_message = tracker.latest_message
        print(f'Entire message: {entire_message}')

        metadata = tracker.latest_message['metadata']  # retrieve metadata from FE
        print(f'Metadata: {metadata}, {type(metadata)}')
        current_symptoms = tracker.get_slot("symptoms") or []
        print(f'Current: {current_symptoms}')

        entities = tracker.latest_message['entities']
        print(f'Entities: {entities}')

        new_symptoms = [entity['value'] for entity in entities if entity['entity'] == 'SYMPTOM']
        print(f'Found symptoms: {new_symptoms}')

        to_diagnose = current_symptoms
        to_diagnose += new_symptoms

        print(f'Doing diagnosis on: {to_diagnose}')

        current_results = get_diagnosis(to_diagnose)
        dispatcher.utter_message(json_message={"user_type": "bot", "text": f"You are probably suffering from: \nDisease: {current_results[0][1]} with probability: {current_results[0][0]} \n Disease: {current_results[1][1]} with probability: {current_results[1][0]}"})
        return [SlotSet("symptoms", to_diagnose)]


class ActionCollectSymptoms(Action):

    def name(self) -> Text:
        return "action_collect_symptoms"  # name used in domain.yml and stories.yml

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        metadata = tracker.latest_message['metadata']  # retrieve metadata from FE
        print(f'Metadata: {metadata}, {type(metadata)}')

        current_symptoms = tracker.get_slot("symptoms") or []
        print(f'Current: {current_symptoms}')

        entities = tracker.latest_message['entities']
        print(f'Entities: {entities}')

        new_symptoms = [entity['value'] for entity in entities if entity['entity'] == 'SYMPTOM']
        print(f'Found symptoms: {new_symptoms}')

        check_msg = ""
        to_check = get_top(new_symptoms)
        print(f'To check: {to_check}')
        new_symptoms_good = []
        for s, possible_s in to_check.items():
            if len(possible_s) == 1:
                new_symptoms_good.append(possible_s[0])
            else:
                # i have to ask user to clarify symptoms
                clarify = ', '.join(possible_s[:-1])
                clarify += ' or '+possible_s[-1]
                check_msg += f"What type is your {s}? {clarify} \n"
                new_symptoms_good.append(s)

        to_diagnose = new_symptoms_good

        for ss in current_symptoms:
            ok = 0
            for el in to_diagnose:
                if ss in el:
                    ok = 1

            if ok == 0:
                to_diagnose.append(ss)

        print(f'Doing diagnosis on: {to_diagnose}')

        diagnosis = ""
        if check_msg == "":
            # current_results = get_diagnosis(to_diagnose)
            # to_ask = get_related_symptoms(to_diagnose, current_results[0][0], current_results[1][0], current_results[0][1],
            #                           current_results[1][1])
            #
            # print(f'{to_ask}')
            #
            # if len(to_diagnose) >= 6 or len(to_ask) == 0:
            #     dispatcher.utter_message(json_message={"user_type": "bot", "text": f"You are probably suffering from: \nDisease: {current_results[0][1]} with probability: {current_results[0][0]} \n Disease: {current_results[1][1]} with probability: {current_results[1][0]}"})
            # #dispatcher.utter_message(text=f"Disease: {current_results[1][1]} with probability: {current_results[1][0]}")
            # else:
            #     dispatcher.utter_message(json_message={"user_type": "bot", "text": f"Do you also have {to_ask}?"})

            current_results = get_diagnosis(to_diagnose)
            print(current_results)
            to_ask = get_related_for_current_symptoms(to_diagnose)
            print(f'{to_ask}')

            prob1, disease1 = current_results[0]
            prob2, disease2 = current_results[1]

            diagnosis = disease2
            if prob2 - prob1 > 0.4 or prob2 > 0.6 or len(to_ask) == 0 or len(to_diagnose) >= 8:
                dispatcher.utter_message(json_message={"user_type": "bot", "text": f"You are probably suffering from: \nDisease: {disease1} with probability: {prob1} \n Disease: {disease2} with probability: {prob2}"})
            else:
                max_l = min(3, len(to_ask))
                next_s = to_ask[:max_l]
                next_s = [el[0] for el in next_s]
                print(next_s)
                final = ', '.join(next_s[:-1])
                final += ' or ' + next_s[-1]
                print(final)
                dispatcher.utter_message(json_message={"user_type": "bot", "text": f"Do you also have {final}?"})
        else:
            dispatcher.utter_message(text=check_msg)

        return [SlotSet("symptoms", to_diagnose), SlotSet("diagnosis", diagnosis.lower())]


class ActionFindHospitals(Action):
    def name(self) -> Text:
        return "action_find_hospitals"  # name used in domain.yml and stories.yml

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        print(f'Entities: {entities}')
        user_street = [e for e in entities if e['entity'] == 'STREET'][0]
        user_city = [e for e in entities if e['entity'] == 'TOWN'][0]
        user_location = f"{user_street}, {user_city}"

        print(f'Current: {user_location}')

        hospitals, loc = find_nearest_hospitals(user_location)

        dispatcher.utter_message(json_message={"user_type": "bot", "text": f"The closest hospital i found is {hospitals[0]['name']}.\n You can see other facilities by clicking the button below", "found_hospitals": hospitals, "current_location": {"lat": loc[0], "lng": loc[1]}})
        return [SlotSet("user_location", user_location)]


class ActionFindHospitalsCurrentLocation(Action):
    def name(self) -> Text:
        return "action_find_hospitals_current_location"  # name used in domain.yml and stories.yml

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        metadata = tracker.latest_message['metadata']  # retrieve metadata from FE
        print(f'Metadata: {metadata}, {type(metadata)}')
        if metadata == {}:
            dispatcher.utter_message("You seem to have your location disabled. Make sure you have geolocation enabled and I can try again")
            return []

        latitude = metadata['lat']
        longitude = metadata['long']
        print(f"Latitude: {latitude}, longitude: {longitude}")

        user_location = reverse_geocode(latitude, longitude)
        hospitals, loc = find_nearest_hospitals_current_location(latitude, longitude)

        print(f'Current: {user_location}')

        dispatcher.utter_message(json_message={"user_type": "bot", "text": f"Your current location is: {user_location}. The closest hospital i found is {hospitals[0]['name']}.\n You can see other facilities by clicking the button below. Please note that that the detected location might not be 100% accurate.", "found_hospitals": hospitals, "current_location": {"lat": latitude, "lng": longitude}})
        return [SlotSet("user_location", user_location)]


class ActionGiveExplanation(Action):

    def name(self) -> Text:
        return "action_give_explanation"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        print(entities)

        disease = ""
        if len(entities) > 0:
            disease = [entity['value'] for entity in entities if entity['entity'] == 'DISEASE'][0]

        current_diagnosis = tracker.get_slot("diagnosis") or ""
        print(f'Current: {current_diagnosis}')

        print(f'Found disease: {disease} or diagnosis: {current_diagnosis}')
        description = get_explanation_new(disease, current_diagnosis)
        dispatcher.utter_message(json_message={"user_type": "bot", "text": description})
        return []


class ActionGiveTreatments(Action):

    def name(self) -> Text:
        return "action_give_treatments"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        print(entities)

        disease = ""
        if len(entities) > 0:
            disease = [entity['value'] for entity in entities if entity['entity'] == 'DISEASE'][0]
        print(f'Found disease: {disease}')

        current_diagnosis = tracker.get_slot("diagnosis") or ""
        print(f'Current: {current_diagnosis}')

        print(f'Found disease: {disease} or diagnosis: {current_diagnosis}')
        general_treatments, extra_advice, see_doctor = get_treatments(disease, current_diagnosis)
        dispatcher.utter_message(json_message={"treatments": general_treatments, "advice": extra_advice, "see_doctor": see_doctor})

        return []


class ActionCleanUp(Action):
    def name(self) -> Text:
        return "action_cleanup"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        return [AllSlotsReset(), Restarted()]
