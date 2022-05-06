def query_params_filter(request, queryset, key_fields, char_fields):
    if len(request.query_params) > 0:
        for p in request.query_params:
            if p in key_fields:
                queryset = queryset.filter(**{'%s__in' % p: request.query_params.getlist(p)})
            elif p in char_fields:
                queryset = queryset.filter(**{'%s__icontains' % p: request.query_params.get(p)})
            elif p.replace("ex_", "") in key_fields:
                queryset = queryset.exclude(**{'%s__in' % p: request.query_params.getlist(p)})
            elif p.replace("ex_", "") in char_fields:
                queryset = queryset.exclude(**{'%s__icontains' % p: request.query_params.get(p)})
    return queryset
