import smtplib
from dotenv import load_dotenv
import os
from email.message import EmailMessage
load_dotenv()
from app.models import db, Subscriber
from sync_rss import sync_warnings_to_db
from flask import Flask

def send_emails(new_records_count, subscribers_list):
    """
    Function send e-mail notifications to subscribers    
    """

    if not subscribers_list:
        print("No subscribers!")
        return
    
    msg = EmailMessage() 
    msg["Subject"] = f"Nowe ostrzeżenia GIS! ({new_records_count} nowych)"
    msg["From"] = os.getenv('EMAIL')
    msg["To"] = os.getenv('EMAIL') 
    msg["Bcc"] = ", ".join(subscribers_list)

    #Text version if html doesnt work
    msg.set_content(f"Witaj!\n\nW systemie pojawiło się {new_records_count} nowych ostrzeżeń dotyczących żywności.\nSprawdź szczegóły w aplikacji.")
    #HTML version
    msg.add_alternative(f"""\
    <html>
      <body>
        <h2 style="color: #dc3545;">Uwaga! Nowe ostrzeżenia GIS</h2>
        <p>W systemie EatSafe zarejestrowaliśmy <strong>{new_records_count}</strong> nowych ostrzeżeń dotyczących żywności.</p>
        <p><a href="linkt_do_aplikacji_eatsafe">Kliknij tutaj, aby sprawdzić szczegóły</a></p>
        <hr>
        <small style="color: #6c757d;">Otrzymujesz tę wiadomość, ponieważ jesteś zapisany do bazy subskrybentów.</small>
      </body>
    </html>
    """, subtype='html')

    try:
        smtp_server = "smtp.gmail.com"
        port = 587
        with smtplib.SMTP(smtp_server, port) as s:
            s.starttls()
            s.login(os.getenv('EMAIL'), os.getenv('EMAIL_PASSWORD'))
            s.send_message(msg)
        print(f"Successfully sends email to {len(subscribers_list)} subscribers.")
    except Exception as e:
        print(f"Error while sending email: {e}")



def run_sync_rss_and_notify():
    #synchronizing
    new_warnings_count = sync_warnings_to_db()

    if new_warnings_count > 0:
        subscribers = [sub.email for sub in Subscriber.query.filter_by(is_active=1).all()]
        send_emails(new_warnings_count, subscribers)
    


if __name__ == "__main__":
    load_dotenv()
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    with app.app_context():
        run_sync_rss_and_notify()