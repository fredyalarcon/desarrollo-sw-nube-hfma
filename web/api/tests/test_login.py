import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from flask_jwt_extended import create_access_token
from app import create_app  # Asume que tienes una función para crear tu app
from models import Usuario  # Importa tu modelo Usuario

class TestVistaLogin(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada test: configura la app y el cliente de pruebas."""
        self.app = create_app()  # Crea tu app de Flask
        self.client = self.app.test_client()  # Cliente de pruebas de Flask
        self.app.config['JWT_SECRET_KEY'] = 'super-secret'  # Clave secreta para JWT

    @patch('models.Usuario.query')  # Mockea la consulta a la base de datos
    def test_login_exitoso(self, mock_query):
        """Prueba de inicio de sesión exitoso."""
        # Configura un usuario de prueba que devolverá el mock
        usuario = MagicMock()
        usuario.id = 1
        mock_query.filter_by.return_value.first.return_value = usuario

        # Datos del usuario para la solicitud de prueba
        data = {
            "username": "testuser",
            "password": "password123"
        }

        # Realiza una solicitud POST simulada al endpoint /login
        response = self.client.post('/login', 
                                    data=json.dumps(data),
                                    content_type='application/json')

        # Verifica que la respuesta sea 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verifica que el token de acceso esté en la respuesta
        response_data = json.loads(response.data)
        self.assertIn('access_token', response_data)

    @patch('models.Usuario.query')
    def test_login_fallido(self, mock_query):
        """Prueba de inicio de sesión fallido con credenciales incorrectas."""
        # Configura el mock para que no encuentre un usuario
        mock_query.filter_by.return_value.first.return_value = None

        # Datos incorrectos del usuario
        data = {
            "username": "wronguser",
            "password": "wrongpassword"
        }

        # Realiza la solicitud POST al endpoint /login
        response = self.client.post('/login',
                                    data=json.dumps(data),
                                    content_type='application/json')

        # Verifica que la respuesta sea 402 (Nombre de usuario o contraseña incorrectos)
        self.assertEqual(response.status_code, 402)

        # Verifica el mensaje de error en la respuesta
        response_data = json.loads(response.data)
        self.assertEqual(response_data['mensaje'], 'Nombre de usuario o contraseña incorrectos')

if __name__ == '__main__':
    unittest.main()