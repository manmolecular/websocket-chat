from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """
    Validate the username/password part
    """

    username: str = Field(min_length=1, max_length=10, regex=r"[a-zA-Z0-9]{1,10}$")
    password: str = Field(min_length=8, max_length=30)


def validate(username: str, password: str) -> bool:
    """
    Validate username/password
    :param username: username
    :param password: password
    :return: True or False
    """
    try:
        UserBase(username=username, password=password)
    except:
        return False
    return True
