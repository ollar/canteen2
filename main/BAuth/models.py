from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from main.database import Base, db_session

class Client(Base):
    __tablename__ = 'client'
    # human readable name, not required
    name = Column(String(40))

    # human readable description, not required
    description = Column(String(400))

    # creator of the client, not required
    user_id = Column(Integer, ForeignKey('user.id'))
    # required if you need to support client credential
    user = relationship('User')

    client_id = Column(String(40), primary_key=True)
    client_secret = Column(String(55), unique=True, index=True,
                              nullable=False)

    # public or confidential
    is_confidential = Column(Boolean)

    _redirect_uris = Column(Text)
    _default_scopes = Column(Text)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

class Grant(Base):
    __tablename__ = 'grant'
    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer, ForeignKey('user.id', ondelete='CASCADE')
    )
    user = relationship('User')

    client_id = Column(
        String(40), ForeignKey('client.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    code = Column(String(255), index=True, nullable=False)

    redirect_uri = Column(String(255))
    expires = Column(DateTime)

    _scopes = Column(Text)

    def delete(self):
        db_session.delete(self)
        db_session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

class Token(Base):
    __tablename__ = 'token'
    id = Column(Integer, primary_key=True)
    client_id = Column(
        String(40), ForeignKey('client.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    user_id = Column(
        Integer, ForeignKey('user.id')
    )
    user = relationship('User')

    # currently only bearer is supported
    token_type = Column(String(40))

    access_token = Column(String(255), unique=True)
    refresh_token = Column(String(255), unique=True)
    expires = Column(DateTime)
    _scopes = Column(Text)

    def delete(self):
        db_session.delete(self)
        db_session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
