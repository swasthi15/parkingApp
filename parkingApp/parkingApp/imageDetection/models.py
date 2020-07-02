from django.db import models

class MapLocation(models.Model):
	location_name = models.CharField(max_length=100, null=False,default=None)
	latitude = models.CharField(max_length=100, null=False,default=None)
	longitude = models.CharField(max_length=100, null=False,default=None)
	total_free = models.IntegerField(null=False,default=0)

	
class Images(models.Model):
	location = models.ForeignKey(MapLocation,on_delete = models.CASCADE)
	image_name = models.CharField(max_length=100, null=False,default=None)
	is_free = models.BooleanField(default=True)





