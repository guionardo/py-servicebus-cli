import unittest

from src.tools.sb import ServiceBusConnectionString, to_snake_case


class TestServiceBusCS(unittest.TestCase):

    def test_connection_string(self):
        connection_string = "endpoint=sb://testing.servicebus.windows.net/;" +\
            "SharedAccessKeyName=testing_key;SharedAccessKey=abcd"
        sb = ServiceBusConnectionString(connection_string)
        self.assertEqual(
            'sb://testing.servicebus.windows.net/', sb.endpoint)

    def test_invalid_connection_string(self):
        connection_string = 'invalid=true'
        with self.assertRaises(ValueError):
            ServiceBusConnectionString(connection_string)

    def test_snake_case(self):
        test_case = {
            'Endpoint': 'endpoint',
            'SharedAccessKeyName': 'shared_access_key_name',
            'SharedAccessKey': 'shared_access_key'
        }
        for key in test_case.keys():
            self.assertEqual(test_case[key], to_snake_case(key))

    def test_to_string(self):
        connection_string = "endpoint=sb://testing.servicebus.windows.net/;" +\
            "SharedAccessKeyName=testing_key;SharedAccessKey=abcd"
        sb = ServiceBusConnectionString(connection_string)
        self.assertEqual('Endpoint=sb://testing.servicebus.windows.net/;' +
                         "SharedAccessKeyName=testing_key;SharedAccessKey=abcd", sb.to_string())
