#!/bin/bash
echo "Starting script..."
echo "Check Connection to MariaDB..."

# read password for database user from file
DATABASE_PASSWORD=$(cat "$DATABASE_PASSWORD_FILE")
while :
do
  # try connecting to the database -> if successful operation, the database is reachable and ready
  db_available=$(mariadb -h mariadb -u "$DATABASE_USER" --password="$DATABASE_PASSWORD" &> /dev/null && echo $?)
  if [ "$db_available" == 0 ]; then
    echo "MariaDB is reachable"
    break
  fi
  # wait 5 seconds before next connection attempt to the database
  sleep 5
done

# set database connection url as environment variable
export DATABASE_URL=mysql+pymysql://$DATABASE_USER:$DATABASE_PASSWORD@mariadb/$DATABASE

# initialize database if needed
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

# startup flask application
echo "Starting up FLASK web application"
flask run -h 0.0.0.0
