from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv
load_dotenv()

db_connection_str = os.environ['DB_CONNECTION_STR']


engine = create_engine(
    db_connection_str,
    connect_args={
        "ssl": {
            "ca": "./singlestore_bundle.pem"  
        }
    }
)

def load_jobs_from_db():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM jobs"))
        jobs=[]
        for row in res.all():
            jobs.append(row._asdict())
        return jobs    

def load_job_from_db(id):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM jobs WHERE id = :val"),
                          {"val": id})
        rows = res.all()
        if len(rows) == 0:
            return None
        else:
            return rows[0]._asdict()

def add_application_to_db(job_id,val):
    with engine.connect() as conn:
        query =text("INSERT INTO applications (job_id,full_name,email,linkedin,education,work_experience,cv_link) VALUES (:job_id, :full_name, :email, :linkedin, :education, :work_experience, :cv_link)"
                 )
        conn.execute(query,
                     {
                         "job_id": job_id,
                         "full_name": val['full_name'],
                         "email": val['email'],
                         "linkedin": val['linkedin'],
                         "education": val['education'],
                         "work_experience": val['work_experience'],
                         "cv_link": val['cv_link']
                     }
                    )
        conn.commit()



def get_admin(username):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM admins WHERE user_name = :username"),
                          {"username": username})
        row = res.fetchone()
        return row._asdict() if row else None

def load_applications_from_db():
    with engine.connect() as conn:
        query = text("""
            SELECT applications.*, jobs.title as job_title 
            FROM applications 
            JOIN jobs ON applications.job_id = jobs.id
        """)
        res = conn.execute(query)
        return [row._asdict() for row in res.all()]


def move_to_accepted(application_id):
    with engine.connect() as conn:
        try:
            with conn.begin():
                # 1. Fetch the application row
                application = conn.execute(
                    text("SELECT * FROM applications WHERE id = :id"),
                    {"id": application_id}
                ).fetchone()

                # 2. If no such application, abort
                if not application:
                    return False

                # 3. Convert Row to dict via _asdict()
                data = application._asdict()

                # 4. Insert into accepted_applications using named parameters
                conn.execute(
                    text("""
                        INSERT INTO accepted_applications 
                        (job_id, full_name, email, linkedin, education, work_experience, cv_link)
                        VALUES (:job_id, :full_name, :email, :linkedin, :education, :work_experience, :cv_link)
                    """),
                    {
                        "job_id":           data["job_id"],
                        "full_name":        data["full_name"],
                        "email":            data["email"],
                        "linkedin":         data["linkedin"],
                        "education":        data["education"],
                        "work_experience":  data["work_experience"],
                        "cv_link":          data["cv_link"]
                    }
                )

                # 5. Delete from applications
                conn.execute(
                    text("DELETE FROM applications WHERE id = :id"),
                    {"id": application_id}
                )

                return True
        except Exception as e:
            # Log and return False on any error
            print(f"Error moving to accepted: {str(e)}")
            return False


def move_to_rejected(application_id):
    with engine.connect() as conn:
        try:
            with conn.begin():
                # 1. Fetch the application row
                application = conn.execute(
                    text("SELECT * FROM applications WHERE id = :id"),
                    {"id": application_id}
                ).fetchone()

                # 2. If no such application, abort
                if not application:
                    return False

                # 3. Convert Row to dict via _asdict()
                data = application._asdict()

                # 4. Insert into rejected_applications using named parameters
                conn.execute(
                    text("""
                        INSERT INTO rejected_applications 
                        (job_id, full_name, email, linkedin, education, work_experience, cv_link)
                        VALUES (:job_id, :full_name, :email, :linkedin, :education, :work_experience, :cv_link)
                    """),
                    {
                        "job_id":           data["job_id"],
                        "full_name":        data["full_name"],
                        "email":            data["email"],
                        "linkedin":         data["linkedin"],
                        "education":        data["education"],
                        "work_experience":  data["work_experience"],
                        "cv_link":          data["cv_link"]
                    }
                )

                # 5. Delete from applications
                conn.execute(
                    text("DELETE FROM applications WHERE id = :id"),
                    {"id": application_id}
                )

                return True
        except Exception as e:
            # Log and return False on any error
            print(f"Error moving to rejected: {str(e)}")
            return False



def add_admin_to_db(username, password_hash):
    with engine.connect() as conn:
        try:
            result = conn.execute(text("""
                INSERT INTO admins (user_name, password_hash)
                VALUES (:username, :password_hash)
            """), {
                "username": username,
                "password_hash": password_hash
            })
            conn.commit()
            return True
        except Exception as e:
            print(f"Database Error: {str(e)}")  # Detailed error logging
            conn.rollback()
            return False
