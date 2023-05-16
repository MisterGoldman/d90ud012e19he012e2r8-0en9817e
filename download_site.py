# download_site.py

class DownloadSite:
    def __init__(self, site_packaging):
        self.site_packaging = site_packaging


    def download(self, template_name, text, category):
        package = self.site_packaging.package_site(template_name, text, category)
        # TODO: Предоставить пользователю ссылку на скачивание
        return package
