# Hypofin

An investment planning app for Poles.

## Development

Run backend:

```sh
cd backend
poetry install  # see python-poetry.org
poetry shell
uvicorn hypofin:server --reload
```

Run frontend:

```sh
cd frontend
npm install
npm run dev
```
