import csv
import json
import unittest
import gra


def csv_count_rows():
    with open(gra.csv_file, newline='', encoding='utf-8') as csvfile:
        movies = csv.reader(csvfile, delimiter=';')
        return sum(1 for _ in movies) - 1


def db_count_rows():
    row = gra.query_db('select count(*) as total from award', one=True)
    return row['total']


def csv_producer_by_title(title):
    with open(gra.csv_file, newline='', encoding='utf-8') as csvfile:
        movies = csv.reader(csvfile, delimiter=';')
        next(movies)
        for year, title_csv, studios, producers, winner in movies:
            if title in title_csv:
                return producers
        return None


def db_producer_by_title(title):
    row = gra.query_db("""select group_concat(name) as producers from award inner join producer
                       on award.id = producer.award_id where title like ?""", ('%' + title + '%',), one=True)
    return row['producers']


class TestGra(unittest.TestCase):

    def test_data(self):
        self.assertEqual(csv_count_rows(), db_count_rows())
        self.assertIn('Cavallo', db_producer_by_title('Under the Cherry Moon'))
        self.assertIn('Cavallo', csv_producer_by_title('Under the Cherry Moon'))
        self.assertIn('Barrymore', db_producer_by_title(r"Charlie's Angels: Full Throttle"))
        self.assertIn('Barrymore', csv_producer_by_title(r"Charlie's Angels: Full Throttle"))
        self.assertIn('Weintraub', db_producer_by_title('The Specialist'))
        self.assertIn('Weintraub', csv_producer_by_title('The Specialist'))

    def test_api(self):
        self.assertIn('Wild Wild West', gra.awards_year(1999))
        self.assertIn('Big Daddy', gra.awards_year(1999))
        self.assertIn('Paul Blart', gra.awards_producer('Adam Sandler'))
        self.assertIn('Big Daddy', gra.awards_producer('Jack Giarraputo'))
        self.assertIn('Color of Night', gra.awards_winner(1994))
        self.assertIn('1994', gra.awards_winner(1994))
        self.assertIn('Color of Night', gra.awards_winners())
        self.assertIn('1980', gra.awards_winners())
        self.assertIn('2017', gra.awards_winners())
        self.assertIn('Friday the 13th', gra.awards_studio('paramount pictures'))
        self.assertIn('Pinocchio', gra.awards_studio('Miramax Films'))
        self.assertIn('Matthew Vaughn', gra.min_max())
        self.assertIn('Joel Silver', gra.min_max())


if __name__ == '__main__':
    unittest.main()
