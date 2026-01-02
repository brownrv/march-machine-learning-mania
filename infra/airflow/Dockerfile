FROM apache/airflow:2.10.3

# Copy your project into the image
WORKDIR /opt/airflow/project
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# Install into Airflow's virtualenv as the airflow user
USER airflow
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Install uv and then your package (editable) into the image venv
RUN python -m pip install uv \
 && uv pip install -e .
