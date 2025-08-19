import pytest 
from asmac_backend.asmac_backend.v0 import ASMaC_Backend

def test_create_user():
    # Arrange
    user_name = "alejandro"
    password = "test_password"
    name = "Test User"

    # Act
    result = ASMaC_Backend.create_user(user_name=user_name, password=password, name=name)
    print(result)

def test_login_user():
    # Arrange
    user_name = "alejandro"
    password = "test_password"

    # Act
    user = ASMaC_Backend.login_user(user_name=user_name, password=password)
    print(user)
if __name__ == "__main__":
    test_create_user()
    test_login_user()