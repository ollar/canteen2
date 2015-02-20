class Config():
    SECRET_KEY = "UX\x97\xc7\xd2\xf4\xa1Xf\xdc\xbeuSM\x9b"
    SALT = "\x85\x88\xf8\x9e\xf5K\xc8O\xebe\xbc'zlz"
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost/canteen'
    DEBUG = True