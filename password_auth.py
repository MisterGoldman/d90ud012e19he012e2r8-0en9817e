# password_auth.py

import os
import bcrypt
import base64
import onetimepass
import logging
import time
import secrets
from getpass import getpass

class PasswordAuth:
    MAX_FAILED_ATTEMPTS = 3
    BLOCK_DURATION = 15 * 60  # 15 minutes

    def __init__(self, password, two_factor_auth=False):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.two_factor_auth = two_factor_auth
        if self.two_factor_auth:
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')
        self.failed_attempts = 0
        self.last_failed_attempt = None

    def authenticate(self, provided_password, otp=None):
        # Check if account is blocked
        if self.failed_attempts >= self.MAX_FAILED_ATTEMPTS:
            if time.time() - self.last_failed_attempt < self.BLOCK_DURATION:
                logging.error("Account is blocked due to too many failed login attempts.")
                return False
            else:
                self.failed_attempts = 0  # reset counter if block duration has passed

        if bcrypt.checkpw(provided_password.encode(), self.password_hash):
            if self.two_factor_auth:
                if otp is None:
                    logging.error("Two-factor authentication is enabled, but OTP is not provided.")
                    return False
                if not onetimepass.valid_totp(otp, self.otp_secret):
                    logging.error("Invalid OTP.")
                    return False
            logging.info("Authentication successful.")
            return True
        else:
            self.failed_attempts += 1
            self.last_failed_attempt = time.time()
            logging.error("Invalid password.")
			return False

	def enable_two_factor_auth(self):
		self.two_factor_auth = True
		self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

	def disable_two_factor_auth(self):
		self.two_factor_auth = False
		self.otp_secret = None

	def change_password(self, new_password):
		self.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

	def reset_password(self):
		new_password = secrets.token_hex(8)
		self.change_password(new_password)
		print(f"New password: {new_password}")
		# TODO: send new password by email

	def change_otp_secret(self):
		self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

	def get_totp_uri(self, name):
		if self.two_factor_auth and self.otp_secret:
			return f"otpauth://totp/{name}?secret={self.otp_secret}"
		else:
			logging.error("Two-factor authentication is not enabled.")
			return None
