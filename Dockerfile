FROM python:3.9-slim

WORKDIR rasa-be/
COPY requirements.txt /rasa-be/

RUN pip install --upgrade pip==24.0
RUN pip install rasa==3.6.18
RUN pip install spacy==3.7.4
RUN pip install scikit-learn==1.1.3
RUN pip install scipy==1.12.0
RUN pip install googlemaps==4.10.0
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir sentence-transformers

COPY actions /rasa-be/actions
COPY data /rasa-be/data
COPY Diagnose /rasa-be/Diagnose
COPY googlemaps_api /rasa-be/googlemaps_api
COPY Info /rasa-be/Info
COPY models /rasa-be/models
COPY output_large/model-best /rasa-be/output_large/model-best
COPY SentenceTransformers /rasa-be/SentenceTransformers
COPY symcat_small_data /rasa-be/symcat_small_data
COPY config.yml /rasa-be/
COPY credentials.yml /rasa-be/
COPY domain.yml /rasa-be/
COPY endpoints.yml /rasa-be/
COPY rasa_conversations.db /rasa-be/

RUN mkdir -p /rasa-be/packages
# Install spaCy package and custom NER model
RUN python -m spacy package output_large/model-best packages --name CustomNer --version 0.0.1 --force
RUN python -m pip install packages/en_CustomNer-0.0.1/
RUN rm -rf packages

CMD ["rasa", "run", "-m", "models", "--endpoints", "endpoints.yml", "--enable-api", "--cors", "*", "--debug"]