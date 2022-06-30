from app import db 

class series_post(db.Model):
	__tablename__ = "series_post"
	id = db.Column(db.String(300),unique=True,primary_key=True)
	year = db.Column(db.Integer,db.ForeignKey('teams.year',onupdate='CASCADE',ondelete='CASCADE'))
	round = db.Column(db.String(300))
	series = db.Column(db.String(300))
	tmIDWinner = db.Column(db.String(300),db.ForeignKey('teams.tmID',onupdate='CASCADE',ondelete='CASCADE'))
	lgIDWinner = db.Column(db.String(300))
	tmIDLoser = db.Column(db.String(300),db.ForeignKey('teams.tmID',onupdate='CASCADE',ondelete='CASCADE'))
	lgIDLoser = db.Column(db.String(300))
	w = db.Column(db.String(300))
	L = db.Column(db.String(300))

	def serialize(self):
		return{
			"id": self.id,
			"year": self.year,
			"round": self.round,
			"series": self.series,
			"tmIDWinner": self.tmIDWinner,
			"lgIDWinner": self.lgIDWinner,
			"tmIDLoser": self.tmIDLoser,
			"lgIDLoser": self.lgIDLoser,
			"w": self.w,
			"L": self.L,
		}
