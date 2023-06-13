
# VIN(Vehicle Identification Number) decoder
A simple FastAPI backend to decode VINs, powered by the [vPIC API](https://vpic.nhtsa.dot.gov/api/) and backed by a SQLite cache.


## API Endpoints

#### Decode VIN and get vehicle details

```http
GET /lookup?{$vin}
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `vin` | `string` | 17 characters alphanumeric string **Required**.|

#### Delete vehicle details corresponding to VIN from cache

```http
DELETE /remove?{$vin}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `vin`      | `string` | 17 characters alphanumeric string **Required**.|

#### Export the database as a parquet file

```http
GET /export
```
Does not take any parameters


## Requirements

1) [Python3](https://www.python.org/downloads/)(preferably 3.11.3 or newer)

2) SQLite
On MacOS, it is installed by default. However, if you use a different OS, please head over to [SQLite](https://www.sqlite.org/download.html) to download your OS specific binaries.

3) [Postman](https://www.postman.com/downloads/)/ your API platform of choice to test the endpoints.




## Usage

1) Clone this repository [vin-fastapi](https://github.com/neerajankam/vin-fastapi.git) using ssh/ https/ Git CLI. Use the command below if you'd like to clone using ssh.
```
git clone git@github.com:neerajankam/vin-fastapi.git
```
2) Create a virtual environment using `venv` module of python.
```
python3 -m venv <virtual-environment-name>
```
3) Activate the virtual environment and install the requirements present in requirements.txt
```
source <virtual-environment-name>/bin/activate
pip3 install -r requirements.txt
```
4) Add the absolute path of the repository to the PYTHONPATH to ensure python can find the modules.
```
export PYTHONPATH=<absolute-path-of-vin-fastapi-directory>
```
5) Change to the app directory and launch the FastAPI app that is present in the main.py module using [uvicorn](https://www.uvicorn.org/). It is downloaded in Step 3 and you don't need to download it again.
```
cd /app
uvicorn main:app --reload
```
6) Ensure that the server is up and running by going to `http://127.0.0.1:8000/docs`. You should be able to see swagger documentation page if the server is running.

7) You can now headover to Postman/ your choice of API platform to test the endpoints.
## Directory structure

```
├── LICENSE
├── README.md
├── app (Application modules)
│   ├── config.py (App configuration)
│   ├── main.py (App instance)
│   ├── routers (Endpoint specific routers)
│   │   ├── export.py
│   │   ├── lookup.py
│   │   └── remove.py
│   ├── tests
│   │   ├── __init__.py
│   │   └── routers
│   │       ├── test_export.py
│   │       ├── test_lookup.py
│   │       └── test_remove.py
│   └── utils.py
├── caching (Caching modules)
│   ├── __init__.py
│   ├── cache_interface.py
│   └── sqlite_cache.py
├── data (Application data)
│   ├── vin_cache.parquet
│   └── vins_database.db
├── database (Database modules)
│   ├── __init__.py
│   ├── config.py
│   ├── connection.py
│   └── database_interface.py
├── log (Logging modules)
│   ├── __init__.py
│   └── logger.py
├── models (Database and applicationmodels)
│   ├── __init__.py
│   ├── database_models.py
│   └── parsing_models.py
└── requirements.txt
```
## License

[MIT](https://choosealicense.com/licenses/mit/)

