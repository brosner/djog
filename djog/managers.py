
from django.db import models


class EntryManager(models.Manager):
    """
    An Entry Manager class.
    """
    
    def of_type(self, type_):
        """
        Returns a queryset filtering the entries to the given type.
        """
        return self.filter(entry_type=type_)
    
    def in_month(self, month):
        """
        Returns a queryset filtering the entries to the given month.
        """
        return self.filter(pub_date__month=month)
