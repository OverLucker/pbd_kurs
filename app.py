from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, g, session
from flask.views import View

from database import User, Event

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()


class LoginView(View):
    def dispatch_request(self):
        username = ''
        password = ''
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.login(username, password)
            if user is not None:
                session['username'] = username
                Event(
                    type=Event.EventType.LOGIN,
                    sender=username,
                    date_register=datetime.now()
                ).save()
                return redirect(url_for('event_view'))

        return render_template('login.html', username=username, password=password)


class LogoutView(View):
    def dispatch_request(self):
        username = session.pop('username', None)
        if username:
            Event(
                type=Event.EventType.LOGOUT,
                sender=username,
                date_register=datetime.now()
            ).save()
        return redirect(url_for('login_view'))


class EventListView(View):
    decorators = []

    def dispatch_request(self):
        username = session.get('username', None)
        if username is None:
            return redirect(url_for('login_view'))

        user = User.get_by_username(username)

        return render_template('event_list.html', events=Event.all(limit=20))


class TakePostView(View):
    def dispatch_request(self):
        username = session.get('username', None)
        if username is None:
            return redirect(url_for('login_view'))

        user = User.get_by_username(username)

        return redirect(url_for('event_view'))


class AwayPostView(View):
    def dispatch_request(self):
        username = session.get('username', None)
        if username is None:
            return redirect(url_for('login_view'))

        user = User.get_by_username(username)
        return redirect(url_for('event_view'))


class CreateEventView(View):
    def dispatch_request(self):
        username = session.get('username', None)
        if username is None:
            return redirect(url_for('login_view'))

        user = User.get_by_username(username)
        if request.method == "POST":
            type = request.form.get('type')
            date_register = request.form.get('date_register')
            comment = request.form.get('comment')

            Event(
                type=type,
                sender=username,
                date_register=date_register,
                comment=comment
            ).save()

            return redirect(url_for('event_view'))

        return render_template('event_add.html', event_types=Event.Type)


class CreateReportView(View):
    def dispatch_request(self):
        username = session.get('username', None)
        if username is None:
            return redirect(url_for('login_view'))

        user = User.get_by_username(username)

        return redirect(url_for('event_view'))


app.add_url_rule('/login', view_func=LoginView.as_view('login_view'), methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=LogoutView.as_view('logout_view'))
app.add_url_rule('/take', view_func=TakePostView.as_view('take_view'))
app.add_url_rule('/away', view_func=AwayPostView.as_view('away_view'))
app.add_url_rule('/new', view_func=CreateEventView.as_view('new_view'), methods=['GET', 'POST'])
app.add_url_rule('/report', view_func=CreateReportView.as_view('report_view'))
app.add_url_rule('/', view_func=EventListView.as_view('event_view'))


if __name__ == '__main__':
    app.run()
