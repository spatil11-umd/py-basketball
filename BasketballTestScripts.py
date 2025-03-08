"""
Name: Siddharth Patil
Directory ID: spatil11@terpmail.umd.edu
Date: 2024-14-24
Exercise: Final Proposal
"""

import unittest
from unittest import mock
from finalproposal import BasketballStats 
import csv

class TestBasketballStats(unittest.TestCase):
    def test_find_high_low_stat(self):
        # Initialize the BasketballStats object with test data
        test_data = [
            {"Name": "Greg Heffley", "Points": 20.0, "Assists": 5.0, "Rebounds": 10.0, "FG%": 45.0, "3PT%": 35.0},
            {"Name": "Rowley Jefferson", "Points": 30.0, "Assists": 7.0, "Rebounds": 8.0, "FG%": 50.0, "3PT%": 40.0},
            {"Name": "Rodrick Heffley", "Points": 15.0, "Assists": 4.0, "Rebounds": 12.0, "FG%": 40.0, "3PT%": 30.0},
        ]

        # Create an instance of BasketballStats with a mock file
        basketball_stats = BasketballStats("basketball_data.csv")
        basketball_stats.load_data = mock.MagicMock(return_value=None)
        basketball_stats.data = test_data

        # Define the expected results
        expected_high = {
            "Points": 30.0,
            "Assists": 7.0,
            "Rebounds": 12.0,
            "FG%": 50.0,
            "3PT%": 40.0
        }
        expected_low = {
            "Points": 15.0,
            "Assists": 4.0,
            "Rebounds": 8.0,
            "FG%": 40.0,
            "3PT%": 30.0
        }

        def find_high_stat(stats):
            high_stats = {}
            for key in stats[0].keys():
                if key != "Name":
                    high_stats[key] = max(player[key] for player in stats)
            return high_stats

        def find_low_stat(stats):
            low_stats = {}
            for key in stats[0].keys():
                if key != "Name":
                    low_stats[key] = min(player[key] for player in stats)
            return low_stats

        # Calculate high and low stats
        high_stats = find_high_stat(test_data)
        low_stats = find_low_stat(test_data)

        # Assert that the results match expected outcomes
        self.assertEqual(high_stats, expected_high)
        self.assertEqual(low_stats, expected_low)

if __name__ == '__main__':
    unittest.main()
