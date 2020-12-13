import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  # Set up CORS. Allow '*' for origins.
  CORS(app, resources={'/': {'origins': '*'}})
  
  # Use the after_request decorator to set Access-Control-Allow
  @app.after_request
    def after_request(response):
      #Sets access control.
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
      return response
      
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
    def get_categories():
      # query all categories from db and map them dict
      categories = Category.query.all()
      mappedCategories = {}
      for category in categories:
        mappedCategories[category.id] = category.type

      # abort with 404 response if no categories were found
      if (len(mappedCategories) == 0):
        abort(404)

      return jsonify({
        'success': True,
        'data': {
          'categories': mappedCategories
        }
      })

  @app.route('/questions')
    def get_questions():
      '''
      Querying all questions endpoint.
      '''

      # query all questions and paginate
      questions = Question.query.all()
      questionsCount = len(questions)
      currentQuestionsPage = paginate_questions(request, questions)

      # query all categories and add to dict
      categories = Category.query.all()
      mappedCategories = {}
      for category in categories:
        mappedCategories[category.id] = category.type

      # abort 404 if no questions were found
      if (len(currentQuestionsPage) == 0):
        abort(404)

      return jsonify({
        'success': True,
        'data': {
          'questions': currentQuestionsPage,
          'total_questions': questionsCount,
          'categories': mappedCategories
        }
      })

  @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
      '''
      Delete a question by id endpoint.
      '''
      try:
        question = Question.query.filter_by(id=id).one_or_none()
        if question is None:
          abort(404)
        question.delete()
        return jsonify({
          'success': True,
          'deleted': id
        })

      except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    