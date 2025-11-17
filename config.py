import os


class AppConfig:
    """Centralized configuration for the PDF compressor app."""

    APP_NAME = "📄 PDF Compressor"
    APP_SUBTITLE = "Reduce your PDF file size with ease"

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/pdf_uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload

    DEFAULT_OUTPUT_PATH = os.environ.get(
        'DEFAULT_OUTPUT_PATH',
        os.path.expanduser('~/Downloads')
    )
    DEFAULT_QUALITY = 'printer'
    QUALITY_RECOMMENDATION_LABEL = 'Printer quality'
    QUALITY_OPTIONS = [
        {'value': 'screen', 'label': 'Screen (Smallest, 72 DPI)'},
        {'value': 'ebook', 'label': 'eBook (Medium, 150 DPI)'},
        {'value': 'printer', 'label': 'Printer (High Quality, 300 DPI)'},
        {'value': 'prepress', 'label': 'Prepress (Maximum Quality, 300 DPI)'},
    ]
    QUALITY_HINT_TEMPLATE = (
        "<strong>{recommendation}</strong> is recommended for files under 20MB "
        "when you want excellent quality with a smaller footprint."
    )
