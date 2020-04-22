"""Module for testing B24QueryBuilder class"""
import json
from unittest import TestCase
import unittest

import sys

sys.path.append('../')
from b24_interface.query_builder import B24QueryBuilder


class Test1(TestCase):
    """Class for testing"""

    with open("../resources/test1_result.json", 'r', encoding='utf-8') as fh:
        test1_result = json.load(fh)

    with open("../resources/test2_result.json", 'r', encoding='utf-8') as fh:
        test2_result = json.load(fh)

    def test_add_b24_product(self):
        """test case for event_checker method"""
        product_data = B24QueryBuilder.add_b24_product(
            "Test", 100, "https://bedrosova.ru/upload/test1.png", 111)

        self.assertEqual(product_data, self.test1_result)

    def test_update_b24_product(self):
        """test case for event_checker method"""
        product_data = B24QueryBuilder.update_b24_product(726, "Test", 100, "https://bedrosova.ru/upload/test1.png", 111)

        self.assertEqual(product_data, self.test2_result)


    

    

if __name__ == '__main__':
    unittest.main()
