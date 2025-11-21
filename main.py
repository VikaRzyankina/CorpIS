from fastapi import FastAPI
from routers import (
    positions, topics, employees, teams, clients,
    contracts, projects, services, payments
)

app = FastAPI(title="Web Studio API", version="1.0.0")

# Подключаем все роутеры
app.include_router(positions.router)
app.include_router(topics.router)
app.include_router(employees.router)
app.include_router(teams.router)
app.include_router(clients.router)
app.include_router(contracts.router)
app.include_router(projects.router)
app.include_router(services.router)
app.include_router(payments.router)


@app.get("/")
def read_root():
    return {"message": "Web Studio API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
