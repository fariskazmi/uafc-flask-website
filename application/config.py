
class Config:
    SECRET_KEY = "885b21dac8dd4657507ac9e80e72e851ad37b4efa0dfad45ecbf3dc7b5e2cc20"
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    RECAPTCHA_PUBLIC_KEY = ""
    RECAPTCHA_PRIVATE_KEY = ""