FROM ubuntu

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    python3 \
    python3-numpy \
    python3-pip \
    python3-dev

RUN pip3 install --upgrade pip

RUN pip3 install -U setuptools

RUN pip3 install jupyter

ENV INSTALL_PATH /scheduler
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY . .

RUN pip3 install -r requirements.txt
#RUN pip3 install --editable .

EXPOSE 8008

# Add a notebook profile.
RUN mkdir -p -m 700 /root/.jupyter/ && \
    echo "c.NotebookApp.ip = '*'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py

#ENTRYPOINT ["tini", "--"]
CMD ["jupyter", "notebook", "--port=8008", "--no-browser", "--allow-root"]
