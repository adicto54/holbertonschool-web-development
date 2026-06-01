#!/usr/bin/env python3
"""
Database module for user authentication
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from user import Base, User


class DB:
    """Database class to interact with users table"""

    def __init__(self):
        """Initialize the database"""
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self):
        """Get the database session"""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a user to the database
        
        Args:
            email: User's email
            hashed_password: User's hashed password
            
        Returns:
            User object
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """Find a user by arbitrary keyword arguments
        
        Args:
            **kwargs: Arbitrary keyword arguments to filter by
            
        Returns:
            User object
            
        Raises:
            NoResultFound: If no user is found
            InvalidRequestError: If invalid query arguments are passed
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).first()
            if user is None:
                raise NoResultFound()
            return user
        except TypeError:
            raise InvalidRequestError()

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update a user's attributes
        
        Args:
            user_id: User's ID
            **kwargs: Attributes to update
            
        Raises:
            ValueError: If an invalid attribute is passed
        """
        user = self.find_user_by(id=user_id)
        
        # Check if all kwargs are valid User attributes
        for key in kwargs:
            if not hasattr(user, key):
                raise ValueError(f"Invalid attribute: {key}")
        
        # Update user attributes
        for key, value in kwargs.items():
            setattr(user, key, value)
        
        self._session.commit()
