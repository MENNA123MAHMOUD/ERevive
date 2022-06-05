from flask.helpers import make_response 
from flask_restx import Resource, Namespace , fields , reqparse 
from flask import jsonify, request 
from sqlalchemy import func,desc,asc 
from models import player_allstar 
from app import db 
from utils import convert_db_model_to_restx_model 
            
player_allstar_namespace = Namespace("player_allstar", description="player_allstar Api") 


player_allstar_model =player_allstar_namespace.model("player_allstar",convert_db_model_to_restx_model(player_allstar)) 
player_allstar_id_parser = reqparse.RequestParser() 
player_allstar_id_parser.add_argument('playerID',type=str)


@player_allstar_namespace.route("/")
class player_allstarApi(Resource):

    @player_allstar_namespace.marshal_list_with(player_allstar_model) 
    def get(self):
        player_allstars = db.session.query(player_allstar).all()
        return player_allstars , 200  

    @player_allstar_namespace.marshal_with(player_allstar_model) 
    @player_allstar_namespace.expect(player_allstar_model) 
    def post(self):
        player_allstar = player_allstar(playerID = request.json.get("playerID"),last_name = request.json.get("last_name"),first_name = request.json.get("first_name"),season_id = request.json.get("season_id"),conference = request.json.get("conference"),league_id = request.json.get("league_id"),games_played = request.json.get("games_played"),minutes = request.json.get("minutes"),points = request.json.get("points"),o_rebounds = request.json.get("o_rebounds"),d_rebounds = request.json.get("d_rebounds"),rebounds = request.json.get("rebounds"),assists = request.json.get("assists"),steals = request.json.get("steals"),blocks = request.json.get("blocks"),turnovers = request.json.get("turnovers"),personal_fouls = request.json.get("personal_fouls"),fg_attempted = request.json.get("fg_attempted"),fg_made = request.json.get("fg_made"),ft_attempted = request.json.get("ft_attempted"),ft_made = request.json.get("ft_made"),three_attempted = request.json.get("three_attempted"),three_made = request.json.get("three_made"))
        db.session.add(player_allstar)
        db.session.commit()    
        return player_allstar , 201 

    @player_allstar_namespace.marshal_with(player_allstar_model) 
    @player_allstar_namespace.expect(player_allstar_model) 
    def put(self):
        db.session.query(player_allstar).filter(player_allstar.id==id).update(request.json) 
        db.session.commit() 
        player_allstar = db.session.query(player_allstar).filter(player_allstar.id==id).first() 
        return player_allstar , 200    

    @player_allstar_namespace.marshal_with(player_allstar_model) 
    @player_allstar_namespace.expect(player_allstar_id_parser) 
    def delete(self):
        player_allstar = db.session.query(player_allstar).filter(player_allstar.id==id).first() 
        db.session.query(player_allstar).filter(player_allstar.id==id).delete() 
        db.session.commit() 
        return player_allstar , 200    
