from django.db import models

# Create your models here.


class FHWKeyWordsModel(models.Model):
    keyword = models.CharField(verbose_name = '关键字', max_length = 255)
    weight_count = models.IntegerField(verbose_name = '权重')

    class Meta:
        verbose_name = '凤凰网关键字'
        verbose_name_plural = verbose_name


class FHWModel(models.Model):
    title = models.CharField(verbose_name = '标题', max_length = 512)
    content = models.TextField(verbose_name = '内容')
    link = models.URLField(verbose_name = '链接', max_length = 255)
    send_count = models.IntegerField(verbose_name = '转发数')

    class Meta:
        verbose_name = '凤凰网微博'
        verbose_name_plural = verbose_name


class ZhihuKeyWordsModel(models.Model):
    keyword = models.CharField(verbose_name = '关键字', max_length = 255)
    weight_count = models.IntegerField(verbose_name = '权重')

    class Meta:
        verbose_name = '知乎关键字'
        verbose_name_plural = verbose_name


class ZhihuModel(models.Model):
    title = models.CharField(verbose_name = '标题', max_length = 512)
    content = models.TextField(verbose_name = '内容')
    link = models.URLField(verbose_name = '链接', max_length = 255)
    send_count = models.IntegerField(verbose_name = '转发数')

    class Meta:
        verbose_name = '知乎微博'
        verbose_name_plural = verbose_name


class SinapapersKeyWordsModel(models.Model):
    keyword = models.CharField(verbose_name = '关键字', max_length = 255)
    weight_count = models.IntegerField(verbose_name = '权重')

    class Meta:
        verbose_name = '新浪微博关键字'
        verbose_name_plural = verbose_name


class SinapapersModel(models.Model):
    title = models.CharField(verbose_name = '标题', max_length = 512)
    content = models.TextField(verbose_name = '内容')
    link = models.URLField(verbose_name = '链接', max_length = 255)
    send_count = models.IntegerField(verbose_name = '转发数')

    class Meta:
        verbose_name = '新浪微博微博'
        verbose_name_plural = verbose_name


class CCTVxinwenKeyWordsModel(models.Model):
    keyword = models.CharField(verbose_name = '关键字', max_length = 255)
    weight_count = models.IntegerField(verbose_name = '权重')

    class Meta:
        verbose_name = 'CCTV新闻关键字'
        verbose_name_plural = verbose_name


class CCTVxinwenModel(models.Model):
    title = models.CharField(verbose_name = '标题', max_length = 512)
    content = models.TextField(verbose_name = '内容')
    link = models.URLField(verbose_name = '链接', max_length = 255)
    send_count = models.IntegerField(verbose_name = '转发数')

    class Meta:
        verbose_name = 'CCTV新闻微博'
        verbose_name_plural = verbose_name


class FHWFansModel(models.Model):
    nickname = models.CharField(verbose_name = '昵称', max_length = 255)
    location = models.CharField(verbose_name = '地区', max_length = 255)
    sex = models.CharField(verbose_name = '性别', max_length = 255)