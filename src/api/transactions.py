from decimal import Decimal
from database import database, Transaction, User, UserTransactionLink, Group
from datetime import date
from sqlmodel import Session

def create_transaction(
    title: str,
    amount: Decimal,
    transaction_date: date,
    payer_id: int,
    group_id: int,
    breakdown: dict[int, Decimal]
    ) -> bool:
    with Session(database) as session:
        payees_id = [x for x in breakdown.keys()]

        payer = User.get_by_id(payer_id, session)
        group = Group.get_by_id(group_id, session)
        payees = User.get_by_ids(payees_id, session)

        # Check amount is valid
        breakdown_total = sum([x for x in breakdown.values()])
        if amount != breakdown_total:
            raise ValueError(f"Mismatch totals. Total amount should be {amount}. Breakdown amount is {breakdown_total}")

        payees_table = zip(payees, breakdown.values())
        transaction = Transaction(title=title, amount=amount, transaction_date=transaction_date, payer=payer, group=group)

        transaction_details = []
        for payee, amount in payees_table:
            transaction_details.append(UserTransactionLink(transaction=transaction, user=payee, amount=amount))

        session.add(transaction)
        session.commit()
    return True

def update_transaction(
    transaction_id: int,
    *,
    title: str | None = None,
    amount: Decimal | None = None,
    transaction_date: date | None = None,
    payer_id: int | None = None,
    group_id: int | None = None,
    breakdown: dict[int, Decimal] = None
    ):
    # TODO: Should check updating amount does not break total breakdown amount
    with Session(database) as session:
        transaction = Transaction.get_by_id(transaction_id, session)

        if title:
            transaction.title = title
        if amount:
            transaction.amount = amount
        if transaction_date:
            transaction.transaction_date = transaction_date
        if payer_id:
            transaction.payer_id = payer_id
        if group_id:
            transaction.group_id = group_id

        if breakdown:
            breakdown_list = []
            for payee, amount in breakdown.items():
                current_breakdown = UserTransactionLink.get_by_id(transaction_id, payee, session)
                current_breakdown.amount = amount
                breakdown_list.append(current_breakdown)

        session.commit()

def delete_transaction(transaction_id: int):
    with Session(database) as session:
        transaction = Transaction.get_by_id(transaction_id, session)
        for link in transaction.transaction_link:
            session.delete(link)
        session.delete(transaction)
        session.commit()

def get_transaction(transaction_id: int):
    with Session(database) as session:
        return Transaction.get_by_id(transaction_id, session)