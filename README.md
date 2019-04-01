# healthdata_influx
Imports Apple Health Data into InfluxDB.

![Grafana Screenshot](https://www.tannr.com/wp-content/uploads/2017/03/grafana.png "Grafana Screenshot")
Visualizing InfluxDB using [Grafana](https://grafana.com/).

## How to export iOS Health Data
1. Go to the Health App
2. Tap the profile image at the top right
3. Tap "Export Health Data"
4. Save the `export.zip` file and extract its XML contents (`export.xml`) somewhere accessible by this script.

## Running as a complete service with Docker Compose (bonus Grafana Graphs!)

This is the easiest way to get up and running quickly. This will spin up the importer, an InfluxDB database, and Grafana with a default dashboard ready to go.

#### Requirements:

* [Docker](https://www.docker.com/) with [Docker Compose](https://docs.docker.com/compose/)

#### Installation:

* Create a `data` directory at the project root and add the `export.xml` inside it

#### Building:

`docker-compose build`

#### Running:

1. `docker-compose up` (add `-d` to run in daemon mode)
2. Access Grafana in your web browser: [http://localhost:3000](http://localhost:3000)

Username: `admin` Password: `admin`

#### Refreshing data:

1. Replace `data/export.xml` with a new version
2. `docker-compose run importer`

## Running as a Python module or stand-alone script.

#### Requirements:
	
* [Python 3](https://www.python.org/)
* An accessible [InfluxDB](https://www.influxdata.com/) instance

#### Installation:

* `pip install -r requirements.txt`
* Rename `config_sample.yml` to `config.yml`

#### Configuration:

* Edit `config.yml` to match your InfluxDB settings (host, auth, etc.)

#### Usage:

1. Export Health Data from iOS device
2. `python3 import.py export.xml`


#### See also:
`python import.py --help`

## Running as a stand-alone Docker container

#### Requirements:

* [Docker](https://www.docker.com/)

#### Installation:

* Create a `data` directory at the repo root and add the `export.xml` inside it.
 	* (note that this can be anywhere if the volume mount point on the `docker run` command is changed)

#### Configuration:

* Edit `config.yml` to match your InfluxDB settings (host, auth, etc.)

#### Building:

`docker build . -t twstokes/healthdata_influx`

#### Running (at the repo root):

`docker run -v $PWD/data:/data:ro -v $PWD/config.yml:/app/config.yml:ro twstokes/healthdata_influx`

## Todo / Notes:
* Does not support "Mindful Sessions"
