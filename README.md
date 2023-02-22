# FinalProjectAuctionCompany.
install python 3.9 (packaging already entered).
create a virtual environment.
pip install -r requirements.txt ;
https://redis.io/docs/getting-started/installation/;
python manage.py crontab add ;
python manage.py crontab show ;  
python manage.py runserver ;
redis-cli connected to your local host. If you want you can use  a key (key*) or not; (https://github.com/redis/redis-om-python);
(optional)lrange key 0 -1 each key you can run to return every interaction with this specific auction;
(optional)you can create a pipeline yourself where to enter the auction data;
open homepage and create auction;
Each winner receives an auction winning notification with all the references also in Json format;
in the winning link you will find a button that will take you to Goerli-Etherscan where you can see the notarized winning data and verify the transaction on the blockchain;
