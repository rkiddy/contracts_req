
from dotenv import dotenv_values
from sqlalchemy import create_engine, inspect

cfg = dotenv_values(".env")

engine = create_engine(f"mysql+pymysql://ray:{cfg['PWD']}@{cfg['HOST']}/{cfg['DB']}")
conn = engine.connect()
inspector = inspect(engine)

# mysql> desc supporting_docs;
# +-------------+---------------+------+-----+---------+-------+
# | Field       | Type          | Null | Key | Default | Extra |
# +-------------+---------------+------+-----+---------+-------+
# | pk          | int           | NO   | PRI | NULL    |       |
# | vendor_pk   | int           | YES  |     | NULL    |       |
# | contract_id | varchar(31)   | YES  | MUL | NULL    |       |
# | sap_id      | varchar(31)   | YES  | MUL | NULL    |       |
# | ariba_id    | varchar(31)   | YES  | MUL | NULL    |       |
# | url         | varchar(1023) | YES  |     | NULL    |       |
# | request_pk  | int           | YES  |     | NULL    |       |
# +-------------+---------------+------+-----+---------+-------+
#
# mysql> desc supporting_doc_requests;
# +----------------+-------------+------+-----+---------+-------+
# | Field          | Type        | Null | Key | Default | Extra |
# +----------------+-------------+------+-----+---------+-------+
# | pk             | int         | NO   | PRI | NULL    |       |
# | ariba_id       | varchar(31) | YES  |     | NULL    |       |
# | contract_id    | varchar(31) | YES  |     | NULL    |       |
# | sap_id         | varchar(31) | YES  |     | NULL    |       |
# | vendor_pk      | int         | YES  |     | NULL    |       |
# | request_entity | varchar(63) | YES  |     | NULL    |       |
# | requested      | char(10)    | YES  |     | NULL    |       |
# | received       | char(10)    | YES  |     | NULL    |       |
# +----------------+-------------+------+-----+---------+-------+


# rows is a result cursor, columns is a dictionary or key -> column number in rows.
def fill_in_table(rows, columns):
    result = list()
    for row in rows:
        found = dict()
        for key in columns.keys():
            found[key] = row[columns[key]]
        result.append(found)
    return result


def money(cents):
    cents = int(cents) / 100
    cents = str(cents)
    return "$ {:,.2f}".format(float(cents))


request_columns = {
    'pk': 0,
    'aID': 1,
    'cID': 2,
    'sID': 3,
    'requested': 4,
    'received': 5
}

contract_columns = {
    'vpk': 0,
    'vname': 1,
    'amount': 2,
    'eff_date': 3,
    'exp_date': 4
}


def build_main():

    context = dict()

    sql = f"""
    select r1.pk, r1.ariba_id, r1.contract_id, r1.sap_id,
        r1.requested, r1.received
    from supporting_doc_requests r1
    where r1.request_entity = 'SCC Procurement'
    order by r1.requested desc
    """

    requests = fill_in_table(conn.execute(sql).fetchall(), request_columns)

    for request in requests:

        sql = f"""
        select c1.vendor_pk, v1.name, c1.contract_value,
            c1.effective_date, c1.expir_date
        from contracts c1, vendors v1
        where c1.ariba_id = '{request['aID']}' and
            c1.contract_id = '{request['cID']}' and
            c1.sap_id = '{request['sID']}' and
            c1.vendor_pk = v1.pk
        order by month_pk
        """

        sql = sql.replace("= 'None'", " is NULL")

        contracts = fill_in_table(conn.execute(sql).fetchall(), contract_columns)

        if len(contracts) > 0:
            contract = contracts[-1]
        else:
            contract = {}

        if 'amount' in contract:
            contract['amount'] = money(contract['amount'])

        request['contract'] = contract

        sql = f"""
        select url from supporting_docs
        where request_pk = {request['pk']}
        """

        docs = fill_in_table(conn.execute(sql).fetchall(), {'url': 0})

        if len(docs) > 0:
            request['docs'] = docs

    context['requests'] = requests

    return context

