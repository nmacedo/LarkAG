''' Exceptions raised by LarkAG. '''


class AGDefinitionError(Exception):
    ''' The attribute grammar itself is invalid (raised when the AG is loaded). '''


class CircularDependencyError(AGDefinitionError):
    ''' The attribute equations of a rule depend on each other circularly. '''


class ContextConditionError(Exception):
    ''' An input violates a context condition (CC) of the attribute grammar. '''
