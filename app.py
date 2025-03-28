from flask import Flask, render_template, request, redirect, url_for, make_response, Response
from fpdf import FPDF
import os
app = Flask(__name__)

# All scenarios and choices
scenarios = [
    {
        "text": "Heavy rain forecasted, flood warnings issued.",
        "choices": [
            "Issue an early warning to the public.",
            "Wait for confirmation before issuing any warning.",
            "Deploy evacuation teams immediately."
        ]
    },
    {
        "text": "Floodwaters are rising, roads are blocked.",
        "choices": [
            "Open emergency shelters and dispatch rescue boats.",
            "Instruct residents to stay home and await further instructions.",
            "Ignore the situation and wait for the flood to subside."
        ]
    },
    {
        "text": "Nearby dam at risk of overflowing.",
        "choices": [
            "Release controlled amounts of water from the dam.",
            "Evacuate communities downstream.",
            "Ignore the warnings and hope for the best."
        ]
    },
    {
        "text": "Flooded areas lack power, supplies are running low.",
        "choices": [
            "Send relief supplies via helicopters.",
            "Prioritize restoring power before sending supplies.",
            "Wait for water levels to subside naturally."
        ]
    },
    {
        "text": "Rumors spread about a second wave of flooding.",
        "choices": [
            "Verify reports and keep the public informed.",
            "Ignore the rumors to avoid panic.",
            "Enforce strict curfews and lockdowns."
        ]
    }
]

# Outcomes based on choices
outcomes = [
    {"score": 20, "message": "Excellent choice! You prevented major damage."},
    {"score": -10, "message": "Delayed action caused unnecessary damage."},
    {"score": 15, "message": "Good job! Damage was minimized."}
]

# Homepage
@app.route('/')
def home():
    response = make_response(render_template('index.html'))
    response.set_cookie('score', '0')  # Reset score on start
    return response

# Gameplay
@app.route('/play/<int:index>')
def play(index):
    if index >= len(scenarios):
        return redirect(url_for('summary'))

    scenario = scenarios[index]
    return render_template('game.html', scenario=scenario, index=index)

# Display result
@app.route('/result', methods=['POST'])
def result():
    choice = int(request.form['choice'])
    index = int(request.form['index'])
    scenario = scenarios[index]
    result = outcomes[choice - 1]

    # Track score using cookies
    if 'score' not in request.cookies:
        total_score = 0
    else:
        total_score = int(request.cookies.get('score'))

    total_score += result['score']

    # Ensure score is saved in cookies
    response = make_response(render_template('result.html', scenario=scenario, result=result, score=total_score, index=index, scenarios=scenarios))
    response.set_cookie('score', str(total_score))
    return response

@app.route('/summary')
def summary():
    total_score = int(request.cookies.get('score', 0))
    if total_score > 70:
        message = "🏆 Excellent! You managed the crisis efficiently!"
    elif total_score > 30:
        message = "👍 Good work! Some areas could be improved."
    else:
        message = "⚠️ Poor response! Lives were lost and damage was severe."
    
    response = make_response(render_template('summary.html', score=total_score, message=message))
    response.set_cookie('score', '0')  # Reset score for next playthrough
    return response

# Generate PDF
@app.route('/download-pdf')
def download_pdf():
    score = request.args.get('score', '0')
    message = request.args.get('message', 'No message available.')

    # Create PDF instance
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    # Add PDF content
    pdf.cell(200, 10, txt="Game Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Your Final Score: {score}", ln=True)
    pdf.multi_cell(0, 10, txt=f"Message: {message}")

    # Return PDF response
    response = Response(pdf.output(dest='S').encode('latin1'))  # Encoding for FPDF compatibility
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=game_summary.pdf'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT if available, else 5000
    app.run(host='0.0.0.0', port=port, debug=True)
