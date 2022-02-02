# from decimal import Decimal
# from database import database, Transaction, Journal, Group
# from datetime import date
# from sqlmodel import Session


# def update_transaction(
#     transaction_id: int,
#     *,
#     title: str | None = None,
#     amount: Decimal | None = None,
#     transaction_date: date | None = None,
#     group_id: int | None = None,
#     breakdown: dict[int, Decimal] = None
#     ):
#     # TODO: Should check updating amount does not break total breakdown amount
#     with Session(database) as session:
#         transaction = Transaction.get_by_id(transaction_id, session)

#         if title:
#             transaction.description = title
#         if amount:
#             transaction.amount = amount
#         if transaction_date:
#             transaction.transaction_date = transaction_date
#         if group_id:
#             transaction.group_id = group_id

#         if breakdown:
#             breakdown_list = []
#             for payee, amount in breakdown.items():
#                 current_breakdown = Journal.get_by_id(transaction_id, payee, session)
#                 current_breakdown.amount = amount
#                 breakdown_list.append(current_breakdown)

#         session.commit()

# def delete_transaction(transaction_id: int, session: Session):
#     transaction = Transaction.get_by_id(transaction_id, session)
#     for journal in transaction.journals:
#         session.delete(journal)
#     session.delete(transaction)
#     session.commit()
