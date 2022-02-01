from database import database, Group, User
from sqlmodel import Session

def create_group(
    name: str,
    group_type: str | None = None,
    image: bytes | None = None,
):
    with Session(database) as session:
        group = Group(name=name)
        if group_type:
            group.type = group_type
        if image:
            group.image = image

        session.add(group)
        session.commit()

def update_group(
    group_id: int,
    name: str | None = None,
    group_type: str | None = None,
    image: bytes | None = None
):
    with Session(database) as session:
        group = Group.get_by_id(group_id, session)
        if name:
            group.name = name
        if group_type:
            group.type = group_type
        if image:
            group.image = image

        session.commit()

def delete_group(group_id: int):
    with Session(database) as session:
        group = Group.get_by_id(group_id, session)
        session.delete(group)
        session.commit()

def add_user_to_group(group_id: int, user_id: int):
    with Session(database) as session:
        group = Group.get_by_id(group_id, session)
        user = User.get_by_id(user_id, session)
        user.groups.append(group)
        session.commit()
