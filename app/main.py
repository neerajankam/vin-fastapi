from fastapi import FastAPI, HTTPException, Request


from routers import lookup, remove, export


app = FastAPI()
app.include_router(lookup.router)
app.include_router(remove.router)
app.include_router(export.router)
