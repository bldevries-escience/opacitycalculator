import opticalconstants as oc
# import matplotlib.pyplot as plt


def test_read_in():
    label = 'a_ol_Jager94_mg0.5_fe0.5'
    oc1 = oc.OpticalConstants(label=label)
    print(oc1.label)
    print(oc1.info)
    assert oc1 is not None and len(oc1.wavelength) != 0


def test_read_in_2():
    label = 'a_ol_Jager94_mg0.5_fe0.5'
    oc1 = oc.OpticalConstants()
    oc1.label=label
    oc1.search()
    print(oc1.label)
    print(oc1.info)
    assert len(oc1.wavelength) != 0