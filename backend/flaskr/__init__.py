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
        'categories': mappedCategories
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
        'questions': currentQuestionsPage,
        'total_questions': questionsCount,
        'categories': mappedCategories
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

  @app.route('/questions', methods=['POST'])
    def post_question():
      '''
      Create new question and search questions endpoint.
      '''
      body = request.get_json()

      # if search term is present
      if (body.get('searchTerm')):
        searchTerm = body.get('searchTerm')

        # query the database using search term
        selection = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()

        # 404 if no results found
        if (len(selection) == 0):
          abort(404)

        # paginate the results
        paginated = paginate_questions(request, selection)

        # return results
        return jsonify({
          'success': True,
          'questions': paginated,
          'total_questions': len(Question.query.all())
        })
      # if no search term, create new question
      else:
        # load input from body
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        # validate that all inputs have data
        if ((new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None)):
          abort(422)

        try:
          # create and insert new record
          question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
          question.insert()

          # query all questions and paginate
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)

          return jsonify({
            'success': True,
            'created': question.id,
            'question_created': question.question,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
          })

        except:
          # abort with unprocessable entity response
          abort(422)

  @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
      '''
      Getting questions by category endpoint.
      '''

      # get the category by id
      category = Category.query.filter_by(id=id).one_or_none()

      if (category is None):
        abort(400)

      # get the matching questions
      selection = Question.query.filter_by(category=category.id).all()

      # paginate the selection
      paginated = paginate_questions(request, selection)

      # return the results
      return jsonify({
        'success': True,
        'questions': paginated,
        'total_questions': len(Question.query.all()),
        'current_category': category.type
      })

      
  @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():
      '''
      Playing quiz endpoint.
      '''

      body = request.get_json()
      previous = body.get('previous_questions')
      category = body.get('quiz_category')

      if ((category is None) or (previous is None)):
        abort(400)

      if (category['id'] == 0):
        questions = Question.query.all()
      else:
        questions = Question.query.filter_by(category=category['id']).all()

      total = len(questions)

      # query a random question
      def get_random_question():
        return questions[random.randrange(0, len(questions), 1)]

      # checks to see if a question was used
      def check_if_used(question):
        used = False
        for q in previous:
          if (q == question.id):
            used = True

        return used

      # get random question
      question = get_random_question()

      # check if used, execute until unused question found
      while (check_if_used(question)):
        question = get_random_question()

        # if all questions have been displayed, return without question
        # required in case category has more than five questions
        if (len(previous) == total):
          return jsonify({
            'success': True
          })

      # return the question
      return jsonify({
        'success': True,
        'question': question.format()
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    