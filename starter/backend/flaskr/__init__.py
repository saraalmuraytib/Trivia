import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO 1: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
    #CORS(app, resources={'/': {'origins': '*'}})

  '''
  @TODO 2: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO 3:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.type).all()
    
    if len(categories) == 0:
      abort(404)

    return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}
        })
     

  '''
  @TODO 4: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    categories = Category.query.order_by(Category.type).all()

    if len(current_questions) == 0:
        abort(404)

    '''
    This endpoint should return a list of questions, 
    number of total questions, current category, categories
    '''
    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'categories': {category.id: category.type for category in categories},
        'current_category': None
    })


  '''
  @TODO 5: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(
          Question.id == question_id).one_or_none()
      if question is None:
        abort(404)

      question.delete()
      return jsonify({
          'success': True,
          'deleted': question_id
      })
    except:
      abort(422)
  '''
  @TODO 6: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    # To check if the body contain all the inforamtion that needed to create new question if not --> abort to 422 
    if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)
    
    new_question = body.get('question')
    new_answer = body.get('answer')
    new_difficulty = body.get('difficulty')
    new_category = body.get('category')
    
    try:
      question = Question(question=new_question, answer=new_answer,
                          category=new_category,difficulty=new_difficulty)
      question.insert()

      return jsonify({
        'success': True,
        'created': question.id,
      })

    except:
      abort(422)
  
  '''
  @TODO 7: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', "")

    if search_term is "":
       abort(404)

    #Using ilike helps to allows for case insensitive pattern matching
    results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

    '''
     - Returns: any array of questions,
      a number of totalQuestions that met the search term 
      and the current category string 
    '''
    return jsonify({
           'success': True,
           'questions': [question.format() for question in results],
           'total_questions': len(results),
           'current_category': None
       })
    
  '''
  @TODO 8: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_based_on_category(category_id):
     category = Category.query.filter(Category.id == category_id).one_or_none()

     if category is None:
         abort(404)
     else:
         questions = Question.query.filter(
             Question.category == str(category_id)).all()
         return jsonify({
             'success': True,
             'questions': [question.format() for question in questions],
             'total_questions': len(questions),
             'current_category': category.type
         })

  

  '''
  @TODO 9: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    '''
    - Sends a post request in order to get the next question 
    - Request Body: 
    {'previous_questions':  an array of question id's such as [1, 4, 20, 15]
    'quiz_category': a string of the current category }
    - Returns: a single new question object 
    '''
    try:
      body = request.get_json()
      quiz_category = body.get('quiz_category')
      previous_questions = body.get('previous_questions')

      if quiz_category['id'] == 0: # thats mean the category was "ALL"
          # using notin_ ---> the NOT IN operator --> to help to return not one of the previous questions
          filtered_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
      else:
          # using notin_ ---> the NOT IN operator --> to help to return not one of the previous questions
          filtered_questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()
          
      question = random.choice(filtered_questions).format() if len(filtered_questions) > 0 else None
      return jsonify({
                'success': True,
                'question': question
            })
    except:
            abort(404)


  '''
  @TODO 10: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422


  return app
