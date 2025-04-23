
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    postgresql \
    postgresql-contrib \
    apache2 \
    php \
    libapache2-mod-php \
    php-pgsql \
    sudo \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER webuser1 WITH SUPERUSER PASSWORD 'password';" && \
    createdb -O webuser1 webapp_db && \
    /etc/init.d/postgresql stop
    
USER root

RUN sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/14/main/postgresql.conf && \
    echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/14/main/pg_hba.conf
    
RUN rm -rf /var/www/html/*
COPY app/ /var/www/html/

COPY db_backup/db_backup.sql /tmp/    

RUN echo '#!/bin/bash\n\
service postgresql start\n\
echo "PostgreSQL started"\n\
if [ -f /tmp/db_backup.sql ]; then\n\
  echo "Restoring database from backup"\n\
  su - postgres -c "psql -U webuser1 -d webapp_db -f /tmp/db_backup.sql"\n\
fi\n\
service apache2 start\n\
echo "Apache started"\n\
# Keep container running\n\
tail -f /dev/null' > /start.sh && \
chmod +x /start.sh
    
EXPOSE 80    # Apache
EXPOSE 5432  # PostgreSQL
    
CMD ["/start.sh"]
