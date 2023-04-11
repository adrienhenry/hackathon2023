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