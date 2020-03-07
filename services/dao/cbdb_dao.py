from collections import defaultdict

from services.dao.base_dao import SqliteDAO


class CBDBDAO(SqliteDAO):
    def __init__(self, path, use_cache=True):
        super().__init__(path, use_cache)
        self.all_dynasties_cache = {}
        self.all_status_cache = {}
        self.person_code2address_cache = defaultdict(list)
        self.person_name2ids = defaultdict(set)

    def get_all_dynasties(self):
        if len(self.all_dynasties_cache) == 0:
            sql_str = '''SELECT DISTINCT c_dy, c_dynasty,c_dynasty_chn FROM dynasties'''
            rows = self._select(sql_str, ['dynasty_code', 'desc', 'desc_chn'], ())
            if not self.use_cache:
                return {col['dynasty_code']: {'desc': col['desc'], 'desc_chn': col['desc_chn']} for col in rows}
            self.all_dynasties_cache = {col['dynasty_code']: {'desc': col['desc'], 'desc_chn': col['desc_chn']} for col
                                        in
                                        rows}
        return self.all_dynasties_cache

    def get_all_status(self):
        if len(self.all_status_cache) == 0:
            sql_str = '''SELECT DISTINCT c_status_code, c_status_desc,c_status_desc_chn FROM status_codes'''
            rows = self._select(sql_str, ['status_code', 'desc', 'desc_chn'], ())
            self.all_status_cache = {col['status_code']: {'desc': col['desc'], 'desc_chn': col['desc_chn']} for col in
                                     rows}
        return self.all_status_cache

    def get_person_by_ranges(self, dynasty_codes, min_year, max_year, is_female, status_codes):
        sql_str = '''SELECT DISTINCT biog_main.c_personid,c_name_chn FROM dynasties,biog_main,status_data,status_codes WHERE dynasties.c_dy=biog_main.c_dy AND status_data.c_personid = biog_main.c_personid AND status_data.c_status_code = status_codes.c_status_code'''
        sql_args = []
        if dynasty_codes is not None and len(dynasty_codes) > 0:
            sql_str += ''' AND dynasties.c_dy in {}'''.format(
                tuple(dynasty_codes) if len(dynasty_codes) > 1 else "({})".format(dynasty_codes[0]))
        if min_year is not None:
            sql_str += ''' AND (c_birthyear IS NULL OR c_birthyear=0 OR c_birthyear> ?) '''
            sql_args.append(min_year)
        if max_year is not None:
            sql_str += ''' AND (c_deathyear IS NULL OR c_deathyear=0 OR c_deathyear< ?) '''
            sql_args.append(max_year)
        if is_female is not None:  # if no, print 0; if yes, print 1
            sql_str += ''' AND c_female = ? '''
            sql_args.append(1 if is_female else 0)
        if status_codes is not None and len(status_codes) > 0:
            sql_str += ''' AND status_codes.c_status_code in {}'''.format(
                tuple(status_codes) if len(status_codes) > 1 else "({})".format(status_codes[0]))
        rows = self._select(sql_str, ['person_code', 'name'], sql_args)
        return {cols['person_code']: cols['name'] for cols in rows}

    def get_address_by_person_codes(self, person_codes):
        new_person_codes = [_code for _code in person_codes if _code not in self.person_code2address_cache]
        if self.use_cache and len(new_person_codes) > 0:
            sql_str = '''SELECT DISTINCT c_personid,x_coord,y_coord,c_name_chn FROM biog_addr_data,addresses WHERE biog_addr_data.c_addr_id = addresses.c_addr_id AND c_personid in {}'''.format(
                tuple(new_person_codes) if len(new_person_codes) > 1 else "({})".format(new_person_codes[0]))
            rows = self._select(sql_str, ['person_code', 'x_coord', 'y_coord', 'address_name'], ())
            for cols in rows:
                self.person_code2address_cache[cols['person_code']].append(
                    {'x_coord': cols['x_coord'], 'y_coord': cols['y_coord'], 'address_name': cols['address_name']})
        return {_code: self.person_code2address_cache[_code] for _code in person_codes}

    def get_person_by_person_names(self, person_names):
        new_person_names = [_name for _name in person_names if _name not in self.person_name2ids]
        if self.use_cache and len(new_person_names) > 0:
            sql_str = '''SELECT DISTINCT c_personid, c_name_chn FROM biog_main WHERE c_name_chn in {}'''.format(
                tuple(new_person_names) if len(new_person_names) > 1 else "('{}')".format(new_person_names[0]))
            rows = self._select(sql_str, ['person_code', 'name'], ())
            for cols in rows:
                self.person_name2ids[cols['name']].add(cols['person_code'])
        return {_name: list(self.person_name2ids[_name]) for _name in person_names}


if __name__ == '__main__':
    cbdb_dao = CBDBDAO('../../dataset/CBDB_20190424.db', use_cache=True)
    all_status = cbdb_dao.get_all_status()
    all_dynasties = cbdb_dao.get_all_dynasties()
    print(len(cbdb_dao.get_person_by_ranges(None, None, None, None, None)))
    print(len(cbdb_dao.get_person_by_ranges([15], None, None, None, None)))
    print(len(cbdb_dao.get_person_by_ranges([15, 6], 980, None, None, None)))
    print(len(cbdb_dao.get_person_by_ranges([15, 6], 980, 1120, None, None)))
    print(len(cbdb_dao.get_person_by_ranges([15, 6], 980, 1120, True, None)))
    print(len(cbdb_dao.get_person_by_ranges([15, 6], 980, 1120, True, [2, 40])))
    person = cbdb_dao.get_person_by_ranges([15, 6], 980, 1120, False, [2])
    print(len(person))
    addresses = cbdb_dao.get_address_by_person_codes(person.keys())
    print(1)
