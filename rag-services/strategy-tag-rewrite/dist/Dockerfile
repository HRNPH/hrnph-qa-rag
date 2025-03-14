# syntax=docker/dockerfile:1
FROM docker.io/continuumio/miniconda3:latest

WORKDIR /


# gcc is for build psutil in MacOS
RUN apt-get update && apt-get install -y runit gcc

COPY ./flow/pyproject.toml /flow/pyproject.toml

# create conda environment
RUN conda create -n promptflow-serve python=3.11.8 pip=23.0.1 -q -y && \
    conda run -n promptflow-serve \
    pip install promptflow==1.17.2 \
    promptflow-tools && \
    conda run -n promptflow-serve pip install keyrings.alt && \
    conda run -n promptflow-serve pip install gunicorn==22.0.0 && \
    conda run -n promptflow-serve pip install 'uvicorn>=0.27.0,<1.0.0' && \
    conda run -n promptflow-serve pip cache purge && \
    conda run -n promptflow-serve pip install -e /flow && \
    conda clean -a -y

COPY ./flow /flow


EXPOSE 8080

COPY ./connections /connections

# reset runsvdir
RUN rm -rf /var/runit
COPY ./runit /var/runit
# grant permission
RUN chmod -R +x /var/runit

COPY ./start.sh /
CMD ["bash", "./start.sh"]
