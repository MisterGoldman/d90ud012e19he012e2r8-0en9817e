# web_interface.py

class WebInterface:
    def __init__(self, site_generator, site_preview, site_packaging, download_site, user_auth):
        self.site_generator = site_generator
        self.site_preview = site_preview
        self.site_packaging = site_packaging
        self.download_site = download_site
        self.user_auth = user_auth
        self.language = "English"
        self.design = "Desktop"
        self.session = None

    def change_language(self, language):
        # This is a mock implementation, a real one would involve changing interface elements
        self.language = language
        print(f"Interface language changed to {self.language}")

    def toggle_design(self):
        # This is a mock implementation, a real one would involve changing CSS and HTML structure
        self.design = "Mobile" if self.design == "Desktop" else "Desktop"
        print(f"Design changed to {self.design}")


    def register(self, username, password):
        self.user_auth.register(username, password)
        print(f"User {username} registered successfully. Please check your email for a verification link.")

    def login(self, username, password):
        if self.user_auth.login(username, password):
            self.session = username
            print(f"User {username} logged in successfully. Your session ID is {self.session}.")
        else:
            print("Invalid username or password.")

    def logout(self):
        self.session = None
        # TODO: Delete user's cookie or session

    def change_password(self, username, old_password, new_password):
        if self.user_auth.login(username, old_password):
            self.user_auth.change_password(username, new_password)
            print(f"Password changed successfully for user {username}.")
        else:
            print("Invalid username or old password.")

    def generate_site(self, template_name, text, category):
        if self.session is None:
            print("Please log in first.")
            return None
        if not self.user_auth.has_permission(self.session, "generate_site"):
            print("You do not have permission to generate a site.")
            return None
        site = self.site_generator.generate(template_name, text, category)
        preview = self.site_preview.generate_preview(site)
        package = self.site_packaging.package_site(site)
        download_link = self.download_site.download(package)
        print(f"Site generated. You can download it at {download_link}")
        return site, preview, package, download_link


    # TODO: Add method to allow users to delete their account
    # TODO: Add method to allow users to change their password
    # TODO: Add method to allow users to enable or disable two-factor authentication
    # TODO: Add method to handle forgotten passwords
    # TODO: Add method to handle email verification for new accounts
    # TODO: Add method to handle user-reported issues
    # TODO: Add method to handle user requests for data deletion in compliance with GDPR
    # TODO: Add method to handle updating user profile information
    # TODO: Add method to handle user subscription to newsletter or updates
    # TODO: Add method to handle user's consent to cookies or other tracking technologies
    # TODO: Add method to handle user feedback or ratings
    # TODO: Add method to track user activity for analytics
    # TODO: Add method to handle user preferences for interface customization
    # TODO: Add method to handle sharing of site content on social media platforms
    # TODO: Add method to handle user notifications
    # TODO: Add method to handle user requests for technical support
