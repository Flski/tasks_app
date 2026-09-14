from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import uvicorn
from db_config import engine, db_session
from db_tables import DB
from config import templates_path, secret_key
from db_work import DBWork


app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key)

templates = Jinja2Templates(directory=templates_path)

DB.metadata.create_all(bind=engine)

def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()

def access(request):
    if "login" not in request.session:
        return False
    return True

def access1(request, login):
    if request.session["login"] != login:
        return False
    return True

@app.get("/")
def main_get(request: Request):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

@app.get("/registration", response_class=HTMLResponse)
def registration_get(request: Request):
    if access(request):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    if request.session.get("error_l", False) != False:
        request.session["error_l"] = False
    return templates.TemplateResponse(name="registration.html", request=request, context={"error_r":
    request.session.get("error_r", False)})

@app.post("/registration", response_class=HTMLResponse)
def registration_post(request: Request, db: Session=Depends(get_db), login_: str=Form(...), password_: str=Form(...),
    password1_: str=Form(...)):
    if access(request):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    if 4 <= len(login_) <= 999 and 8 <= len(password_) <= 999 and password_ == password1_:
        if DBWork().add_user(db, login_, password_):
            request.session.clear()
            return RedirectResponse(url="/login", status_code=303)
        request.session["error_r"] = "Логин занят"
        return RedirectResponse(url="/registration", status_code=303)
    request.session["error_r"] = "Логин должен быть от 4 символов, пароль от 8 символов, пароли должны совпадать"
    return RedirectResponse(url="/registration", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    if access(request):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    if request.session.get("error_r", False) != False:
        request.session["error_r"] = False
    return templates.TemplateResponse(name="login.html", request=request, context={"error_l":
    request.session.get("error_l", False)})

@app.post("/login")
def login_post(request: Request, db: Session=Depends(get_db), login_: str=Form(...), password_: str=Form(...)):
    if access(request):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    if 4 <= len(login_) <= 999 and 8 <= len(password_) <= 999:
        if DBWork().check_user(db, login_, password_):
            request.session.clear()
            request.session["login"] = login_
            return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)
        request.session["error_l"] = "Неверный логин или пароль"
        return RedirectResponse(url="/login", status_code=303)
    request.session["error_l"] = "Логин должен быть от 4 символов, пароль от 8 символов"
    return RedirectResponse(url="/login", status_code=303)

@app.get("/tasks", response_class=HTMLResponse)
def tasks_get(request: Request, login:str, db: Session=Depends(get_db)):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    if not access1(request, login):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    if request.session.get("error_at", False) != False:
        request.session["error_at"] = False
    return templates.TemplateResponse(name="tasks.html", request=request, context={"login":
    request.session["login"], "len_login": len(request.session["login"]),
    "tasks": DBWork().get_tasks(db, request.session["login"])})

@app.get("/add_task", response_class=HTMLResponse)
def add_task_get(request: Request, login: str):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    if not access1(request, login):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    return templates.TemplateResponse(name="add_task.html", request=request, context={"login":
    request.session["login"], "len_login": len(request.session["login"]), "error_at":
    request.session.get("error_at", False)})

@app.post("/add_task")
def add_task_post(request: Request, login: str, db: Session=Depends(get_db), name_: str=Form(...)):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    if not access1(request, login):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    if len(name_) > 0:
        if DBWork().add_task(db, login, name_):
            request.session["error_at"] = "Задача создана"
            return RedirectResponse(url=f"/add_task?login={request.session['login']}", status_code=303)
        request.session["error_at"] = "Задача с таким названием уже есть"
        return RedirectResponse(url=f"/add_task?login={request.session['login']}", status_code=303)
    request.session["error_at"] = "Название задачи должнен быть хотя бы один символ"
    return RedirectResponse(url=f"/add_task?login={request.session['login']}", status_code=303)

@app.get("/exit")
def exit_get(request: Request, login: str, db: Session=Depends(get_db)):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    if not access1(request, login):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/delete_task")
def delete_task_get(request: Request, id: int, db: Session=Depends(get_db)):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)

    DBWork().check_and_delete_task(db, request.session["login"], id)
    return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

@app.get("/delete_user", response_class=HTMLResponse)
def delete_user_get(request: Request, login: str):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    if not access1(request, login):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    return templates.TemplateResponse(name="delete_user.html", request=request, context={"login":
    request.session["login"], "len_login": len(request.session["login"]), "error_du":
    request.session.get("error_du", False)})

@app.post("/delete_user")
def delete_user_post(request: Request, login: str, db: Session=Depends(get_db), password_: str=Form(...)):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    if not access1(request, login):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    if 8 <= len(password_) <= 999:
        if DBWork().delete_user(db, login, password_):
            request.session.clear()
            return RedirectResponse(url="/login", status_code=303)
    request.session["error_du"] = "Неверный пароль"
    return RedirectResponse(url=f"/delete_user?login={request.session['login']}", status_code=303)

@app.get("/new_password", response_class=HTMLResponse)
def new_password_get(request: Request, login: str):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    if not access1(request, login):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    return templates.TemplateResponse(name="new_password.html", request=request, context={"login":
    request.session["login"], "len_login": len(request.session["login"]), "error_np":
    request.session.get("error_np", False)})

@app.post("/new_password")
def new_password_post(request: Request, login: str, db: Session=Depends(get_db), password_: str=Form(...),
    password1_: str=Form(...)):
    if not access(request):
        return RedirectResponse(url="/login", status_code=303)
    if not access1(request, login):
        return RedirectResponse(url=f"/tasks?login={request.session['login']}", status_code=303)

    if 8 <= len(password_) <= 999 and 8 <= len(password_) <= 999 and password_ != password1_:
        if DBWork().new_password(db, login, password_, password1_):
            request.session["error_np"] = "Пароль изменён"
            return RedirectResponse(url=f"/new_password?login={request.session['login']}", status_code=303)
    request.session["error_np"] = "Пароль должен быть от 8 символов, новый пароль не должен совпадать со старым"
    return RedirectResponse(url=f"/new_password?login={request.session['login']}", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7000)