FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./inventory-management /inventory-management
COPY requirements.txt ./requirements.txt
RUN pip install /inventory-management
RUN pip install -r requirements.txt

COPY ./app /app