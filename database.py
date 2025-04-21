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

# with engine.connect() as conn:
#     result = conn.execute(text("SELECT * FROM jobs"))
#     res_dicts=[]

#     for row in result.all():
#         res_dicts.append(row._asdict())







    
    
