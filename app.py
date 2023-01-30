from model import *
from forms import*
from sqlalchemy import or_
from datetime import datetime

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/home')
def home(sort_col=""):
    todo_list=Todo.query.all()
    return render_template('home.html', todo_list=todo_list)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    detail = request.form.get('detail')
    deadline = datetime.strptime(request.form.get('deadline'),'%Y-%m-%d')
    new_task = Todo(name=name, detail=detail, deadline=deadline, done=False)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo = Todo.query.get(todo_id)
    todo.done=not todo.done
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("tag", type=str)
    keyword = "%{}%".format(query)
    todo_list = Todo.query.filter(or_(Todo.name.like(keyword),Todo.task_id.like(keyword))).all()
    return render_template("search.html", query=query, todo_list=todo_list)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route('/sort/<string:sort_col>', methods=['Get', 'POST'])
def sort(sort_col):
    if (sort_col == "deadline"):
        col = Todo.deadline
    if (sort_col == "status"):
        col = Todo.done
    todo_list = Todo.query.order_by(col)
    return render_template('search.html', query=sort_col, todo_list=todo_list)

if __name__ == '__main__':
    app.run(debug=True)
