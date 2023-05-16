# site_packaging.py

import zipfile
import os
import shutil

class SitePackaging:
    def __init__(self, site_generator, archive_format="zip"):
        self.site_generator = site_generator
        self.archive_format = archive_format

    def package_site(self, template_name, text, category):
        site = self.site_generator.generate(template_name, text, category)
        archive_name = 'site.' + self.archive_format
        if self.archive_format == 'zip':
            with zipfile.ZipFile(archive_name, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(site):
                    for file in files:
                        zipf.write(os.path.join(root, file))
        elif self.archive_format == 'tar':
            shutil.make_archive('site', 'tar', site)
        else:
            raise ValueError(f"Unsupported archive format: {self.archive_format}")
        shutil.rmtree(site)  # Remove the site files
        return archive_name
