from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=32)
    year = models.IntegerField(default=2000)
    director = models.ForeignKey(
        "movies.Director",
        related_name="movies",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title


class Director(models.Model):
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.name} {self.surname}"
