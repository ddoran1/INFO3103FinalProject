#!/usr/bin/env python3

from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import Resource, Api, reqparse
from flask_session.__init__ import Session
import pymysql.cursors
import json

from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *

import cgitb
import cgi
import sys
cgitb.enable()

import settings #stored in settings.py
import ssl

app = Flask(__name__, static_folder='static', static_url_path='/static')

app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST

api = Api(app)

Session(app)

###############################################################################
#Error handlers
#

@app.errorhandler(400)
def not_found(error):
	return make_response(jsonify( { "status": "Bad request" } ), 400)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify( {"status": "File not found" }), 404)

@app.errorhandler(403)
def not_found(error):
	return make_response(jsonify( { "status": "Username already being used" } ), 403)

###############################################################################
#			static endpoints (for humans)
#

class Root(Resource):
	def get(self):
		return app.send_static_file('./index.html')

class SignUp(Resource):
	def post(self):
		if not request.json:
			abort(400)
		parser = reqparse.RequestParser()
		try:
			parser.add_argument('Username', type=str, required=True)
			parser.add_argument('Password', type=str, required=True)
			parser.add_argument('Email', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		#if they are logged in...
		if request_params['Username'] in session:
			response= {'status': 'user already logged in'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['Username'] + ', ou=People,ou=fcs,o=unb',
					password = request_params['Password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				session['Username'] = request_params['Username']
				response = {'status': 'success'}
				responseCode = 201
			except(LDAPException):
				response = {'status': 'Access denied'}
				responseCode = 403
			finally:
				ldapConnection.unbind()
						##THIS ALL WORKS UP ABOVE ^^^^^
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			Username = request.json['Username'];
			sqlArgs = (Username,)
			cursor = dbConnection.cursor()
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchone()
			if row is None:
				sql = 'createUser'
				sqlArgs = (session['Username'], request_params['Email'])
				cursor.callproc(sql, sqlArgs)
				dbConnection.commit()
				sql = 'getUserByName'
				sqlArgs = (session['Username'],)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				uri = 'https://'+settings.APP_HOST+":"+str(settings.APP_PORT)
				uri = uri+ '/' + "users"
				uri = uri + '/'+str(row['UserID'])
				return make_response(jsonify({"uri": uri}), responseCode)
			else:
				response = {'status': 'User already exists'}
				responseCode = 400;
		except:
			responseCode = 500
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify(response), responseCode)

class SignIn(Resource):

	def post(self):
		if not request.json:
			abort(400)
		parser = reqparse.RequestParser()
		try:
			parser.add_argument('Username', type=str, required=True)
			parser.add_argument('Password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400)

		#if they are logged in...
		if 'Username' in session:
			try:
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass=pymysql.cursors.DictCursor)
				sql = 'getUserByName'
				Username = request.json['Username'];
				sqlArgs = (Username,)
				cursor = dbConnection.cursor()
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row is None:
					response = {'status': 'Username does not exist'}
					responseCode = 400
					return make_response(jsonify(response), responseCode)
				else:
					uri = 'https://'+settings.APP_HOST+":"+str(settings.APP_PORT)
					uri = uri+'users/'+str(row["UserID"])
					return make_response(jsonify({"uri":uri, "UserID": row['UserID']}), 201)
			except:
				response = {'status': 'Fail'}
				responseCode = 500
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify(response), responseCode)
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['Username'] + ', ou=People,ou=fcs,o=unb',
					password = request_params['Password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				session['Username'] = request_params['Username']
			except(LDAPException):
				response = {'status': 'Access denied'}
				responseCode = 403
				return make_response(jsonify(response), responseCode)
			finally:
				ldapConnection.unbind()

		##THIS ALL WORKS UP ABOVE ^^^^^
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor)
			sql = 'getUserByName'
			Username = request.json['Username'];
			sqlArgs = (Username,)
			cursor = dbConnection.cursor()
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchone()
			if row is None:
				response = {'status': 'Username does not exist'}
				responseCode = 400
				return make_response(jsonify(response), responseCode)
			else:
				uri = 'https://'+settings.APP_HOST+":"+str(settings.APP_PORT)
				uri = uri+'users/'+str(row["UserID"])
				return make_response(jsonify({"uri":uri}), 201)
		except:
			response = {'status': 'Fail'}
			responseCode = 500
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify(response), responseCode)

	def get(self):
		if 'Username' in session:
			response = {'status': 'success'}
			responseCode = 200
			return make_response(jsonify(response), responseCode)
		else:
			return app.send_static_file('./index.html')

	def delete(self):
		successCode = 401
		success = False
		if 'Username' in session:
			success = True
			successCode = 200
			session.clear()
		else:
			return make_response(jsonify({"status": success}), successCode)

class Users(Resource):
	def get(self):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass = pymysql.cursors.DictCursor)
			sql = 'getUsers'
			cursor = dbConnection.cursor()
			cursor.callproc(sql)
			rows = cursor.fetchall()
		except:
			abort(403)	#access is forbidden
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({'users': rows}), 200)

class User(Resource):
	def get(self, userID):
		userID = request.json['userID'];
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
			sql='getUserByID'
			cursor = dbConnection.cursor()
			sqlArgs = (userID,)
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchone()
			if row is None:
				return make_response(jsonify({"status": "fail"}), 400)
		except:
			abort(503)
		finally:
			cursor.close()
			dbConnection.close()

		return make_response(jsonify({"user": row}), 201)

	def delete(self, userID):
		if 'Username' in session:
			userID = request.json['userID'];
			try:
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserByName'
				cursor = dbConnection.cursor()
				sqlArgs = (session['Username'],)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row == None:
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if (str(userID) != str(row['UserID'])):
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				sql = 'deleteUser'
				cursor = dbConnection.cursor()
				sqlArgs = (userID, )
				cursor.callproc(sql, sqlArgs)
				dbConnection.commit()
			except:
				abort(503)
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({ "status": "Deletion successful" }), 200)
		else:
			return make_response(jsonify({ "status": "Who are you?"}), 401)


class Lists(Resource):
	def get(self, userID):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor)
			sql = 'getLists'
			sqlArgs = (userID,)
			cursor = dbConnection.cursor()
			cursor.callproc(sql, sqlArgs)
			rows = cursor.fetchall()
			if rows is None:
				success = 404
			else:
				success = 200
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close
		return make_response(jsonify({'lists': rows}), success)

	def post(self, userID):
		if 'Username' in session:
			if not request.json:
				abort(400)
			userID = request.json['userID']
			title = request.json['title']
			descr = request.json['descr']
			try:
				dbConnection = pymysql.connect(settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserByName'
				cursor = dbConnection.cursor()
				sqlArgs = (session['Username'],)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row == None:
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if (str(userID) != str(row['UserID'])):
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				sql = 'postList'
				cursor = dbConnection.cursor()
				sqlArgs = (userID, title, descr)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				dbConnection.commit()
				sql = 'getLastList'
				cursor = dbConnection.cursor()
				sqlArgs = (userID,)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				dbConnection.commit()
			except:
				abort(503)
			finally:
				cursor.close()
				dbConnection.close()
			uri = 'https://'+settings.APP_HOST+':'+str(settings.APP_PORT)
			uri = uri + '/' + 'users' + '/' + str(userID)+ '/' + 'lists' +'/'+str(row['ListID'])
			return make_response(jsonify( { "uri": uri } ), 201)
		else:
			return make_response(jsonify( { "status": "Who are you?"}), 401)

class List(Resource):
	def get(self, userID, listID):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset = 'utf8mb4',
				cursorclass = pymysql.cursors.DictCursor)
			sql = 'getListByID'
			cursor = dbConnection.cursor()
			sqlArgs = (listID,)
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchone()
			if row is None:
				return make_response(jsonify({"status": "List is empty"}), 200)
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"list": row}), 200)

#Update list name
	def put(self, userID, listID):
		if 'Username' in session:
			userID = request.json['userID']
			listID = request.json['listID']
			title = request.json['lstName']
			description = request.json['description']
			try:
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass = pymysql.cursors.DictCursor)
				sql = 'getUserByName'
				cursor = dbConnection.cursor()
				sqlArgs = (session['Username'],)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row == None:
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if (str(userID) != str(row['UserID'])):
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if title != "":
					sql = 'updateListName'
					cursor = dbConnection.cursor()
					sqlArgs = (listID, userID, title, )
					cursor.callproc(sql, sqlArgs)
					dbConnection.commit()
				if description != "":
					sql = 'changeListDescription'
					cursor = dbConnection.cursor()
					sqlArgs = (description, listID, userID)
					cursor.callproc(sql, sqlArgs)
					dbConnection.commit()
			except:
				abort(503)
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({ "status": "Update successful" }), 200)
		else:
			return make_response(jsonify({ "status": "Who are you?"}), 401)

	def delete(self, userID, listID):
		if 'Username' in session:
			try:
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass = pymysql.cursors.DictCursor)
				sql = 'getUserByName'
				cursor = dbConnection.cursor()
				sqlArgs = (session['Username'],)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row == None:
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if (str(userID) != str(row['UserID'])):
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				sql = 'deleteList'
				cursor = dbConnection.cursor()
				sqlArgs = (listID, userID,)
				cursor.callproc(sql, sqlArgs)
				dbConnection.commit()
			except:
				abort(503)
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({ "status": "Deletion successful" }), 200)
		else:
			return make_response(jsonify({ "status": "Who are you?"}), 401)

class Tasks(Resource):
	def post(self, userID, listID):
		if 'Username' in session:
			if not request.json:
				abort(400)
			task = request.json['task']
			try:
				dbConnection = pymysql.connect(settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass= pymysql.cursors.DictCursor)
				sql = 'getUserByName'
				cursor = dbConnection.cursor()
				sqlArgs = (session['Username'],)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row == None:
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if (str(userID) != str(row['UserID'])):
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				sql = 'createTask'
				cursor = dbConnection.cursor()
				sqlArgs = (userID, listID, task)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				dbConnection.commit()
				sql = 'getLastTask'
				cursor = dbConnection.cursor()
				sqlArgs = (listID,)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				dbConnection.commit()
			except:
				abort(503)
			finally:
				cursor.close()
				dbConnection.close()
			uri = 'https://'+settings.APP_HOST+':'+str(settings.APP_PORT)
			uri = uri + '/' + 'users' + '/' + str(userID)+ '/' + 'lists' +'/'+ str(listID) + '/'+'tasks'+ '/' + str(row['TaskID'])
			return make_response(jsonify( { "uri": uri } ), 201)
		else:
			return make_response(jsonify({ "status": "Who are you?"}), 401)

	def get(self, userID, listID):
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset = 'utf8mb4',
				cursorclass = pymysql.cursors.DictCursor)
			sql = 'getListByID'
			sqlArgs = (listID,)
			cursor = dbConnection.cursor()
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchall()
			if row is None:
				return make_response(jsonify({"status": "List does not exist"}), 400)
			else:
				sql = 'getTasksByListID'
				sqlArgs = (listID,)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchall()
				if row is None:
					return make_response(jsonify({"status": "List is empty"}), 200)
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"Tasks": row}), 200)

class Task(Resource):

	def get(self, userID, listID, taskID):
		listID = request.json['listID']
		taskID = request.json['taskID']
		try:
			dbConnection = pymysql.connect(
				settings.DB_HOST,
				settings.DB_USER,
				settings.DB_PASSWD,
				settings.DB_DATABASE,
				charset = 'utf8mb4',
				cursorclass = pymysql.cursors.DictCursor)
			sql = 'getTasksByID'
			cursor = dbConnection.cursor()
			sqlArgs = (listID, taskID, )
			cursor.callproc(sql, sqlArgs)
			row = cursor.fetchall()
			if row is None:
				return make_response(jsonify({"status": "Task does not exist"}), 400)
		except:
			abort(500)
		finally:
			cursor.close()
			dbConnection.close()
		return make_response(jsonify({"Task": row}), 200)

	def put(self, userID, listID, taskID):
		if 'Username' in session:
			if not request.json:
				abort(400)
			taskIn = request.json['taskIn']
			bool = request.json['bool']
			try:
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass = pymysql.cursors.DictCursor)
				sql = 'getUserByName'
				cursor = dbConnection.cursor()
				sqlArgs = (session['Username'],)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row == None:
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if (str(userID) != str(row['UserID'])):
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if taskIn != "":
					sql = 'updateTask'
					cursor = dbConnection.cursor()
					sqlArgs = (userID,listID, taskID, taskIn)
					cursor.callproc(sql, sqlArgs)
					dbConnection.commit()
				sql = 'updateTaskCompleteness'
				cursor = dbConnection.cursor()
				sqlArgs = (userID, listID, taskID, bool)
				cursor.callproc(sql, sqlArgs)
				dbConnection.commit()
			except:
				abort(503)
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({ "status": "Update successful" }), 200)
		else:
			return make_response(jsonify({ "status": "Who are you?"}), 401)

	def delete(self, userID, listID, taskID):
		if 'Username' in session:
			try:
				dbConnection = pymysql.connect(
					settings.DB_HOST,
					settings.DB_USER,
					settings.DB_PASSWD,
					settings.DB_DATABASE,
					charset='utf8mb4',
					cursorclass = pymysql.cursors.DictCursor)
				sql = 'getUserByName'
				cursor = dbConnection.cursor()
				sqlArgs = (session['Username'],)
				cursor.callproc(sql, sqlArgs)
				row = cursor.fetchone()
				if row == None:
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				if (str(userID) != str(row['UserID'])):
					return make_response(jsonify({ "status": "Who are you?"}), 401)
				sql = 'deleteTask'
				cursor = dbConnection.cursor()
				sqlArgs = (listID, taskID,)
				cursor.callproc(sql, sqlArgs)
				dbConnection.commit()
			except:
				abort(503)
			finally:
				cursor.close()
				dbConnection.close()
			return make_response(jsonify({ "status": "Deletion successful" }), 200)
		else:
			return make_response(jsonify({ "status": "Who are you?"}), 401)

###############################################################################
#			Adding resources
#
api.add_resource(Root,'/')
api.add_resource(SignUp, '/signup')
api.add_resource(SignIn, '/signin')
api.add_resource(Users, '/users')
api.add_resource(User, '/users/<string:userID>')
api.add_resource(Lists, '/users/<string:userID>/lists')
api.add_resource(List, '/users/<string:userID>/lists/<int:listID>')
api.add_resource(Tasks, '/users/<string:userID>/lists/<int:listID>/tasks')
api.add_resource(Task, '/users/<string:userID>/lists/<int:listID>/tasks/<int:taskID>')


###############################################################################
#			Starting
#

if __name__ == "__main__":
	context = ('./certs/cert.pem', './certs/key.pem')
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		ssl_context=context,
		debug=settings.APP_DEBUG
	)
