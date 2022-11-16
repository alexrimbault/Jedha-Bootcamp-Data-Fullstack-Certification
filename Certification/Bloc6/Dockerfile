FROM python:3.7.13

WORKDIR /home/app

# copy requirements.txt in the container and install dependencies with pip & update
COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt
RUN apt-get update && apt-get install -y libfluidsynth2 fluid-soundfont-gm build-essential libasound2-dev libjack-dev fluidsynth

COPY midi_samples midi_samples
COPY model.py model.py
COPY app.py app.py
COPY MuseScore_General.sf2 MuseScore_General.sf2

CMD streamlit run --server.port $PORT app.py
