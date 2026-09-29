from streamlit.testing.v1 import AppTest
import bfup_ex3 as core


def test_course_values():
    r = core.ex3_compute()
    assert abs(r["d_eff"] - 2449) < 2
    assert abs(r["omega"] - 0.26) < 0.005
    assert abs(r["x"] - 573) < 5
    assert abs(r["a0"] - 4400) < 20
    assert abs(r["V_Rcd"] - 464) < 5 and abs(r["V_Rcd45"] - 609) < 5
    assert abs(r["x_U"] - 44) < 1
    assert abs(r["m_UR"] - 116) < 1.5
    assert abs(r["V_RUd"] - 387) < 5
    assert abs(r["V_Rd"] - 1881) < 5 and r["ok"]


def test_app_runs():
    at = AppTest.from_file("app.py", default_timeout=90).run()
    assert not at.exception
    for opt in at.selectbox[0].options:
        at.selectbox[0].set_value(opt).run()
        assert not at.exception, opt
    at.checkbox[0].check().run()
    assert not at.exception
