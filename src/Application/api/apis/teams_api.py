from datetime import datetime 
from flask.helpers import make_response 
from flask_restx import Resource, Namespace , fields , reqparse 
from flask import jsonify, request 
from sqlalchemy import func,desc,asc 
from models import teams 
from app import db 
from utils import convert_db_model_to_restx_model 
            
teams_namespace = Namespace("teams", description="teams Api") 


teams_model =teams_namespace.model("teams",convert_db_model_to_restx_model(teams)) 
teams_id_parser = reqparse.RequestParser() 
teams_id_parser.add_argument('year',type=int)
teams_id_parser.add_argument('tmID',type=str)


@teams_namespace.route("/")
class teamsApi(Resource):

    @teams_namespace.marshal_list_with(teams_model) 
    def get(self):
        try:
            teamss = db.session.query(teams).all()
        except Exception as e:
            return None , 500
        return teamss , 200  

    @teams_namespace.marshal_with(teams_model) 
    @teams_namespace.expect(teams_model) 
    def post(self):
        try:
            teamss = teams(year = request.json.get("year"),lgID = request.json.get("lgID"),tmID = request.json.get("tmID"),franchID = request.json.get("franchID"),confID = request.json.get("confID"),divID = request.json.get("divID"),rank = request.json.get("rank"),confRank = request.json.get("confRank"),playoff = request.json.get("playoff"),name = request.json.get("name"))
            db.session.add(teamss)
            db.session.commit()    
        except Exception as e:
            return None , 500
        return teamss , 201 

    @teams_namespace.marshal_with(teams_model) 
    @teams_namespace.expect(teams_model) 
    def put(self):
        try:
            db.session.query(teams).filter(teams.year==request.json.get('year') and teams.tmID==request.json.get('tmID') ).update(request.json) 
            db.session.commit() 
            teamss = db.session.query(teams).filter(teams.year==request.json.get('year') and teams.tmID==request.json.get('tmID') ).first() 
        except Exception as e:
            return None , 500
        return teamss , 200    

    @teams_namespace.marshal_with(teams_model) 
    @teams_namespace.expect(teams_id_parser) 
    def delete(self):
        try:
            teamss = db.session.query(teams).filter(teams.year==teams_id_parser.parse_args().get('year') and teams.tmID==teams_id_parser.parse_args().get('tmID') ).first() 
            db.session.query(teams).filter(teams.year==teams_id_parser.parse_args().get('year') and teams.tmID==teams_id_parser.parse_args().get('tmID') ).delete() 
            db.session.commit() 
        except Exception as e:
            return None , 500
        return teamss , 200    

get_teams_filteredby_name_model = teams_namespace.model('get_teams_filteredby_name_model',{ 'teams.year' : fields.Integer,'teams.lgID' : fields.String,'teams.tmID' : fields.String,'teams.franchID' : fields.String,'teams.confID' : fields.String,'teams.divID' : fields.String,'teams.rank' : fields.Integer,'teams.confRank' : fields.Integer,'teams.playoff' : fields.String,'teams.name' : fields.String,'count_teams.lgID' : fields.String,'count_teams.year' : fields.Integer,'count_all' : fields.Integer })
get_teams_filteredby_name_parser = reqparse.RequestParser()
get_teams_filteredby_name_parser.add_argument('teams.name', type=str, required=True, location='args')

@teams_namespace.route('/get_teams_filteredby_name', methods=['GET'])
class get_teams_filteredby_name_resource(Resource):
    @teams_namespace.marshal_list_with(get_teams_filteredby_name_model)
    @teams_namespace.expect(get_teams_filteredby_name_parser)

    def get(self):
        args = get_teams_filteredby_name_parser.parse_args()

        results = None
        try:
            results = db.session.query(teams, func.count(teams.lgID).label('count_teams.lgID'), func.count(teams.year).label('count_teams.year'), func.count().label('count_all'))\
				.filter(teams.name == args['teams.name'])\
				.group_by(teams.franchID, teams.confRank, teams.name, teams.divID, teams.playoff, teams.confID, teams.year, teams.lgID, teams.tmID, teams.rank).all()

        except Exception as e:
            return None , 400

        return results , 200

get_teams_groupedby_lgID_model = teams_namespace.model('get_teams_groupedby_lgID_model',{ 'teams.lgID' : fields.String,'teams.name' : fields.String })
get_teams_groupedby_lgID_parser = reqparse.RequestParser()
get_teams_groupedby_lgID_parser.add_argument('is_order_of_count_of_rows_desc', type=bool, required=True, location='args')

@teams_namespace.route('/get_teams_groupedby_lgID', methods=['GET'])
class get_teams_groupedby_lgID_resource(Resource):
    @teams_namespace.marshal_list_with(get_teams_groupedby_lgID_model)
    @teams_namespace.expect(get_teams_groupedby_lgID_parser)

    def get(self):
        args = get_teams_groupedby_lgID_parser.parse_args()
        direction = desc if args['is_order_of_count_of_rows_desc'] else asc

        results = None
        try:
            results = db.session.query(teams.lgID, teams.name)\
				.group_by(teams.lgID)\
				.order_by(direction(func.count())).all()

        except Exception as e:
            return None , 400

        return results , 200

get_teams_filteredby_tmID_lgID_orderedby_franchID_model = teams_namespace.model('get_teams_filteredby_tmID_lgID_orderedby_franchID_model',{ 'teams.year' : fields.Integer,'teams.lgID' : fields.String,'teams.tmID' : fields.String,'teams.franchID' : fields.String,'teams.confID' : fields.String,'teams.divID' : fields.String,'teams.rank' : fields.Integer,'teams.confRank' : fields.Integer,'teams.playoff' : fields.String,'teams.name' : fields.String })
get_teams_filteredby_tmID_lgID_orderedby_franchID_parser = reqparse.RequestParser()
get_teams_filteredby_tmID_lgID_orderedby_franchID_parser.add_argument('is_order_of_franchID_desc', type=bool, required=True, location='args')

@teams_namespace.route('/get_teams_filteredby_tmID_lgID_orderedby_franchID', methods=['GET'])
class get_teams_filteredby_tmID_lgID_orderedby_franchID_resource(Resource):
    @teams_namespace.marshal_list_with(get_teams_filteredby_tmID_lgID_orderedby_franchID_model)
    @teams_namespace.expect(get_teams_filteredby_tmID_lgID_orderedby_franchID_parser)

    def get(self):
        args = get_teams_filteredby_tmID_lgID_orderedby_franchID_parser.parse_args()
        franchID_direction = desc if args['is_order_of_franchID_desc'] else asc

        results = None
        try:
            results = db.session.query(teams)\
				.filter(teams.lgID == teams.tmID)\
				.order_by(franchID_direction(teams.franchID)).all()

        except Exception as e:
            return None , 400

        return results , 200

get_teams_filteredby_lgID_model = teams_namespace.model('get_teams_filteredby_lgID_model',{ 'teams.year' : fields.Integer,'teams.lgID' : fields.String,'teams.tmID' : fields.String,'teams.franchID' : fields.String,'teams.confID' : fields.String,'teams.divID' : fields.String,'teams.rank' : fields.Integer,'teams.confRank' : fields.Integer,'teams.playoff' : fields.String,'teams.name' : fields.String,'count_teams.tmID' : fields.String,'count_all' : fields.Integer })
get_teams_filteredby_lgID_parser = reqparse.RequestParser()
get_teams_filteredby_lgID_parser.add_argument('teams.lgID', type=str, required=True, location='args')

@teams_namespace.route('/get_teams_filteredby_lgID', methods=['GET'])
class get_teams_filteredby_lgID_resource(Resource):
    @teams_namespace.marshal_list_with(get_teams_filteredby_lgID_model)
    @teams_namespace.expect(get_teams_filteredby_lgID_parser)

    def get(self):
        args = get_teams_filteredby_lgID_parser.parse_args()

        results = None
        try:
            results = db.session.query(teams, func.count(teams.tmID).label('count_teams.tmID'), func.count().label('count_all'))\
				.filter(teams.lgID == args['teams.lgID'])\
				.group_by(teams.franchID, teams.confRank, teams.name, teams.divID, teams.playoff, teams.confID, teams.year, teams.lgID, teams.tmID, teams.rank).all()

        except Exception as e:
            return None , 400

        return results , 200

