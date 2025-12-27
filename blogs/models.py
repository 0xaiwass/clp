from django.db import models
from django_bleach.models import BleachField
from slugify import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from accounts.models import User
from bleach import clean as bleach_clean
from django.utils.html import strip_tags
########################################################
class BlogCategory(models.Model):
    class CategoryType(models.TextChoices):
        TUTORIALS = 'tutorials', 'آموزشی'
        NEWS = 'news', 'اخبار'
        WORKSHOP = 'workshop', 'فعالیت های مجموعه'
        PRODUCT_VIDEOS = 'product_videos', 'معرفی محصولات'
    type = models.CharField(max_length=30, choices=CategoryType.choices, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, allow_unicode=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.type, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_type_display()
########################################################
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, allow_unicode=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
########################################################
class BlogPost(models.Model):
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True, allow_unicode=True)
    content = CKEditor5Field(config_name='default')

    meta_title = models.TextField(blank=True, null=True, max_length=60)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='blogs_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    published = models.BooleanField(default=False)

    excerpt = models.TextField(blank=True)
    reading_time = models.PositiveIntegerField(default=1)


    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['published', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.excerpt:
            text = strip_tags(self.content)
            self.excerpt = text[:160]

        word_count = len(strip_tags(self.content).split())
        self.reading_time = max(1, word_count // 200)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blogs:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
########################################################
class Comment(models.Model):
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = BleachField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)  # moderation

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.phone} on {self.blog}"

    def save(self, *args, **kwargs):
        # Clean content to prevent XSS
        self.content = bleach_clean(self.content, tags=[], attributes={}, strip=True)
        super().save(*args, **kwargs)
########################################################
