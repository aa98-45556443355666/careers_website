from sqlalchemy import create_engine, text

db_connection_str = (
    "mysql+pymysql://aarush_0312-b2832:Q8cF%2B1J%2CT8t%23qzj3z%3D4P;U(@"
    "svc-3482219c-a389-4079-b18b-d50662524e8a-shared-dml.aws-virginia-6.svc.singlestore.com:3333/"
    "db_aarush__a0ad9"
    "?charset=utf8mb4"
)

engine = create_engine(
    db_connection_str,
    connect_args={
        "ssl": {
            "ca": "./singlestore_bundle.pem"  
        }
    }
)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM jobs"))
        for row in result:
            print(row)
except Exception as e:
    print("Error:", e)
