from django.contrib.auth import get_user_model
from django.db import models
from wagtail.search import index

User = get_user_model()


class Category(index.Indexed, models.Model):
    name = models.CharField(max_length=100, db_index=True, )

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    search_fields = [
        index.SearchField('name'),
        index.AutocompleteField('name'),
    ]


class Income(index.Indexed, models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_index=True, )
    date = models.DateField(db_index=True, )
    amount = models.DecimalField(max_digits=10, decimal_places=2, )
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'income'

    def __str__(self):
        return f"{self.date} - {self.amount} - {self.description} - {self.category}"

    search_fields = [
        index.SearchField('description'),
        index.AutocompleteField('category'),
    ]


