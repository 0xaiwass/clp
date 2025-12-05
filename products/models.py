from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
#-----------------------------------------------------------
# BASE MODELS ----------------------------------------------
#-----------------------------------------------------------
class Base(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name="نام محصول")
    slug = models.SlugField(max_length=100)
    tags = models.CharField(max_length=50, blank=True, null=True)

    old_price = models.PositiveBigIntegerField(default=0, null=True, blank=True, verbose_name="قیمت اصلی")
    offer_price = models.PositiveBigIntegerField(default=0, verbose_name="قیمت با تخفیف")
    off_percent = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="درصدتخفیف")
    # ✅ Main image
    image = models.ImageField(upload_to="products/images/", blank=True, null=True)
    description = CKEditor5Field(config_name='default', null=True, blank=True, verbose_name="توضیحات")

    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_offer = models.BooleanField(default=False, verbose_name="پیشنهادی")
    is_new = models.BooleanField(default=False,  verbose_name="جدید")
    most_selling = models.BooleanField(default=False,  verbose_name="پرفروش")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    @property
    def extra_images(self):
        content_type = ContentType.objects.get_for_model(self)
        return ProductImage.objects.filter(content_type=content_type, object_id=self.id)

    @property
    def discount_percent(self):
        if self.offer_price and self.old_price and self.old_price > self.offer_price:
            return int(100 - (self.offer_price / self.old_price) * 100)
        return None

    def save(self, *args, **kwargs):
        # 🔹 SlugField Auto Generate
        if not self.slug and self.name:
            self.slug = slugify(self.name)

        # 🔹 Auto calculate discount percent only if field exists in DB
        if hasattr(self, "off_percent"):
            if self.old_price and self.offer_price and self.old_price > self.offer_price:
                self.off_percent = round(((self.old_price - self.offer_price) / self.old_price) * 100)
            else:
                self.off_percent = 0
        super().save(*args, **kwargs)



    @property
    def get_top_features(self, top_n=3):
        """
        Return top_n features as a list of (label, value) tuples
        Only includes fields that are relevant (non-empty, not internal)
        """
        exclude = [
            "id", "slug", "tags", "old_price", "offer_price",
            "off_percent", "image", "description", "is_active",
            "is_offer", "is_new", "created_at"
        ]

        features = []
        for field in self._meta.get_fields():
            if field.name in exclude:
                continue
            if field.is_relation and not field.many_to_one:
                continue

            value = getattr(self, field.name, None)
            if value not in [None, "", 0, False]:
                display = getattr(self, f"get_{field.name}_display", None)
                if callable(display):
                    value = display()
                features.append((field.verbose_name or field.name, value))

        # Return only top_n features
        return features[:top_n]


    @property
    def get_specs(self):
        """
        Return ALL specs (field name + value) dynamically
        Excludes system/internal fields.
        """
        exclude = [
            "id", "slug", "tags", "old_price", "offer_price",
            "off_percent", "image", "description", "is_active",
            "is_offer", "is_new", "created_at"
        ]

        specs = []
        for field in self._meta.fields:  # Only direct model fields
            if field.name in exclude:
                continue

            value = getattr(self, field.name, None)
            if value not in [None, "", 0, False]:
                # If field has choices, show human-readable value
                display = getattr(self, f"get_{field.name}_display", None)
                if callable(display):
                    value = display()
                specs.append((field.verbose_name.title(), value))

        return specs



    @property
    def get_category(self):
        return "base"

    @property
    def model_name(self):
        return self.__class__.__name__.lower()

    @property
    def verbose_name(self):
        return self._meta.verbose_name.title()
#-----------------------------------------------------------
class ProductImage(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')

    image = models.ImageField(upload_to="products/images/alt_img")
    alt_text = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product}"
#-----------------------------------------------------------
class CLP(Base):
    class GuitarSeries(models.TextChoices):
        EX = 'EX', 'EX'
        LS = 'LS', 'LS'
        S = 'S', 'S'
    clp_series = models.CharField(max_length=20, choices=GuitarSeries.choices,
                                  null=True, blank=True,  verbose_name="سری گیتار")

    class BodyMaterial(models.TextChoices):
        PLYWOOD = 'plywood', 'plywood'
        SOLID_WOOD = 'solid_wood', 'solid_wood'
        RESIN_EPOXY = 'resin_epoxy', 'resin_epoxy'
    body_material = models.CharField(max_length=20, choices=BodyMaterial.choices,
                                     null=True, blank=True,  verbose_name="جنس بدنه")

    stick_wood_material = models.CharField(max_length=100, null=True, blank=True, verbose_name="جنس دسته")
    fingerboard_wood_material = models.CharField(max_length=100, null=True, blank=True, verbose_name="جنس فینگربرد")
    frets_quantity = models.PositiveIntegerField(default=0, null=True, blank=True, verbose_name="تعداد فرت‌ها")
    selector_mode = models.CharField(max_length=100, null=True, blank=True, verbose_name="سلکتور")
    bridge = models.CharField(max_length=100, null=True, blank=True, verbose_name="بریج")
    pickup_types = models.CharField(max_length=100, null=True, blank=True, verbose_name="پیکاپ")
    guaranty = models.BooleanField(default=False, null=True, blank=True, verbose_name="گارانتی ۲۴ماهه")

    @property
    def get_category(self):
        return "clp"


    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'CLP'
        verbose_name_plural = 'CLP'
#-----------------------------------------------------------
class AMP(Base):

    type = models.CharField(max_length=100, null=True, blank=True, default='Transistor', verbose_name="نوع امپ")
    watt = models.CharField(max_length=100, null=True, blank=True, verbose_name="وات")
    panel_screw = models.CharField(max_length=100, null=True, blank=True, verbose_name="تعداد پیچ تنظیم")
    channel_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="تعداد کانال‌ها")
    input = models.CharField(max_length=50, null=True, blank=True, verbose_name="ورودی")
    output = models.CharField(max_length=50, null=True, blank=True, verbose_name="خروجی")
    headphone_output = models.BooleanField(default=False, verbose_name="خروجی هدفن")
    guaranty = models.BooleanField(default=False, null=True, blank=True, verbose_name="گارانتی ۲۴ماهه")

    @property
    def get_category(self):
        return "amp"

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'AMP'
        verbose_name_plural = 'AMP'
#-----------------------------------------------------------
class Equipment(Base):
    class EquipmentSeriesChoices(models.TextChoices):

        #Guitar Eq
        BODY = 'body', 'Body'
        BRIDGE = 'bridge', 'Bridge'
        SADDLE = 'saddle', 'Saddle'
        PICKUP = 'pickup', 'Pickup'
        SELECTOR = 'selector', 'Selector'
        POTENTIOMETER = 'potentiometer', 'Potentiometer'
        NUB_VOLUME = 'nub_volume', 'Nub Volume'
        OUTPUT_JACK = 'output_jack', 'Output_Jack'
        NECK = 'neck', 'Neck'
        FRET = 'fret', 'Fret'
        FINGERBOARD = 'fingerboard', 'Fingerboard'
        TUNING_PEGS = 'tuning_pegs', 'Tuning Pegs'
        NECK_SCREW = 'neck_screw', 'Neck_Screw'
        TRUSS_ROD = 'truss_rod', 'Truss Rod'
        #Others
        STRAP = 'strap', 'Strap'
        PIN_STRAP = 'pin_strap', 'pin_strap'
        PICK = 'pick', 'Pick'
        STAND = 'stand', 'Stand'
        CLEANER = 'cleaner', 'Cleaner'
        METRONOME = 'metronome', 'Metronome'
        CABLE = 'cable', 'Cable'
        CAPO = 'capo', 'Capo'
        NUT = 'nut', 'Nut'
    equipment_series = models.CharField(max_length=40, choices=EquipmentSeriesChoices.choices,
                                        verbose_name="سری لوازم‌جانبی")

    class NeckChoices(models.TextChoices):
        FRETLESS = 'fretless', 'Fretless'
        FRETTED = 'fretted', 'Fretted'
    neck_type = models.CharField(max_length=30, choices=NeckChoices.choices,
                                 null=True, blank=True, default=None, verbose_name="نوع دسته")

    class Fret(models.TextChoices):
        CUTTED = 'cutted', 'Cutted'
        METRIC = 'metric', 'Metric'
    fret_type = models.CharField(max_length=20, choices=Fret.choices,
                                 null=True, blank=True, verbose_name="نوع فرت")

    brand = models.CharField(max_length=40, null=True, blank=True, verbose_name="برند")

    @property
    def get_category(self):
        return "equipment"

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'
#-----------------------------------------------------------
class GuitarStrings(Base):
    class GuitarStringsChoices(models.TextChoices):
        CLASSIC = 'classic', 'Classic'
        ACOUSTIC = 'acoustic', 'Acoustic'
        ELECTRIC = 'electric', 'Electric'
    string_type = models.CharField(max_length=30, choices=GuitarStringsChoices.choices, verbose_name="نوع ساز")

    class StringTensionChoices(models.TextChoices):
        HARD = 'hard', 'Hard'
        NORMAL = 'normal', 'Normal'
        SOFT = 'soft', 'Soft'
        TENSION_10_47 = '10-47', '10-47'
        TENSION_11_52 = '11-52', '11-52'
        TENSION_12_54 = '12-54', '12-54'
        TENSION_10_46 = '10-46', '10-46'
        TENSION_9_42 = '9-42', '9-42'

    tension = models.CharField(max_length=30, null=True, blank=True,
                               choices=StringTensionChoices.choices, verbose_name="سایز سیم")

    brand = models.CharField(max_length=30, null=True, blank=True, verbose_name="برند")

    @property
    def get_category(self):
        return "guitarstrings"


    class Meta:
        ordering = ('-created_at', 'tension')
        verbose_name = 'GuitarStrings'
        verbose_name_plural = 'GuitarStrings'
#-----------------------------------------------------------
# class Comment(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     product = GenericForeignKey('content_type', 'object_id')
#
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         ordering = ("-created_at",)
#
#     def __str__(self):
#         return f"Comment by {self.user} on {self.product}"