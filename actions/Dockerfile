FROM python:3.9-slim

WORKDIR rasa-actions/
COPY ../requirements.txt /rasa-actions/

RUN pip install --upgrade pip==24.0
RUN pip install rasa==3.6.18
RUN pip install scikit-learn==1.1.3
RUN pip install scipy==1.12.0
RUN pip install googlemaps==4.10.0
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir sentence-transformers

COPY ../actions /rasa-actions/actions
COPY ../data /rasa-actions/data
COPY ../Diagnose /rasa-actions/Diagnose
COPY ../googlemaps_api /rasa-actions/googlemaps_api
COPY ../Info /rasa-actions/Info
COPY ../models /rasa-actions/models
COPY ../SentenceTransformers /rasa-actions/SentenceTransformers
COPY ../symcat_small_data /rasa-actions/symcat_small_data
COPY ../config.yml /rasa-actions/
COPY ../credentials.yml /rasa-actions/
COPY ../domain.yml /rasa-actions/
COPY ../endpoints.yml /rasa-actions/

CMD ["rasa", "run", "actions"]