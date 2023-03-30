FROM python:3.9.6 as setup_venv
ENV POETRY_VERSION="1.2.0"
ENV POETRY_HOME="/opt/.poetry"
WORKDIR /opt
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV export PATH=".poetry/bin:$PATH"
RUN poetry config virtualenvs.in-project true
COPY . /opt/hackathon
WORKDIR /opt/hackathon
RUN poetry install --no-dev
ENTRYPOINT ["./start_streamlit"]
# # Start the server
# FROM 3.9-slim-buster as running_image
# ENV STUDY_DIRECTORY=/opt/blackcube_studies
# WORKDIR /opt
# RUN mkdir $STUDY_DIRECTORY
# VOLUME $STUDY_DIRECTORY
# ENV VIRTUAL_ENV="/opt/.venv"
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# COPY --from=setup_venv $VIRTUAL_ENV $VIRTUAL_ENV
# ENV BLACKCUBE_PORT=5000
# COPY --from=setup_venv /opt/blackcube blackcube
# COPY --from=setup_venv /opt/pyproject.toml pyproject.toml
# COPY start_blackcube_server start_blackcube_server
# RUN chmod +x start_blackcube_server
