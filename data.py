
from dotenv import dotenv_values
from flask import request
from sqlalchemy import create_engine, inspect

cfg = dotenv_values(".env")

con_engine = create_engine(f"mysql+pymysql://{cfg['USR']}:{cfg['PWD']}@{cfg['HOST']}/{cfg['DB']}")
conn = con_engine.connect()
inspector = inspect(con_engine)


def db_exec(engine, sql):
    # print(f"sql: {sql}")
    if sql.strip().startswith('select'):
        return [dict(r) for r in engine.execute(sql).fetchall()]
    else:
        return engine.execute(sql)


def fetch_max_pk(table):
    sql = f"select max(pk) as pk from {table}"
    return db_exec(conn, sql)[0]['pk']


def url_label(url):
    if url is None:
        return None
    else:
        return url.split('/')[-1]


def contracts_req_main(digest):
    context = dict()
    context['digest'] = digest

    sql = """
        select s1.pk, s1.ariba_id, s1.contract_id, s1.sap_id, s1.requested, v1.name
        from supporting_doc_requests s1, contracts c1, vendors v1
        where (s1.ariba_id = c1.ariba_id or (ISNULL(s1.ariba_id) and ISNULL(c1.ariba_id))) and
            (s1.contract_id = c1.contract_id or (ISNULL(s1.contract_id) and ISNULL(c1.contract_id))) and
            (s1.sap_id = c1.sap_id or (ISNULL(s1.sap_id) and ISNULL(c1.sap_id))) and
            c1.vendor_pk = v1.pk
    """
    rows = dict()
    for row in db_exec(conn, sql):
        if row['pk'] not in rows:
            rows[row['pk']] = row

    req_pks = ', '.join([ str(pk) for pk in list(rows.keys())])
    sql = f"select * from supporting_docs where request_pk in ({req_pks})"
    for doc in db_exec(conn, sql):
        pk = doc['request_pk']
        if pk in rows:
            if 'urls' not in rows[pk]:
                rows[pk]['urls'] = list()
            url_entry = dict()
            url_entry['url'] = doc['url']
            url_entry['label'] = url_label(doc['url'])
            rows[pk]['urls'].append(url_entry)

    context['reqs'] = rows.values()
    return context


def contracts_add_form(digest):
    context = dict()
    context['digest'] = digest
    context['reqs'] = db_exec(conn, "select * from supporting_doc_requests")
    context['vendors'] = db_exec(conn, "select * from vendors order by name")
    return context


def contracts_req_add(form):
    # print(f"request: {dict(request.form)}")

    next_req_pk = fetch_max_pk('supporting_doc_requests') + 1

    if form['a_id'] != '' or form['c_id'] != '' or form['s_id'] != '':
        if form['req_date'] != 'None':
            if request.form['a_id'] is None:
                a_id = 'NULL'
            else:
                a_id = f"'{request.form['a_id']}'"
            if request.form['c_id'] is None:
                c_id = 'NULL'
            else:
                c_id = f"'{request.form['c_id']}'"
            if request.form['s_id'] is None:
                s_id = 'NULL'
            else:
                s_id = f"'{request.form['s_id']}'"
            sql = f"""
            insert into supporting_doc_requests
            (pk, ariba_id, contract_id, sap_id, request_entity, requested)
            values ({next_req_pk}, {a_id}, {c_id}, {s_id}, 'SCC Procurement', '{request.form['req_date']}')
            """
            print(f"sql: {sql}")
            # db_exec(conn, sql)


def contracts_doc_add(form):
    next_doc_pk = fetch_max_pk('supporting_docs') + 1
    print(f"form: {form}")
    parts = list()
    if form['a_id'] != '':
        parts.append(f"ariba_id = '{form['a_id']}'")
    if form['c_id'] != '':
        parts.append(f"contracts_id = '{form['c_id']}'")
    if form['s_id'] != '':
        parts.append(f"sap_id = '{form['s_id']}'")
    if form['req_date'] != '':
        parts.append(f"requested = '{form['req_date']}'")
    quals = ' and '.join(parts)
    sql = f"select * from supporting_doc_requests where {quals}"
    rows = db_exec(conn, sql)

    req_pk = rows[0]['pk']

    if form['url1'] != '':
        sql = f"""
            insert into supporting_docs values
            ({next_doc_pk}, {req_pk}, '{form['url1']}', '{form['rec_date']}')
        """
        # print(f"sql: {sql}")
        db_exec(conn, sql)
        next_doc_pk += 1

    if form['url2'] != '':
        sql = f"""
            insert into supporting_docs values
            ({next_doc_pk}, {req_pk}, '{form['url2']}', '{form['rec_date']}')
        """
        # print(f"sql: {sql}")
        db_exec(conn, sql)
        next_doc_pk += 1

    if form['url3'] != '':
        sql = f"""
            insert into supporting_docs values
            ({next_doc_pk}, {req_pk}, '{form['url3']}', '{form['rec_date']}')
        """
        # print(f"sql: {sql}")
        db_exec(conn, sql)
        next_doc_pk += 1
