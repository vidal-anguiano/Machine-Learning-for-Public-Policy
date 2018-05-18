from vatools.src import util
from vatools.src.db_conn import DB_Connection
from vatools.src import ml



if __name__ == '__main__':
    db = DB_Connection('../credentials.json')
    db.connect()
    outcomes = db.query('select * from outcomes')
    projects = db.query('select * from projects')

    util.impute(outcomes,
                col_meth = {'at_least_1_teacher_referred_donor': ['f'],
                            'at_least_1_green_donation': ['f'],
                            'three_or_more_non_teacher_referred_donors': ['f'],
                            'one_non_teacher_referred_donor_giving_100_plus': ['f'],
                            'donation_from_thoughtful_donor': ['f'],
                            'great_messages_proportion': 'zeros',
                            'non_teacher_referred_count': 'zeros',
                            'teacher_referred_count': 'zeros'})
    print('Missing values in outcomes data imputed with "f".')

    util.impute(projects,
                col_meth = {'primary_focus_area': 'missing',
                            'grade_level': 'missing',
                           'resource_type': 'missing',
                           'school_metro': 'missing'})
    print('Missing values in projects data imputed. See preprocess.py for details.')

    util.fix_bool(outcomes, ['is_exciting',
                         'fully_funded',
                         'at_least_1_teacher_referred_donor',
                         'at_least_1_green_donation', 'great_chat',
                         'three_or_more_non_teacher_referred_donors',
                         'one_non_teacher_referred_donor_giving_100_plus',
                         'donation_from_thoughtful_donor'])
    print('Booleans in Outcomes set to 1 and 0.')

    util.fix_bool(projects, ['eligible_double_your_impact_match',
                             'eligible_almost_home_match',
                             'school_charter',
                             'school_charter_ready_promise',
                             'school_kipp',
                             'school_magnet',
                             'school_nlns',
                             'school_year_round',
                             'teacher_ny_teaching_fellow',
                             'teacher_teach_for_america'])
    print('Booleans in Projects set to 1 and 0.')

    util.discretize_many(outcomes, {'non_teacher_referred_count': 5,
                                    'teacher_referred_count': 5})
    print('Columns in outcomes successfully discretized.')

    util.discretize_many(projects, {'students_reached': [5, True],
                                    'total_price_excluding_optional_support': [5, True],
                                    'total_price_including_optional_support': [4, True]})
    print('Columns in projects successfully discretized.')


    projects = util.dummies(projects, ['grade_level',
                            'poverty_level',
                            'primary_focus_area',
                            'resource_type',
                            'school_metro'])
    print('Dummies created!')

    projects = util.dullify(projects,
                 col_val = {'school_county':['Los Angeles','Cook']})
    print('High cardinality columns fixed!')
