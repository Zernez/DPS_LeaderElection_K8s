import pytest

@pytest.fixture(autouse=True)
def logic_suite(monkeypatch):
    def fake_register(self, host=7071, port_id= 7070, node_id= 10001, n= 0):
        return 200
    
    def fake_start(self):     
        return 200
    
    def fake_post(self,url="localhost", json={}):  
        return 200
  
    monkeypatch.setenv('ELECTION_SERVICE_SERVICE_HOST', 'localhost')
    monkeypatch.setenv('PORT_CONFIG', '5000')
    monkeypatch.setenv('NUM_HOST', '5')
    from python.bully_logic import logic
    import requests
    monkeypatch.setitem(logic.register[0], 'ID', 10001)
    monkeypatch.setitem(logic.register[0], 'port', 7070)
    monkeypatch.setitem(logic.register[0], 'election', True)
    monkeypatch.setitem(logic.register[1], 'ID', 10002)
    monkeypatch.setitem(logic.register[1], 'port', 7071)
    monkeypatch.setitem(logic.register[1], 'election', True)
    monkeypatch.setitem(logic.register[2], 'ID', 10003)
    monkeypatch.setitem(logic.register[2], 'port', 7072)
    monkeypatch.setitem(logic.register[2], 'election', True)
    monkeypatch.setitem(logic.register[3], 'ID', 10004)
    monkeypatch.setitem(logic.register[3], 'port', 7073)
    monkeypatch.setitem(logic.register[3], 'election', True)
    monkeypatch.setitem(logic.register[4], 'ID', 10005)
    monkeypatch.setitem(logic.register[4], 'port', 7074)
    monkeypatch.setitem(logic.register[4], 'election', True)
    monkeypatch.setattr(logic,'register_service', fake_register)
    monkeypatch.setattr(logic,'start', fake_start)
    monkeypatch.setattr(requests,'post', fake_post)
    return logic

class TestEnvironment:

    def test_preamble(self, logic_suite):
        logic_element = logic_suite()
        assert logic_element.preamble() == 200

    def test_define_ports(self, logic_suite):
        logic_element = logic_suite()
        assert logic_element.define_ports() == [7070, 7071, 7072, 7073, 7074]

    def test_define_ids(self, logic_suite):
        logic_element = logic_suite()
        assert logic_element.define_ids() == [10001, 10002, 10003, 10004, 10005]

    def test_generate_node_id(self, logic_suite):
        logic_element = logic_suite()
        assert logic_element.generate_node_id() > 0

    def test_register_id(self, logic_suite):
        logic_element = logic_suite()
        assert logic_element.register_service(host=5011, port_id= 5010, node_id= 10001, n= 0) == 200

    def test_get_details(self, logic_suite):
        logic_element = logic_suite()
        assert logic_element.get_details([7070,7074]) == [{'ID': 10001, 'port': 7070,'election': True},
            {'ID': 10005, 'port': 7074,'election': True}]

    def test_get_higher_nodes(self, logic_suite):
        logic_element = logic_suite()
        assert logic_element.get_higher_nodes([{'ID': 10001, 'port': 7070,'election': True},
            {'ID': 10002, 'port': 7071,'election': True},
            {'ID': 10003, 'port': 7072,'election': True},
            {'ID': 10004, 'port': 7073,'election': True},
            {'ID': 10005, 'port': 7074,'election': True}], 10001) == [7071,7072,7073,7074]

    def test_election(self, logic_suite):
        logic_element = logic_suite()
        assert logic_element.election([5011,5012,5013,5014], 10005)== 10005
