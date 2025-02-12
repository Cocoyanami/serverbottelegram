FROM ubuntu:latest

# Instalar dependencias necesarias
RUN apt update && apt install -y cron rsync

# Copiar el script de backup al contenedor
COPY backup.sh /usr/local/bin/backup.sh
RUN chmod +x /usr/local/bin/backup.sh

# Configurar el cron para ejecutar el backup cada hora
RUN echo "0 * * * * root /usr/local/bin/backup.sh" >> /etc/crontab

CMD ["cron", "-f"]
