from datetime import timedelta

class Config:
    JWT_SECRET_KEY = "Mysecretkey123"
    #JWT_ACCESS_TOKEN_EXPIRES = False 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    WTF_CSRF_ENABLED = False