import unittest

class TestExample(unittest.TestCase):

    def test_example_for_adam(self):
        # Arrange
        a = 2
        # Act
        b = a ** 2
        # Assert
        self.assertEqual(b, 4)
