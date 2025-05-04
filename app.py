from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from models import db, AliasRecord
from utils.alias_generator import generate_aliases
from io import BytesIO
import pandas as pd
import os
from flask import jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aliases.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    AliasRecord.query.delete()
    db.session.commit()
    aliases = []
    email = ''
    count = 10
    if request.method == 'POST':
        email = request.form['email']
        count = int(request.form['count'])
        if count < 1 or count > 5000:
            flash("Please enter a number between 1 and 5000.", "error")
            return render_template('index.html', aliases=[], email=email, count=count)
        try:
            aliases = generate_aliases(email, count)
            # Store in DB
            for alias in aliases:
                record = AliasRecord(base_email=email, alias=alias)
                db.session.add(record)
            db.session.commit()
        except Exception as e:
            flash(str(e), "error")
    return render_template('index.html', aliases=aliases, email=email, count=count)

@app.route('/export/<filetype>')
def export(filetype):
    records = AliasRecord.query.order_by(AliasRecord.created_at).all()
    aliases = [r.alias for r in records]
    if not aliases:
        return "No aliases to export. Please generate some first.", 400

    if filetype == 'txt':
        buffer = BytesIO()
        buffer.write('\n'.join(aliases).encode('utf-8'))
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='aliases.txt', mimetype='text/plain')
    elif filetype == 'xlsx':
        output = BytesIO()
        df = pd.DataFrame({'Alias': aliases})
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='aliases.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        return "Invalid file type", 400

@app.route('/clear', methods=['POST'])
def clear():
    AliasRecord.query.delete()
    db.session.commit()
    flash("All aliases deleted.", "info")
    return redirect(url_for('home'))


@app.route('/clear_on_exit', methods=['POST'])
def clear_on_exit():
    AliasRecord.query.delete()
    db.session.commit()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)