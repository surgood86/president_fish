
Установить докер.


sudo apt-get install 
python3-pip pip3 install 
pipenv pip3 install docker-compose
( pipenv install docker-compose )


pipenv install --system 
docker-compose up --build

после успешной установки остановить процесс и наберать docker-compose up -d --build после 
наберать docker-compose exec web python manage.py migrate
все данные будут в datadump.json оттуда все данные мигрируем в бд  
т.к. все запускается внутри docker то придется ко всем командам прибавлять docker-compose exec web, в начале вынужденная мера