# site_generator.py

from jinja2 import Environment, FileSystemLoader
from text_uniqizer import TextUniqizer
from template_uniqizer import TemplateUniqizer
import urllib.parse
import os

class SiteGenerator:
    def __init__(self, template_handler, text_uniqizer, meta_handler, style_handler, style_uniqizer, template_uniqizer):
        self.template_handler = template_handler
        self.text_uniqizer = text_uniqizer
        self.style_handler = style_handler
        self.template_uniqizer = template_uniqizer
        self.user_settings = {}
        self.template_choices = []
        self.style_choices = []

    def add_template_choice(self, template_name):
        self.template_choices.append(template_name)

    def remove_template_choice(self, template_name):
        if template_name in self.template_choices:
            self.template_choices.remove(template_name)

    def add_style_choice(self, style_name):
        self.style_choices.append(style_name)

    def remove_style_choice(self, style_name):
        if style_name in self.style_choices:
            self.style_choices.remove(style_name)

    def generate_styles(self, category):
        styles = ""
        if category == "business":
            styles = """
                body { font-family: Arial, sans-serif; color: #333; }
                h1 { color: #1a1a1a; }
                h2, h3 { color: #666; }
            """
        elif category == "art":
            styles = """
                body { font-family: 'Times New Roman', serif; color: #212121; }
                h1 { color: #515151; }
                h2, h3 { color: #7a7a7a; }
            """
        return styles

    def generate_site(self, category, template_name, text, images, videos):
        uniqized_text = self.text_uniqizer.uniqize(text, category)
        unique_styles = self.generate_styles(category)
        template, unique_styles = self.template_uniqizer.uniqize(category, template_name, unique_styles)
        image_html = [self.generate_image_html(url) for url in images]
        video_html = [self.generate_video_html(url) for url in videos]
        meta_tags = self.meta_handler.generate_meta_tags(category, uniqized_text)

        site = template.render(
            text=uniqized_text, 
            styles=unique_styles, 
            images=image_html, 
            videos=video_html, 
            meta_tags=meta_tags
        )
        return site

    def generate(self, template_name, text, category, algorithm='default', images=[], videos=[]):
        if algorithm == 'default':
            template = self.template_handler.load_template(template_name)
            uniq_text = self.text_uniqizer.uniqize(text, category)
        elif algorithm == 'random_template':
            template = self.template_handler.load_random_template(category)
            uniq_text = self.text_uniqizer.uniqize(text, category)
        else:
            raise ValueError(f"Unknown generation algorithm: {algorithm}")

        return self.generate_site(category, template_name, uniq_text, images, videos)

    def generate_image_html(self, image_url):
        if not image_url or not self.is_valid_url(image_url):
            return ""
        return f'<img src="{image_url}" alt="User uploaded image">'

    def is_valid_url(self, url):
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def generate_video_html(self, video_url, video_type='mp4'):
        if not video_url or not self.is_valid_url(video_url):
            return ""
        video_type = 'mp4' if video_type not in ['mp4', 'ogg', 'webm'] else video_type
        mime_type = f"video/{video_type}"
        return f'<video controls><source src="{video_url}" type="{mime_type}">Your browser does not support the video tag.</video>'

    def add_template(self, template_name, template_content):
        with open(f'templates/{template_name}.html', 'w') as file:
            file.write(template_content)

    def remove_template(self, template_name):
        try:
            os.remove(f'templates/{template_name}.html')
        except FileNotFoundError:
            print(f"Template '{template_name}' not found.")

    def add_style(self, style_name, style_content):
        with open(f'styles/{style_name}.css', 'w') as file:
            file.write(style_content)

    def remove_style(self, style_name):
        try:
            os.remove(f'styles/{style_name}.css')
        except FileNotFoundError:
            print(f"Style '{style_name}' not found.")

    def set_user_settings(self, settings):
        self.user_settings.update(settings)

    def get_user_settings(self):
        return self.user_settings
