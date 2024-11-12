# IMAGE
FROM python:3.10

# WORKPATH
WORKDIR /app

# INSTALANDO DEPENDENCIAS
COPY requirements.txt /app/
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt


# EXPONE PUERTO PARA DJANGO
EXPOSE 8000

# CONTAINER INIT
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
