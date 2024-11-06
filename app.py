from flask import Flask, render_template, request, redirect, url_for,flash,session
import pandas as pd

app = Flask(__name__)

@app.route('/')
def main():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])  # Get the logged-in user data
    return render_template('main.html', user=user)

@app.route('/index')
def index():
    # Read Excel 
    excel_file = 'instance/Prosth-รายการวัสดุนอกเวลาที่ต้องการสั่งซื้อ.xlsx'
    df = pd.read_excel(excel_file)

    # Replace NaN values with an empty string
    df = df.fillna('')

    # Convert the DataFrame 
    DataBase = df.to_dict(orient='records')

    # Pass data to the template
    return render_template('index.html', Data=DataBase)

# Route update data
@app.route('/update_data', methods=['POST'])
def update_data():
    # Read Excel file
    excel_file = 'instance/Prosth-รายการวัสดุนอกเวลาที่ต้องการสั่งซื้อ.xlsx'
    df = pd.read_excel(excel_file)

    # Replace NaN values with empty string
    df = df.fillna('')

    # Get form data and update 
    for i, row in df.iterrows():
        df.at[i, 'Unnamed: 1'] = request.form.get(f'order_{i+1}')
        df.at[i, 'Unnamed: 2'] = request.form.get(f'item_{i+1}')
        df.at[i, 'Unnamed: 3'] = request.form.get(f'unit_{i+1}')
        df.at[i, 'Unnamed: 4'] = request.form.get(f'stock_{i+1}')
        df.at[i, 'Unnamed: 15'] = request.form.get(f'quantity_{i+1}')
        df.at[i, 'Unnamed: 13'] = request.form.get(f'category_{i+1}')  # Update category

    # Write the updated DataFrame back to the Excel file
    df.to_excel(excel_file, index=False)

    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    message = ""
    excel_file = 'instance/Prosth-รายการวัสดุนอกเวลาที่ต้องการสั่งซื้อ.xlsx'

    if request.method == 'POST':
        # Read the current Excel data
        df = pd.read_excel(excel_file)
        df = df.fillna('')  # Replace NaN with an empty string

        # Collect new material data from form fields
        new_data = {
            'Unnamed: 1': request.form['emp_id'],       # ID
            'Unnamed: 2': request.form['name'],         # Material Name
            'Unnamed: 3': request.form['position'],     # Unit
            'Unnamed: 4': request.form['hire_date'],    # Stock
            'Unnamed: 15': request.form['no'],          # Quantity
            'Unnamed: 13': request.form['category']        # Category Field
        }

        # Check if ID already exists
        if df['Unnamed: 1'].astype(str).eq(new_data['Unnamed: 1']).any():
            message = "รหัสมีอยู่แล้ว โปรดใช้รหัสอื่น."
        else:
            # Add new data to the DataFrame
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

            # Save the updated DataFrame back to the Excel file
            df.to_excel(excel_file, index=False)
            message = "ทำรายการสำเร็จ!"  # Success message in Thai

        return render_template('add.html', message=message)

    return render_template('add.html', message=message)


@app.route('/edit/<int:row_index>', methods=['GET', 'POST'])
def edit_row(row_index):
    # Read Excel file
    excel_file = 'instance/Prosth-รายการวัสดุนอกเวลาที่ต้องการสั่งซื้อ.xlsx'
    df = pd.read_excel(excel_file)
    df = df.fillna('')

    if request.method == 'POST':
        # Update the specific row 
        df.at[row_index, 'Unnamed: 1'] = request.form['order']
        df.at[row_index, 'Unnamed: 2'] = request.form['item']
        df.at[row_index, 'Unnamed: 3'] = request.form['unit']
        df.at[row_index, 'Unnamed: 4'] = request.form['stock']
        df.at[row_index, 'Unnamed: 15'] = request.form['quantity']
        df.at[row_index, 'Unnamed: 13'] = request.form['category']  # Update the category field

        # Save the updated data back to Excel
        df.to_excel(excel_file, index=False)
        return redirect(url_for('index'))

    # Pass the specific row data to the template
    row_data = df.iloc[row_index].to_dict()
    return render_template('edit_row.html', row_data=row_data, row_index=row_index)

@app.route('/delete/<int:row_index>', methods=['POST'])
def delete_row(row_index):
    excel_file = 'instance/Prosth-รายการวัสดุนอกเวลาที่ต้องการสั่งซื้อ.xlsx'
    df = pd.read_excel(excel_file)
    df = df.fillna('')

    # Drop the row and reset the DataFrame index
    df = df.drop(index=row_index).reset_index(drop=True)

    # Save the updated DataFrame back to the Excel file
    df.to_excel(excel_file, index=False)

    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_entry():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        excel_file = 'instance/Prosth-รายการวัสดุนอกเวลาที่ต้องการสั่งซื้อ.xlsx'
        df = pd.read_excel(excel_file).fillna('')

        # Add an index column to keep track of the original row index
        df = df.reset_index()

        # Filter the DataFrame for the first match and get it as a dictionary
        filtered_df = df[df['Unnamed: 1'].astype(str) == emp_id]
        employee = filtered_df.iloc[0].to_dict() if not filtered_df.empty else None

        return render_template('search_result.html', employee=employee)

    return redirect(url_for('index'))

from flask_sqlalchemy import SQLAlchemy
import hashlib


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # เปลี่ยนชื่อฐานข้อมูลเป็น users.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # ใช้สำหรับการแสดง flash message
db = SQLAlchemy(app)

# Model for storing user data
class User(db.Model):
    __tablename__ = 'user_db'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = User.query.filter_by(username=username, password=hashed_password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('main'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

# Route for displaying the profile
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('main'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
