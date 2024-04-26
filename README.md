# Full word filter backend for django REST framework

In your ``settings.py``

    INSTALLED_APPS += ('rest_framework_word_filter', )

Compatible with python 3.6+, django 3.0+

## Using

Import

    from rest_framework_word_filter import FullWordSearchFilter
    ....
    
and add to filter backends. Add attribute ``word_fields`` to define which fields in model will be used for search.

    class FooListView(ListAPIView):
        model = Foo
        queryset = Foo.objects.all()
        serializer_class = FooSerializer
        filter_backends = (FullWordSearchFilter, )
        word_fields = ('text',)

Fill free to send issues or pull requests =)

