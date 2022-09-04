# back_profiles

[![codecov](https://codecov.io/gh/tdp-II-grupo-5-2022-2c/back/branch/main/graph/badge.svg?token=60XKM2X9OI)](https://codecov.io/gh/tdp-II-grupo-5-2022-2c/back)
[![Linters](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/linter.yaml/badge.svg)](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/linter.yaml)
[![Tests](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/test.yaml/badge.svg)](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/test.yaml)
[![Deploy](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/deploy.yaml/badge.svg)](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/deploy.yaml)


# Link a Heroku

Prod: https://album-qatar-back.herokuapp.com/docs

Staging: https://album-qatar-back-stg.herokuapp.com/docs

### Dependencies

- Python 3.9
- Poetry

Install with:
```bash
poetry lock --no-update
poetry install
```

### Docker

Run app commands local
```
docker build -t back .
docker run -p 5000:5000 --env-file .env back
```

### Docker-compose

Local MongoDB image built in with Docker image. Use database url already set up in example .env

```bash
docker-compose build
docker-compose up
```

### Manual Deploy to Heroku

Para agregar las configuraciones manuales por primera vez

```
heroku config:set port=5000
heroku config:set version="1.0.0"
heroku config:set title="Back_Profile"
```

Deploy despues de pushear a main
```
heroku container:login
heroku container:push web -a album-qatar-back
heroku container:release web -a album-qatar-back
```

### Test

Run tests using [pytest](https://docs.pytest.org/en/6.2.x/)

``` bash
pytest tests/
```
