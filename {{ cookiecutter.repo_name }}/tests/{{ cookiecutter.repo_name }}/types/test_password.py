from passlib.context import LazyCryptContext

from {{ cookiecutter.repo_name }}.models.types.password import Password

context = LazyCryptContext(schemes=[
    'md5_crypt'
])

def test_password():
    pwd = Password(context.hash("test_password"), context)

    assert pwd == "test_password", "Comparing against plaintext should work"
    assert pwd != "wrong_password", "not equals should work"
