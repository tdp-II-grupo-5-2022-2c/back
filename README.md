# back_profiles

[![codecov](https://codecov.io/gh/tdp-II-grupo-5-2022-2c/back/branch/main/graph/badge.svg?token=CeoOvqKi2B)](https://codecov.io/gh/tdp-II-grupo-5-2022-2c/back)
[![Linters](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/linter.yaml/badge.svg)](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/linter.yaml)
[![Tests](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/test.yaml/badge.svg)](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/test.yaml)
[![Deploy](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/deploy.yaml/badge.svg)](https://github.com/tdp-II-grupo-5-2022-2c/back/actions/workflows/deploy.yaml)


### Dependencies

- Python 3.9
- Poetry

Install with:
```bash
poetry install
```

### Docker

Run app commands local
```
docker build -t back-profiles .
docker run -p 5000:5000 --env-file .env back-profiles
```

### Docker-compose

Local MongoDB image built in with Docker image. Use database url already set up in example .env

```bash
docker-compose build
docker-compose up
```

### Manual Deploy to Heroku

```
heroku config:set port=5000
heroku config:set version="1.0.0"
heroku config:set title="Back_Profile"

heroku container:push web -a spotifiuby-profiles
heroku container:release web -a spotifiuby-profiles


```

### Test

Run tests using [pytest](https://docs.pytest.org/en/6.2.x/)

``` bash
pytest tests/
```
