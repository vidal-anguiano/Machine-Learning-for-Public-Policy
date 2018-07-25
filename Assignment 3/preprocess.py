from vatools.utils import data_processing as dp
from vatools.db_conn.db_conn import DBConnection
from vatools.ml import ml


if __name__ == '__main__':
    db = DBConnection('../credentials.json')
    db.connect()
    outcomes = db.query('select * from outcomes')
    projects = db.query('select * from projects')

    ''' *** PREPROCESSING, CLEANING, AND FEATURE CREATION *** '''

    # Imputing values into columns in projects as detailed in the key, value pairs.
    dp.impute(projects,
                col_meth = {'primary_focus_area': 'missing',
                            'grade_level': 'missing',
                           'resource_type': 'missing',
                           'school_metro': 'missing'})
    print('Missing values in projects data imputed. See preprocess.py for details.\n')


    # Converting boolean columns from "t/f" to 1/0
    dp.fix_bool(outcomes, ['fully_funded'])
    print('Booleans in Outcomes set to 1 and 0.\n')


    # Converting boolean columns from "t/f" to 1/0
    dp.fix_bool(projects, ['eligible_double_your_impact_match',
                             'eligible_almost_home_match',
                             'school_charter',
                             'school_charter_ready_promise',
                             'school_kipp',
                             'school_magnet',
                             'school_nlns',
                             'school_year_round',
                             'teacher_ny_teaching_fellow',
                             'teacher_teach_for_america'])
    print('Booleans in Projects set to 1 and 0 from t/f.\n')


    # Discretize columns in projects data.
    dp.discretize_many(projects, {'students_reached': 5,
                                    'total_price_excluding_optional_support': 5,
                                    'total_price_including_optional_support': 6})
    print('Columns in projects successfully discretized.\n')


    # Creating dummies for columns in projects data.
    projects = dp.dummies(projects, ['grade_level',
                            'poverty_level',
                            'primary_focus_area',
                            'resource_type',
                            'school_metro'])
    print('Dummies created!\n')


    # Creating date and time features.
    projects = dp.get_date_parts(projects, {'date_posted':['month','day_of_week','is_weekend']})


    # Reducing cardinality in projects school_county and putting rest in "other".
    projects = dp.dullify(projects,
                 col_val = {'school_county':['Los Angeles','Cook']})
    print('High cardinality columns fixed!\n')


    #Change the "positive" value from fully funded to not fully funded
    outcomes['not_fully_funded'] = outcomes['fully_funded'].apply(lambda x: 1 if x == 0 else 0)


    # Dumping cleaned data into database table
    db.create_table_from_df(outcomes,'outcomes_cleaned', override_edits = True)
    # db.create_table_from_df(projects,'projects_cleaned', sep =',')
    # Had to manually load data to database due to error
    # extra data after last expected column
    # CONTEXT:  COPY projects_cleaned, line 66351: "a3da9e50d570bbb1bb597bec77cca48d,8b210d09d18d434e440305b64bb3537e,e20cefa5a7929da97b849f4ab03bebad,,..."
    db.query('''CREATE TABLE combined_data as
                SELECT a.*,
                       b.not_fully_funded
                FROM projects_cleaned a
                JOIN outcomes_cleaned b
                ON a.projectid = b.projectid;''', False)
