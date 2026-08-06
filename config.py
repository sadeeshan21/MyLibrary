class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1111@localhost/mydb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'change-this-to-something-random-later'
    SQLALCHEMY_ECHO = True   # <-- add this line