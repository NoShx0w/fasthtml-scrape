
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from fasthtml.common import *
from collections import namedtuple

from apps.nav.nav import app as nav
from apps.h2f.h2f import app as h2f
from apps.scrape.scrape import app as scrape

apps = FastAPI()

@apps.get("/", response_class=RedirectResponse)
def homepage(request: Request) -> RedirectResponse:
    return RedirectResponse("/nav/", status_code=301)


#@apps.post("/")
#async def post(request: Request): return {"message": "", "root_path": request.scope.get("root_path")}

nav = nav
h2f = h2f
scrape = scrape

apps.mount("/nav", nav)
apps.mount("/h2f", h2f)
apps.mount("/scrape", scrape)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:apps", host="0.0.0.0", port=8000, reload=True, access_log=True)
