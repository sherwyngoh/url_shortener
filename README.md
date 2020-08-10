
# URL Shortener
Notes on thought process in notes.txt
### Stack:
- Python 3.8.5 
- Flask 1.1.2
-  Redis 6.0.6
- Docker version 19.03.12
- docker-compose version 1.25.0

##  Up and running:

Make sure you have docker up and running.
```
docker-compose up
```

## debugging

If you want to use python [pdb](https://docs.python.org/3/library/pdb.html)
### docker side
```
docker-compose up -d
docker ps -a # to get the id of the container
docker attach <container_id>
```

#### python code
```
import pdb
pdb.set_trace()
```

#### To get a python3 shell to work with
```
docker-compose run web python3
```

## Updating requirements

1. Update `requirements.txt`
 2. run `docker-compose up --build`

# Endpoints:
```
[POST] /shorten
Input: 
  {"url": "http://the_long_url.com/"}
Output:
  data:
    {"url": "http://test.com/the_short_url", "expires_in": "1 week"}
  status code:
    201 - will always create a new short url

[POST] /lengthen
Input:
  {"url": "http://test.com/the_short_url"}
Output:
  data: 
    {"url": "http://the_long_url.com/", "expires_in": "1 week"}
  status code:
    200 if found, else 404
```

# To test the endpoints

`curl -X POST --header "Content-Type: application/json" --header "Accept: application/json" -d '{"url": "http://someurl.com"}' "http://localhost:5000/create_short_url"`

replace "6fad2f" with the appropriate short url id you receive

`curl -X POST --header "Content-Type: application/json" --header "Accept: application/json" -d '{"url": "http://example.com/6fad2f"}' "http://localhost:5000/get_long_url"`


