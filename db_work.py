from db_tables import User, Task
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class DBWork:
    def user_found(self, db, login):
        return db.query(User).filter_by(login=login).first()

    def add_user(self, db, login, password):
        db_user_found = self.user_found(db, login)
        if not db_user_found:
            db_new_user = User(login=login, password=generate_password_hash(password))
            db.add(db_new_user)
            db.commit()
            db.refresh(db_new_user)
            return True
        return False

    def check_user(self, db, login, password):
        db_user_found = self.user_found(db, login)
        if db_user_found:
            if check_password_hash(db_user_found.password, password):
                return True
        return False

    def add_task(self, db, login, name):
        db_user_found = self.user_found(db, login)
        db_tasks_found = db.query(Task).filter_by(name=name).all()
        if db_user_found:
            if len(db_tasks_found) >= 1:
                if len([i for i in db_tasks_found if i.user_id == db_user_found.id]) >= 1:
                    return False
            db_new_task = Task(name=name, date=str(datetime.now())[:-10], user_id=db_user_found.id)
            db.add(db_new_task)
            db.commit()
            db.refresh(db_new_task)
            return True
        return False

    def get_tasks(self, db, login):
        db_user_found = self.user_found(db, login)
        if db_user_found:
            db_tasks_found = db.query(Task).filter_by(user_id=db_user_found.id).all()
            return db_tasks_found
        return []

    def delete_user(self, db, login, password):
        db_user_found = self.user_found(db, login)
        if db_user_found:
            if check_password_hash(db_user_found.password, password):
                db_tasks_found = db.query(Task).filter_by(user_id=db_user_found.id).all()
                if db_tasks_found:
                    for i in db_tasks_found: db.delete(i)
                db.delete(db_user_found)
                db.commit()
                return True
        return False

    def check_and_delete_task(self, db, login, id):
        db_user_found = self.user_found(db, login)
        db_task_found = db.query(Task).filter_by(id=id).first()
        if db_user_found and db_task_found:
            if db_user_found.id == db_task_found.user_id:
                db.delete(db_task_found)
                db.commit()

    def new_password(self, db, login, password1, password2):
        db_user_found = self.user_found(db, login)
        if db_user_found:
            if check_password_hash(db_user_found.password, password1):
                db_user_found.password = generate_password_hash(password2)
                db.commit()
                db.refresh(db_user_found)
                return True
        return False