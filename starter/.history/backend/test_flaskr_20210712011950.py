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

        self.new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 3,
            'category': 3
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #___________________Test for TODO 3____________________
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    #___________________Test for TODO 3 for expected error____________________
    def test_404_get_category_non_existing(self):
        res = self.client().get('/categories/20')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #___________________Test for TODO 4____________________   
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_questions'])

    #___________________Test for TODO 4 for expected error____________________
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #___________________Test for TODO 5___________________    
    def test_delete_question(self):
        question = Question(question='test question', answer='test answer',
                            difficulty=3, category=3)
        question.insert()
        question_id = question.id
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        
        question = Question.query.filter(Question.id == question.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    #___________________Test for TODO 5 for expected error____________________
    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable') 

    #___________________Test for TODO 6___________________   
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    #___________________Test for TODO 6 for expected error____________________
    def test_422_if_question_creation_not_allowed(self):
        new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 5
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    #___________________Test for TODO 7___________________
    def test_search_questions(self):
        res = self.client().post('/questions/search', json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    #___________________Test for TODO 7 for expected error____________________
    def test_404_search_question(self):
        res = self.client().post('/questions/search', json={"searchTerm": ""})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
        
    #___________________Test for TODO 8___________________
    def test_get_questions_based_on_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    #___________________Test for TODO 8 for expected error____________________
    def test_404_get_questions_based_on_category(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    #___________________Test for TODO 9___________________
    def test_quiz(self):
        previous_questions = [13, 14]
        res = self.client().post("/quizzes", json={"quiz_category": 3, "previous_questions": ([1, 2])})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['id'] not in previous_questions)
   
    #___________________Test for TODO 9 for expected error____________________
    
    




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()