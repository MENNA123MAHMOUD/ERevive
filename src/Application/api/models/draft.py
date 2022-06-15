from app import db 

class draft(db.Model):
	__tablename__ = "draft"
	id = db.Column(db.String(300),unique=True,primary_key=True)
	draftYear = db.Column(db.Integer,db.ForeignKey('teams.year',onupdate='CASCADE',ondelete='CASCADE'))
	draftRound = db.Column(db.String(300))
	draftSelection = db.Column(db.String(300))
	draftOverall = db.Column(db.DateTime)
	tmID = db.Column(db.String(300),db.ForeignKey('teams.tmID',onupdate='CASCADE',ondelete='CASCADE'))
	firstName = db.Column(db.String(300))
	lastName = db.Column(db.String(300))
	suffixName = db.Column(db.String(300))
	playerID = db.Column(db.String(300))
	draftForm = db.Column(db.String(300))
	lgID = db.Column(db.String(300))

	def serialize(self):
		return{
			"id": self.id,
			"draftYear": self.draftYear,
			"draftRound": self.draftRound,
			"draftSelection": self.draftSelection,
			"draftOverall": self.draftOverall,
			"tmID": self.tmID,
			"firstName": self.firstName,
			"lastName": self.lastName,
			"suffixName": self.suffixName,
			"playerID": self.playerID,
			"draftForm": self.draftForm,
			"lgID": self.lgID,
		}
