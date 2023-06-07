import unittest
import datetime
import apis


class TestNextWeekday(unittest.TestCase):

    def test_monday_tuesday(self):
        monday_noon = datetime.datetime(2023, 5, 1, 12, 0, 0) # May 1 2023 is a Monday
        target_number = 1 # Tuesday
        tuesday_noon = datetime.datetime(2023, 5, 2, 12, 0, 0) # 24 hours later exactly
        self.assertEqual(apis.next_weekday(monday_noon, target_number), tuesday_noon)
        print("correct weekday")

if __name__ == '__main__':
    unittest.main()
