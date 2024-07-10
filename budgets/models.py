from django.contrib.auth import get_user_model
from django.db import models
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
        unique_together = (('user', 'category', 'date', ),)

    def __str__(self):
        return f'{self.user} - {self.category} - {self.date} - {self.amount}'

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
        return f"{self.date} - {self.amount} - {self.description} - {self.category}"

    panels = [
        FieldPanel("date"),
        FieldPanel("amount"),
        FieldPanel("description"),
        FieldPanel("category"),
    ]

    search_fields = [
        index.SearchField('description'),
        # index.AutocompleteField('category'),
    ]


class Expense(index.Indexed, models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_index=True,)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=55, db_index=True, )
    description = models.CharField(max_length=256, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    panels = [
        FieldPanel("date"),
        FieldPanel("amount"),
        FieldPanel("description"),
        FieldPanel("category"),
    ]

    search_fields = [
        index.SearchField('description'),
        # index.AutocompleteField('category'),
    ]

    class Meta:
        db_table = 'expenses'
