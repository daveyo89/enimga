import smtplib

from src.Config.ConfigHandler import ConfigHandler


class Mailer:
    def __init__(self, message, recipients):
        self.message = message
        self.recipients = recipients

    def send_mail(self):
        ch = ConfigHandler()
        gmail_user, gmail_password = ch.check_existing_config().values()

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, ch.decrypt_message(gmail_password))

            for recipient in self.recipients:
                server.sendmail(from_addr='engima@baba.com', to_addrs=recipient,
                                msg=" ".join(self.message).encode('utf-8'))
            server.close()

            print('Email sent!')
        except Exception as e:
            print(e)
            print('Something went wrong...')
        finally:
            del ch
