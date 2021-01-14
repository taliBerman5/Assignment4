import inspect


def row_map(row, col_mapping, dto_type):
    ctor_args = [row[idx] for idx in col_mapping]
    return dto_type(*ctor_args)


def orm(cursor, dto_type):
    args = inspect.getargspec(dto_type.__init__).args

    args = args[1:]
    col_names = [column[0] for column in cursor.description]
    col_mapping = [col_names.index(arg) for arg in args]
    return [row_map(row, col_mapping, dto_type) for row in cursor.fetchall()]


class Dao:
    def __init__(self, dto_type, conn):
        self._conn = conn
        self._dto_type = dto_type
        self._table_name = dto_type.__name__.lower() + 's'
        self.last_id = 0

    def insert(self, dto_instance):
        ins_dict = vars(dto_instance)
        column_names = ','.join(ins_dict.keys())
        params = ins_dict.values()
        qmarks = ','.join(['?'] * len(ins_dict))

        stmt = 'INSERT INTO {} ({}) VALUES ({})'.format(self._table_name, column_names, qmarks)
        params = list(params)
        self._conn.execute(stmt, params)
        self.last_id += 1

    def find_all(self):
        c = self._conn.cursor()
        c.execute('SELECT * FROM {}'.format(self._table_name))
        return orm(c, self._dto_type)

    def find(self, **keyvals):
        column_names = keyvals.keys()
        params = keyvals.values()

        stmt = 'SELECT * FROM {} WHERE {}'.format(self._table_name, ' AND '.join([col + '=?' for col in column_names]))

        c = self._conn.cursor()
        c.execute(stmt, list(params))
        return orm(c, self._dto_type)

    def delete(self, **keyvals):
        column_names = keyvals.keys()
        params = keyvals.values()

        stmt = 'DELETE FROM {} WHERE {}'.format(self._table_name, ' AND '.join([col + '=?' for col in column_names]))

        c = self._conn.cursor()
        c.execute(stmt, list(params))

    def update(self, set_values, cond):
        set_column_names = set_values.keys()
        set_params = list(set_values.values())

        cond_column_names = cond.keys()
        cond_params = list(cond.values())

        params = set_params + cond_params

        stmt = 'UPDATE {} SET {} WHERE {}'.format(self._table_name,
                                                  ', '.join([set + ' = ?' for set in set_column_names]),
                                                  ' AND '.join([cond + ' = ?' for cond in cond_column_names]))

        c = self._conn.cursor()
        c.execute(stmt, params)
