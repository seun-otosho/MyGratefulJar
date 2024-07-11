from django.contrib.auth import get_user_model
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from django import forms
from wagtail.admin.panels import FieldPanel
from wagtail.search import index

User = get_user_model()


class Category(index.Indexed, models.Model):
    name = models.CharField(max_length=55, db_index=True, )

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    search_fields = [
        index.SearchField('name', partial_match=True),
        # index.AutocompleteField('name'),
    ]


class BudgetItem(index.Indexed, models.Model):
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(db_index=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_index=True, blank=True, )

    class Meta:
        db_table = 'budgets'
        verbose_name = 'Budget Item'
        unique_together = (('user', 'category', 'date',),)

    def __str__(self):
        return f'Budget for {self.category} - {self.date:%b, %Y} - {self.amount:,}'

    panels = [
        FieldPanel("date"),
        FieldPanel("amount"),
        FieldPanel("category", widget=forms.RadioSelect),
    ]

    search_fields = [
        index.SearchField('amount', partial_match=True),
        # index.AutocompleteField('name'),
    ]


class Income(index.Indexed, models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_index=True, blank=True, )
    date = models.DateField(db_index=True, )
    amount = models.DecimalField(max_digits=10, decimal_places=2, )
    description = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'income'

    def __str__(self):
        return f"{self.date:%b, %Y} - {self.amount:,} - {self.description} - {self.category}"

    panels = [
        FieldPanel("date"),
        FieldPanel("amount"),
        FieldPanel("description"),
        FieldPanel("category", widget=forms.RadioSelect),
    ]

    search_fields = [
        index.SearchField('description'),
        # index.AutocompleteField('category'),
    ]


class ExpenseTag(TaggedItemBase):
    content_object = ParentalKey('Expense', related_name='tagged_expenses', on_delete=models.DO_NOTHING, )


class Expense(ClusterableModel, index.Indexed, models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_index=True, )
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=55, db_index=True, )
    description = models.CharField(max_length=256, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    tags = ClusterTaggableManager(through=ExpenseTag, blank=True)

    panels = [
        FieldPanel("date"),
        FieldPanel("amount"),
        FieldPanel("description"),
        FieldPanel("category", widget=forms.RadioSelect),
        FieldPanel("tags")
    ]

    search_fields = [
        index.SearchField('description'),
        # index.AutocompleteField('category'),
    ]

    class Meta:
        db_table = 'expenses'

    def __str__(self):
        return f'{self.category} of {self.amount:,} on {self.date:%b %d, %Y}'