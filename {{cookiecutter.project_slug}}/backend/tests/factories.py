import factory
from faker import Faker
from sqlmodel import Session

from app.models import User, UserCreate, UserUpdate
from app.core.security import get_password_hash

faker = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.LazyFunction(faker.email)
    password = factory.LazyFunction(faker.password)
    hashed_password = factory.LazyAttribute(lambda o: get_password_hash(o.password))
    is_active = True
    is_superuser = False
    full_name = factory.LazyFunction(faker.name)
    name = factory.LazyFunction(faker.first_name)
    last_name = factory.LazyFunction(faker.last_name)
    cellphone = factory.LazyFunction(lambda: faker.random_int(min=100000000, max=2000000000))
    has_mfa = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        session: Session = kwargs.pop("session")
        plain_password = kwargs.pop("password")  # Get the plain password
        obj = model_class(**kwargs)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj, plain_password


class UserCreateFactory(factory.Factory):
    class Meta:
        model = UserCreate

    email = factory.LazyFunction(faker.email)
    password = factory.LazyFunction(faker.password)
    full_name = factory.LazyFunction(faker.name)
    name = factory.LazyFunction(faker.first_name)
    last_name = factory.LazyFunction(faker.last_name)


class UserUpdateFactory(factory.Factory):
    class Meta:
        model = UserUpdate

    email = factory.LazyFunction(faker.email)
    password = factory.LazyFunction(faker.password)
    full_name = factory.LazyFunction(faker.name)
    name = factory.LazyFunction(faker.first_name)
    last_name = factory.LazyFunction(faker.last_name)
    cellphone = factory.LazyFunction(lambda: faker.random_int(min=100000000, max=2000000000))
    is_active = factory.LazyFunction(faker.boolean)
    is_superuser = factory.LazyFunction(faker.boolean)
    has_mfa = factory.LazyFunction(faker.boolean)
