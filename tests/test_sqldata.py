import os
import opticalconstants as oc
# import matplotlib.pyplot as plt


def test_read_in():
    label = 'a_ol_Jager03_mg1.0_fe0.0'
    oc1 = oc.OpticalConstants(label=label)
    print(oc1.label)
    print(oc1.info)
    assert oc1 is not None and len(oc1.wavelength) != 0


def test_read_in_2():
    label = 'a_ol_Jager03_mg1.0_fe0.0'
    oc1 = oc.OpticalConstants()
    oc1.label=label
    oc1.search()
    print(oc1.label)
    print(oc1.info)
    assert len(oc1.wavelength) != 0

def test_read_in_3():
    label = 'a_ol_Jager03_mg1.0_fe0.0'
    oc1 = oc.OpticalConstants()
    oc1.label=label
    oc1.search()
    print(oc1.doi)
    print (oc1.getColumnInTable("doi"))
    print (oc1.getColumnInTable("u_rho"))
    print (oc1.getColumnInTable("u_temperature"))
    print (oc1.getColumnInTable("label"))
    assert oc1.doi and oc1.u_rho and oc1.u_temperature

def test_external_db():
    db = os.path.join("tests", "data","TEST_EXTERNAL_DB.db")
    label = 'a_ol_Jager03_mg1.0_fe0.0'
    try:
        oc1 = oc.OpticalConstants(SQLITE_NK_DB_FILE_PATH=db)
        oc1.label=label
        oc1.search()

        worked= (len(oc1.wavelength) != 0)
    except:
        worked=False

    assert worked

# NEEDS IMPLEMENTING
def test_db_does_not_exist():
    db="unknown.db"
    try:
        oc1 = oc.OpticalConstants(SQLITE_NK_DB_FILE_PATH=db)
        oc1.label=label
        oc1.search()

        worked= (len(oc1.wavelength) != 0)
    except:
        worked=False

    assert False

def db_force_generation_new_db_file():
    assert False