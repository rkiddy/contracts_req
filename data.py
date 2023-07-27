
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


def url_label(url):
    if url is None:
        return None
    else:
        return url.split('/')[-1]


def contracts_req_main():
    context = dict()
    sql = """
        select r1.ariba_id, r1.contract_id, r1.sap_id, r1.requested, r1.received, r2.vendor_pk, r2.url
        from supporting_doc_requests r1 left outer join supporting_docs r2 on r1.pk = r2.request_pk
        order by r1.requested desc
    """
    reqs = db_exec(conn, sql)
    found = dict()
    vendor_pks = list()
    for req in reqs:
        req['url_label'] = url_label(req['url'])
        if req['vendor_pk']:
            vendor_pks.append(req['vendor_pk'])
        key = f"{req['ariba_id']}|{req['contract_id']}|{req['sap_id']}|{req['requested']}"
        if key not in found:
            found[key] = list()
            found[key].append(req)
        found[key].append({'url': req['url'], 'url_label': req['url_label']})

    vendor_pks_str = ', '.join(vendor_pks)
    sql = f"select * from vendors where pk in ({vendor_pks_str})"
    vendors = dict()
    for v in db_exec(conn, sql):
        vendors[str(v['pk'])] = v['name']

    next_found = list()

    for row in found:
        if found[row][0]['vendor_pk']:
            found[row][0]['vendor'] = vendors[found[row][0]['vendor_pk']]
        next_found.append(found[row])

    context['reqs'] = next_found
    print(f"reqs: {next_found}")

    return context
