from venv import logger

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from models import db, AliasRecord
from utils.alias_generator import generate_aliases
from io import BytesIO
import pandas as pd
import os
import logging
from flask import jsonify

# ── AutoCure Self-Healing Handler ──
from autocure_handler import attach_autocure
handler = attach_autocure()  # attaches to root logger to catch all errors

if handler:
    print(f"AutoCure handler attached successfully. Logs will be sent to: {handler.ws_url}")
else:
    print("No AutoCure handler attached. Please check your environment variables and dependencies.")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'meowmeow'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aliases.db')
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
            logging.error("Failed to generate aliases: %s", e, exc_info=True)
            flash(str(e), "error")
    return render_template('index.html', aliases=aliases, email=email, count=count)

@app.route('/export/<filetype>')
def export(filetype):
    records = AliasRecord.query.order_by(AliasRecord.created_at).all()
    aliases = [r.alias for r in records if not None]
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


# ── Intentional error routes for AutoCure testing ──
@app.route('/test-error/division')
def test_division_error():
    """Intentional ZeroDivisionError for testing."""
    result = 1 / 0
    return str(result)

@app.route('/test-error/type')
def test_type_error():
    """Intentional TypeError for testing."""
    result = "hello" + str(42)
    return str(result)

@app.route('/test-error/key')
def test_key_error():
    """Intentional KeyError for testing."""
    data = {"name": "test"}
    return data["nonexistent_key"]

@app.route('/test-error/complex')
def test_complex_error():
    """Multi-file call chain: app → validator → formatter (ZeroDivisionError)."""
    from utils.validator import validate_aliases
    # Generate only dot-variant aliases so plus_count=0 → triggers ZeroDivisionError in formatter.py
    aliases = ["test.email@gmail.com", "t.e.s.t@gmail.com", "te.st@gmail.com"]
    result = validate_aliases(aliases, "test@gmail.com")
    return jsonify(result)


@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler — logs to AutoCure."""
    logging.error(
        "Unhandled exception on %s %s: %s",
        request.method, request.path, e,
        exc_info=True,
    )
    return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=5555)