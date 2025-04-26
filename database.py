from sqlalchemy import create_engine, text
import os

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






    
    
