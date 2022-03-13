class AbstractQuery(object):
    invert = False

    def generate(self, field_name, value):
        raise NotImplementedError


class EqualsQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return {
                   "match": {
                       field_name: value
                   }
               }, self.invert


class NotEqualsQuery(AbstractQuery):
    invert = True

    def generate(self, field_name, value):
        return {
                   "match": {
                       field_name: value
                   }
               }, self.invert


class GtQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return {
                   "range": {
                       field_name: {
                           "gt": value
                       }
                   }
               }, self.invert


class GteQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return {
                   "range": {
                       field_name: {
                           "gte": value
                       }
                   }
               }, self.invert


class LtQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return {
                   "range": {
                       field_name: {
                           "lt": value
                       }
                   }
               }, self.invert


class LteQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return {
                   "range": {
                       field_name: {
                           "lte": value
                       }
                   }
               }, self.invert


class ContainsQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return {
                   "wildcard": {
                       field_name: {
                           "value": "*" + value + "*"
                       }
                   }
               }, self.invert


class NotContainsQuery(AbstractQuery):
    invert = True

    def generate(self, field_name, value):
        return {
                   "wildcard": {
                       field_name: {
                           "value": "*" + value + "*"
                       }
                   }
               }, self.invert


class InQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return [{"match_phrase": {field_name, phrase}} for phrase in value], self.invert


class NotInQuery(AbstractQuery):
    invert = True

    def generate(self, field_name, value):
        return [{"match_phrase": {field_name, phrase}} for phrase in value], self.invert


class StartsWithQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return {
                   "prefix": {
                       field_name: {
                           "value": value
                       }
                   }
               }, self.invert


class EndsWithQuery(AbstractQuery):
    invert = False

    def generate(self, field_name, value):
        return {
                   "wildcard": {
                       field_name: {
                           "value": "*" + value
                       }
                   }
               }, self.invert


class NotStartsWithQuery(AbstractQuery):
    invert = True

    def generate(self, field_name, value):
        return {
                   "prefix": {
                       field_name: {
                           "value": value
                       }
                   }
               }, self.invert


class NotEndsWithQuery(AbstractQuery):
    invert = True

    def generate(self, field_name, value):
        return {
                   "wildcard": {
                       field_name: {
                           "value": "*" + value
                       }
                   }
               }, self.invert


class QueryBuilderFactory(object):
    operator_class_mapping = {'=': EqualsQuery,
                              '>': GtQuery,
                              '>=': GteQuery,
                              '<': LtQuery,
                              '<=': LteQuery,
                              '~': ContainsQuery,
                              'in': InQuery,
                              'startswith': StartsWithQuery,
                              'endswith': EndsWithQuery,
                              '!=': NotEqualsQuery,
                              '!~': NotContainsQuery,
                              'not in': NotInQuery,
                              'not startswith': NotStartsWithQuery,
                              'not endswith': NotEndsWithQuery,
                              }

    def get_query_builder(self, operator):
        query_generator_cls = self.operator_class_mapping.get(operator)
        return query_generator_cls()
