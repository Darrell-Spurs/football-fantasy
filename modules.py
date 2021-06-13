from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, NumberRange, length

class Toolbox:
    def __init__(self):
        pass

    def yesterday(self):
        from time import localtime as lt
        pre_z = lambda a: str(a).rjust(2, "0")
        months=[31,28,31,30,31,30,31,31,30,31,30,31]
        y,m,d = lt().tm_year,lt().tm_mon,lt().tm_mday-1
        [m,d] = [m-1, months[m-2]+d] if d<1 else [m, d]
        [y,m,d] = [y-1,(m+11)%12+1,d] if m<1 else [y,m,d]
        return "-".join(map(pre_z,(y,m,d)))

    def parsing_stats(self,tds,note=False):
        date = self.yesterday()
        keys = ['Name', 'Team', 'Position', 'Minutes', 'Goals', 'Assists', 'Shots',
                'Shots on Target', 'Yellow Cards','Red Cards', 'Tackles', 'Steals',
                'Total Passes', 'Pass%', 'Saves', 'Fouls Committed', 'Fouls Suffered']
        value_indexes = [0,1,2,3,4,6,12,13,7,8,15,16,17,18,20,21,22]
        r_vlaue={'Update Time': date}
        if not note:
            for i in range(len(keys)):
                r_vlaue[keys[i]] = tds[value_indexes[i]].text
        else:
            for i in range(len(keys)):
                value_indexes[i]=value_indexes[i]+1 if i>2 else value_indexes[i]
                r_vlaue[keys[i]] = tds[value_indexes[i]].text
        return r_vlaue

class LoginForm(FlaskForm):
    email = StringField("Email: ",validators=[DataRequired(message="Please enter you email"),length(max=16)])
    password = PasswordField("Password: ",validators=[DataRequired(message="Please enter you password"),length(max=16)])
    submit = SubmitField("Login")

class SignupForm(FlaskForm):
    email = StringField("Email: ",validators=[DataRequired(message="Please enter you username"),length(max=16)])
    username = StringField("Username: ", validators=[DataRequired(message="Please enter you username"), length(max=16)])
    password = PasswordField("Password: ",validators=[DataRequired(message="Please enter you password"), length(max=16)])
    fav_nation = StringField("Favorite Nation: ", validators=[length(max=40)])
    fav_club = StringField("Favorite Club: ", validators=[length(max=40)])
    submit = SubmitField("Sign Up")