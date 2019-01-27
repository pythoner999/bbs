from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
    用戶信息表
    """
    nid = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11, null=True, blank=True, unique=True)
    avatar = models.FileField(upload_to="avatars/", default="avatars/default.png", verbose_name="頭像")
    create_time = models.DateTimeField(auto_now_add=True)

    blog = models.OneToOneField(to="Blog", to_field="nid", null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "用戶"
        verbose_name_plural = verbose_name


class Blog(models.Model):
    """
    博客信息
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)  # 個人博客標題
    site = models.CharField(max_length=32, unique=True)  # 個人博客後綴
    theme = models.CharField(max_length=32, null=True, blank=True)  # 博客主題（css樣式）

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "blog站點"
        verbose_name_plural = verbose_name


class Category(models.Model):
    """
    個人博客文章分類
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)  # 分類標題
    blog = models.ForeignKey(to="Blog", to_field="nid")  # 外鍵關聯博客，一個博客站點可以有多個分類

    def __str__(self):
        return self.title

    class Meta:
        unique_together = (("title", "blog"),)
        verbose_name = "文章分類"
        verbose_name_plural = verbose_name


class Tag(models.Model):
    """
    標籤
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)  # 標籤名
    blog = models.ForeignKey(to="Blog", to_field="nid")  # 所屬博客

    def __str__(self):
        return self.title

    class Meta:
        unique_together = (("title", "blog"),)
        verbose_name = "標籤"
        verbose_name_plural = verbose_name


class Article(models.Model):
    """
    文章
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name="文章標題")
    desc = models.CharField(max_length=255)  # 文章描述
    create_time = models.DateTimeField(auto_now_add=True)  # 創建時間 --> datetime()

    # 評論數
    comment_count = models.IntegerField(verbose_name="評論數", default=0)
    # 點讚數
    up_count = models.IntegerField(verbose_name="點讚數", default=0)
    # 踩
    down_count = models.IntegerField(verbose_name="踩數", default=0)

    category = models.ForeignKey(to="Category", to_field="nid")
    user = models.ForeignKey(to="UserInfo", to_field="nid")
    tags = models.ManyToManyField(  # 中介模型
        to="Tag",
        through="Article2Tag",
        through_fields=("article", "tag"),
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name


class ArticleDetail(models.Model):
    """
    文章詳情表
    """
    nid = models.AutoField(primary_key=True)
    content = models.TextField()
    article = models.OneToOneField(to="Article", to_field="nid")

    class Meta:
        verbose_name = "文章詳情"
        verbose_name_plural = verbose_name


class Article2Tag(models.Model):
    """
    文章和标签的多对多关系表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="nid")
    tag = models.ForeignKey(to="Tag", to_field="nid")

    def __str__(self):
        return "{}-{}".format(self.article.title, self.tag.title)

    class Meta:
        unique_together = (("article", "tag"),)
        verbose_name = "文章-標籤"
        verbose_name_plural = verbose_name


class ArticleUpDown(models.Model):
    """
    點讚表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to="UserInfo", null=True)
    article = models.ForeignKey(to="Article", null=True)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = (("article", "user"),)
        verbose_name = "文章點讚"
        verbose_name_plural = verbose_name


class Comment(models.Model):
    """
    評論表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="nid")
    user = models.ForeignKey(to="UserInfo", to_field="nid")
    content = models.CharField(max_length=255)  # 評論內容
    create_time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey("self", null=True, blank=True)  # blank=True 在django admin裡面可以不填

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "評論"
        verbose_name_plural = verbose_name
