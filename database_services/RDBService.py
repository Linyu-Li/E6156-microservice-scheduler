import pymysql
import logging

import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBService:
    def __init__(self):
        pass

    @classmethod
    def _get_db_connection(cls):
        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()

        print("connecting to database {}".format(db_info))
        db_connection = pymysql.connect(
            **db_info
        )
        return db_connection

    @classmethod
    def get_by_prefix(cls, db_schema, table_name, column_name, value_prefix):
        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " where " + \
              column_name + " like " + "'" + value_prefix + "%'"
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def _get_where_clause_args(cls, template):
        terms = []
        args = []
        clause = None
        limit = 0;
        offset = 0;

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k, v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " where " + " AND ".join(terms)

        return clause, args

    @classmethod
    def _get_set_clause_args(cls, template):
        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k, v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " set " + " ,".join(terms)

        return clause, args

    @classmethod
    def find_by_template(cls, db_schema, table_name, template, limit=None, offset=None):
        print("getting database connection")
        wc, args = RDBService._get_where_clause_args(template)

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        if not limit and not offset:
            sql = "select * from " + db_schema + "." + table_name + " " + wc
        else:
            sql = "select * from " + db_schema + "." + table_name + " " + wc + "limit "+limit + " offset "+offset
        res = cur.execute(sql, args=args)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def delete_by_template(cls, db_schema, table_name, template):
        wc, args = RDBService._get_where_clause_args(template)

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "delete from " + db_schema + "." + table_name + " " + wc
        cur.execute(sql, args=args)
        cur.fetchall()
        conn.commit()

        conn.close()

        return

    @classmethod
    def update_by_template(cls, db_schema, table_name, template, where_id):
        sc, args_sc = RDBService._get_set_clause_args(template)
        '''
        where_json = None
        for i in sc:
            if i == "where":
                where_json = template["where"]
                break

        wc, args_wc = RDBService._get_where_clause_args(where_json)
        '''

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "update " + db_schema + "." + table_name + sc + " where Id = " + str(where_id)
        cur.execute(sql, args=args_sc)
        cur.fetchall()
        conn.commit()

        conn.close()

        return

    @classmethod
    def run_sql(cls, sql_statement, args=None, fetch=False):
        conn = RDBService._get_db_connection()

        try:
            cur = conn.cursor()
            res = cur.execute(sql_statement, args=args)
            if fetch:
                res = cur.fetchall()
            conn.commit()
        except Exception as e:
            conn.close()
            raise e

        return res

    @classmethod
    def create(cls, db_schema, table_name, create_data):
        cols = []
        vals = []
        args = []

        for k, v in create_data.items():
            cols.append(k)
            vals.append('%s')
            args.append(v)

        cols_clause = "(" + ",".join(cols) + ")"
        vals_clause = "values (" + ",".join(vals) + ")"

        sql_stmt = "insert into " + db_schema + "." + table_name + " " + cols_clause + \
                   " " + vals_clause

        res = RDBService.run_sql(sql_stmt, args)
        return res

    @classmethod
    def get_max_id(cls, db_schema, table_name):
        sql_stmt = "select max(Id) as id from " + db_schema + "." + table_name
        res = RDBService.run_sql(sql_stmt, fetch=True)
        return res[0]["id"]
