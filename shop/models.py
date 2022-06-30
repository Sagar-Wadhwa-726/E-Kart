from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    desc = models.CharField(max_length=30000)
    pub_date = models.DateField()
    category = models.CharField(max_length=50, default="")
    sub_category = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to="shop/images", default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=70, default="")
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    cust_query = models.TextField(max_length=170, default="")

    def __str__(self):
        return self.name


class orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField(default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=90)
    address = models.CharField(max_length=90)
    address2 = models.CharField(max_length=90)
    city = models.CharField(max_length=90)
    state = models.CharField(max_length=90)
    zip_code = models.CharField(max_length=90)
    phone = models.IntegerField()

    class Meta:
        verbose_name_plural = "Orders"

    def __str__(self):
        return self.name


class orderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[0:17] + "..."


# Creating a model named profile which is the extension of the User Model
# Extending the User Model, by using OnetoOneRelationship, user model binded to the Profile model through foreign Key

# on_delete=models.CASCADE --> if a particular user db entry deleted, then delete the Profile db also for that user
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username
