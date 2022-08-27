#!/bin/bash
echo "Starting up script..."
echo "Check Connection to MariaDB..."

DATABASE_PASSWORD=$(cat "$DATABASE_PASSWORD_FILE")
while :
do
  db_available=$(mariadb -h mariadb -u "$DATABASE_USER" --password="$DATABASE_PASSWORD" &> /dev/null && echo $?)
  if [ "$db_available" == 0 ]; then
    echo "MariaDB is reachable"
    break
  fi
  sleep 5
done

export DATABASE_URL=mysql+pymysql://$DATABASE_USER:$DATABASE_PASSWORD@mariadb/$DATABASE

echo "Check if MariaDB has to be initialized..."
already_initialized=$(flask db show &> /dev/null && echo $?)
if [ "$already_initialized" != 0 ]; then
  echo "MariaDB has to be initialized..."
  flask db init
  flask db migrate -m "create tables"
  flask db upgrade
  echo "MariaDB initialized!"
else
  echo "MariaDB is already initialized"
fi

echo "Starting up FLASK web application"
flask run -h 0.0.0.0
