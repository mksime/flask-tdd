import os
import unittest
import tempfile

import app

class BasicTestCase(unittest.TestCase):
    def test_index(self):
        '''Teste inicial: Assegura que o Flask foi configurado corretamente'''
        tester = app.app.test_client(self)
        response = tester.get('/', content_type = 'html/text')
        self.assertEqual(response.status_code, 200)
        
    def test_database(self):
        '''Teste inicial: assegura que a base de dados existe'''
        tester = os.path.exists('flaskr.db')
        self.assertTrue(tester)

class FlakrTestCase(unittest.TestCase):
    def setUp(self):
        '''Configura uma base de dados temporária em branco antes de cada teste'''
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        app.init_db()

    def tearDown(self):
        '''Destrói a base de dados temporária em branco depois de cada teste'''
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])
    
    def login(self, username, password):
        '''Função auxiliar para login'''
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        '''Função auxiliar para logout'''
        return self.app.get('/logout', follow_redirects=True)

    # Funções assert
    def test_empty_db(self):
        '''Assegura que o banco de dados está vazio'''
        rv = self.app.get('/')
        assert b'No entries yet. Add some!' in rv.data

    def test_login_logout(self):
        '''Testa login e logout usando as funções auxiliares'''
        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']   
        )
        assert b'You are logged in' in rv.data
        rv = self.logout()
        assert b'You are logged out' in rv.data
        rv = self.login(
            app.app.config['USERNAME'] + 'x',
            app.app.config['PASSWORD']
        )
        assert b'Invalid username' in rv.data
        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD'] + 'x'
        )
        assert b'Invalid password' in rv.data

    def test_messages(self):
        '''Assegura que um usuário possa postar mensagens'''
        self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

if __name__ == '__main__':
    unittest.main()