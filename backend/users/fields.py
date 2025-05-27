import base64
import uuid
from rest_framework import serializers
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            # Пример: data:image/png;base64,xxxxxx
            format, imgstr = data.split(';base64,')  # format ~= data:image/png
            ext = format.split('/')[-1]  # png

            img_data = base64.b64decode(imgstr)
            file_name = f'{uuid.uuid4()}.{ext}'
            data = ContentFile(img_data, name=file_name)

        return super().to_internal_value(data)