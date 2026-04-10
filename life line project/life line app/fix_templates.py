from pathlib import Path
base = Path("templates/layout.html")
base.write_text("""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{% block title %}Life Line{% endblock %}</title>
    <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='css/style.css') }}\">
</head>
<body>
    {% block content %}{% endblock %}
    <script src=\"{{ url_for('static', filename='js/script.js') }}\"></script>
</body>
</html>
""", encoding='utf-8')
login = Path("templates/login.html")
login.write_text("""{% extends \"layout.html\" %}
{% block title %}Login | Life Line{% endblock %}
{% block content %}
<div style=\"background: #F0F4F8; min-height: 90vh; display: flex; align-items: center; justify-content: center; padding: 20px;\">
    
    <div class=\"animate__animated animate__fadeInUp\" style=\"display: flex; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 900px; width: 100%;\">
        
        <div style=\"flex: 1; background: url('https://images.pexels.com/photos/4056816/pexels-photo-4056816.jpeg'); background-size: cover; background-position: center; display: none; display: block;\">
            <div style=\"background: rgba(0, 94, 184, 0.4); height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 40px; color: white; box-sizing: border-box;\">
                <div style=\"text-align: center;\">
                    <h3>Welcome Back</h3>
                    <p>Securing your medical data with enterprise-grade encryption.</p>
                </div>
            </div>
        </div>

        <div style=\"flex: 1; padding: 50px; box-sizing: border-box;\">
            <h2 style=\"color: #005EB8; margin-top: 0;\">Login to LifeLine</h2>
            <p style=\"color: #777;\">Access your dashboard and active cases.</p>
            
            <form style=\"margin-top: 30px;\" method=\"GET\" action=\"/login\"> 
                <div style=\"margin-bottom: 20px;\">
                    <label style=\"display: block; color: #444; margin-bottom: 8px;\">Email Address</label>
                    <input type=\"email\" placeholder=\"name@hospital.com\" style=\"width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px;\">
                </div>
                <div style=\"margin-bottom: 25px;\">
                    <label style=\"display: block; color: #444; margin-bottom: 8px;\">Password</label>
                    <input type=\"password\" placeholder=\"••••••••\" style=\"width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px;\">
                </div>
                
                <button type=\"submit\" style=\"width: 100%; background: #005EB8; color: white; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s;\">
                    SIGN IN
                </button>
            </form>
            
            <p style=\"text-align: center; margin-top: 20px; font-size: 0.9rem; color: #888;\">
                Don't have an account? <a href=\"#\" style=\"color: #005EB8; text-decoration: none;\">Contact Administrator</a>
            </p>
        </div>
    </div>
</div>
{% endblock %}
""", encoding='utf-8')
print('updated layout and created login.html')
