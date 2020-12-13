import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
  """This class represents the trivia test case"""

  def setUp(self):
    """Define test variables and initialize app."""
    self.app = create_app()
    self.client = self.app.test_client
    self.database_name = "trivia_test"
    self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
    setup_db(self.app, self.database_path)

    # dummy question for use in tests
    self.new_question = {
      'question': 'Which is the highest mountain in the world?',
      'answer': 'Mauna kia in Hawaii',
      'difficulty': 3,
      'category': '3'
    }

    # binds the app to the current context
    with self.app.app_context():
      self.db = SQLAlchemy()
      self.db.init_app(self.app)
      # create all tables
      self.db.create_all()
    
  def tearDown(self):
    """Executed after reach test"""
    pass

  def test_get_paginated_questions(self):
    """Test questions pagination success"""

    # get response and load data
    response = self.client().get('/questions')
    data = json.loads(response.data)

    # check status code and message
    self.assertEqual(response.status_code, 200)
    self.assertEqual(data['success'], True)

    # check that total_questions and questions return data
    self.assertTrue(data['total_questions'])
    self.assertTrue(len(data['questions']))

  def test_404_request_beyond_valid_page(self):
    """Test questions pagination error"""

    # send request with bad page data, load response
    response = self.client().get('/questions?page=100')
    data = json.loads(response.data)

    # check status code and message
    self.assertEqual(response.status_code, 404)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'resource not found')


# Make the tests conveniently executable
if __name__ == "__main__":
  unittest.main()