from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w_0-odpl+sd4=vc$xyxah#pnb=df+(rb@a+4#$c4p+x&#a-tal'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["clpguitar.com","www.clpguitar.com",'141.11.250.14']

# Session config: 1-hour idle timeout, secure cookies
SESSION_COOKIE_AGE = 3600  # 1 hour max (from last activity)
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Don't expire on close (idle check handles it)
SESSION_SAVE_EVERY_REQUEST = True  # Reset timer on every page visit (if authenticated)
SESSION_COOKIE_SECURE = True  # HTTPS only (your Nginx has SSL)
SESSION_COOKIE_HTTPONLY = True  # Prevent JS access (anti-XSS)
SESSION_COOKIE_SAMESITE = 'Lax'  # Secure cross-site
# Backend: DB (your default; fast for <10k users)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    ###############################
    ###############################
    'home.apps.HomeConfig',
    'accounts.apps.AccountsConfig',
    'blogs.apps.BlogsConfig',
    'products.apps.ProductsConfig',
    'carts.apps.CartsConfig',
    'orders.apps.OrdersConfig',
    ###############################
    'django_ckeditor_5',
    'django.contrib.sitemaps',
    'django_bleach',
    'django.contrib.humanize',
    'compressor',
    ###############################
    ###############################
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'clp.middleware.SessionTimeoutMiddleware',
    'clp.middleware.AdminAccessMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'clp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'clp.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'clp_db',
        'USER': 'sephiroth',
        'PASSWORD': 'Fscty7536!@#',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
################################################################
########################CUSTOM SETTINGS#########################
STATIC_URL = '/static/'

# Ignore duplicates in collectstatic
STATICFILES_IGNORE_PATTERNS = [
    'django_ckeditor_5/dist/translations/*.js',  # Targets the duplicates
    'django_ckeditor_5/src/*.js',  # If needed
]


STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]
COMPRESS_ENABLED = False

STATICFILES_DIRS = [
    BASE_DIR / "static",  # adjust this if your static folder is elsewhere
]

STATIC_ROOT = BASE_DIR / "staticfiles"

AUTH_USER_MODEL = 'accounts.User'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
########################CK EDITOR SETTINGS#########################

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'png', 'jpg']

CKEDITOR_5_CONFIGS = {

    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'link',
            'bulletedList', 'numberedList', '|',
            'blockQuote', 'codeBlock', '|',
            'insertTable', 'insertImage', 'mediaEmbed', '|',
            'undo', 'redo', 'sourceEditing', 'alignment', 'direction',
        ],
        'language': 'fa',
        'image': {
            'toolbar': [
                'imageTextAlternative', 'imageStyle:alignLeft',
                'imageStyle:alignRight', 'imageStyle:alignCenter',
                'imageStyle:alignBlockLeft', 'imageStyle:alignBlockRight',
            ]
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties',
            ]
        },
        'mediaEmbed': {
            'previewsInData': True,
        },
    }
}
#########################BLEACH#################################
# Allowed HTML tags
BLEACH_ALLOWED_TAGS = [
    "b", "i", "u", "em", "strong", "a"
]

# Allowed attributes for tags
BLEACH_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"]
}

# Allowed URL protocols
BLEACH_ALLOWED_PROTOCOLS = ["http", "https"]

# Remove any disallowed tags completely
BLEACH_STRIP_TAGS = True
################################################################
