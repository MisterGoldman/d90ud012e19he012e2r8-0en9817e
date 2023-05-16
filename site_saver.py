#site_saver.py

import os
import tarfile
import zipfile
import logging
import requests
from urllib.parse import urlparse, urljoin
from datetime import datetime
import shutil
from bs4 import BeautifulSoup
import concurrent.futures
from PIL import Image
import glob
from selenium import webdriver


class SiteSaver:
    SUPPORTED_EXTENSIONS = ['html', 'css', 'js', 'jpg', 'jpeg', 'png', 'gif']

    def __init__(self, format='zip'):
        self.sites_dir = "sites"
        self.format = format
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        if not os.path.exists(self.sites_dir):
            os.makedirs(self.sites_dir)
        logging.basicConfig(level=logging.INFO)

    def _get_file_name(self, url):
        parsed_url = urlparse(url)
        file_name = f"{parsed_url.netloc}{parsed_url.path.replace('/', '_')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return file_name

    def _get_site_meta_info(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title"
            meta_info = f"URL: {url}\nTitle: {title}\nSaved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            return meta_info
        except Exception as e:
            logging.warning(f"Could not get meta info from {url}. Reason: {e}")
            return None

    def _is_site_available(self, url):
        try:
            response = requests.get(url)
            return response.status_code == 200
        except Exception as e:
            logging.warning(f"Site {url} is not available. Reason: {e}")
            return False

    def _save_file(self, file_path, site_dir):
        try:
            if file_path.split('.')[-1] in self.SUPPORTED_EXTENSIONS:
                with open(file_path, 'rb') as file:
                    if self.format == 'zip':
                        with zipfile.ZipFile(site_dir + '.zip', 'a') as zipf:
                            zipf.writestr(file_path, file.read())
                    elif self.format == 'tar':
                        with tarfile.open(site_dir + '.tar.gz', 'a:gz') as tarf:
                            tarf.addfile(tarfile.TarInfo(file_path), file)
        except Exception as e:
            logging.warning(f"Could not save file {file_path}. Reason: {e}")

    def _save_directory(self, directory_path, site_dir):
        for foldername, subfolders, filenames in os.walk(directory_path):
            for filename in filenames:
                self._save_file(os.path.join(foldername, filename), site_dir)

    def save(self, url):
        if not self._is_site_available(url):
            logging.error(f"Site {url} is not
        if not self._is_site_available(url):
            logging.error(f"Site {url} is not available. Skipping...")
            return

        site_dir = os.path.join(self.sites_dir, self._get_file_name(url))
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)

        meta_info = self._get_site_meta_info(url)
        if meta_info:
            with open(os.path.join(site_dir, 'meta_info.txt'), 'w') as meta_info_file:
                meta_info_file.write(meta_info)

        self.save_site(url, site_dir)

        if self.format == 'zip':
            shutil.make_archive(site_dir, 'zip', site_dir)
        elif self.format == 'tar':
            shutil.make_archive(site_dir, 'gztar', site_dir)

        shutil.rmtree(site_dir)

        logging.info(f"Site {url} saved successfully to {site_dir + '.' + ('zip' if self.format == 'zip' else 'tar.gz')}")
        return site_dir + '.' + ('zip' if self.format == 'zip' else 'tar.gz')

    def save_file(self, url, path):
        response = requests.get(url)
        with open(path, 'wb') as f:
            f.write(response.content)

    def unique_image(self, image_path):
        try:
            with Image.open(image_path) as img:
                img = img.resize((img.width // 2, img.height // 2))
                img.save(image_path)
        except Exception as e:
            logging.warning(f"Could not unique image {image_path}. Reason: {e}")

    def save_site(self, site_url, category):
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        site_dir = os.path.join(self.sites_dir, category, urlparse(site_url).netloc)
        if not os.path.exists(site_dir):
            os.makedirs(site_dir)
        futures = []
        for link in soup.find_all(['a', 'img']):
            url = urljoin(site_url, link.get('href' if link.name == 'a' else 'src'))
            if not url.startswith(site_url):
                continue
            path = os.path.join(site_dir, urlparse(url).path.lstrip('/'))
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            if link.name == 'img':
                future = self.executor.submit(self.save_file, url, path)
                future.add_done_callback(lambda x: self.unique_image(path))
                futures.append(future)
            else:
                futures.append(self.executor.submit(self.save_file, url, path))

        concurrent.futures.wait(futures)

    def list_saved_sites(self):
        return glob.glob(f"{self.sites_dir}/*")

        futures = []
        for link in soup.find_all(['a', 'img']):
            url = urljoin(site_url, link.get('href' if link.name == 'a' else 'src'))
            if not url.startswith(site_url):
                continue
            path = os.path.join(site_dir, urlparse(url).path.lstrip('/'))
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            if link.name == 'img':
                future = self.executor.submit(self.save_file, url, path)
                future.add_done_callback(lambda x: self.unique_image(path))
                futures.append(future)
            else:
                futures.append(self.executor.submit(self.save_file, url, path))

        concurrent.futures.wait(futures)

    def list_saved_sites(self):
        return glob.glob(f"{self.sites_dir}/*")
            screenshot_file = os.path.join(self.sites_dir, self._get_file_name(url) + '.png')
            driver.save_screenshot(screenshot_file)
            driver.quit()
            return screenshot_file
        except Exception as e:
            logging.warning(f"Could not save screenshot of {url}. Reason: {e}")
            return None

    def close(self):
        self.executor.shutdown()


# TODO: 1. Добавить поддержку облачного хранилища (AWS S3, Google Cloud Storage).
# TODO: 2. Добавить поддержку других форматов архивации (rar, 7z и т.д.).
# TODO: 4. Добавить поддержку сжатия файлов перед сохранением.
# TODO: 5. Добавить поддержку сохранения метаинформации о сайте (автор, дата создания, описание).
# TODO: 6. Реализовать поддержку создания уникальных имен для сайтов.
# TODO: 8. Добавить поддержку сохранения вложенных страниц сайта.
# TODO: 9. Добавить поддержку автоматического обновления сохраненного сайта.
# TODO: 10. Добавить поддержку сохранения сайта с авторизацией.
# TODO: 11. Добавить поддержку 
# TODO: 12. Добавить поддержку настроек для выбора типов файлов для сохранения.
# TODO: 13. Добавить поддержку сохранения сайтов с динамическим контентом (JavaScript).
# TODO: 16. Добавить поддержку сохранения сайтов с использованием headless браузера.
# TODO: 19. Добавить функционал для восстановления сайта из сохраненной копии.
# TODO: 20. Добавить поддержку сохранения сайта в различных масштабах (мобильный, планшет, десктоп).
